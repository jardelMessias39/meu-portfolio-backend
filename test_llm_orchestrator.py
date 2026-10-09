import pytest
import os
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock
from llm_orchestrator import LLMOrchestrator
from llm_provider import LLMErrorType, LLMProviderError, LLMResponse
from models import ChatMessage
from fastapi import HTTPException
import httpx

@pytest.fixture
def mock_gemini():
    gemini = MagicMock()
    gemini.model = "gemini-test"
    gemini.generate_response = AsyncMock()
    return gemini

@pytest.fixture
def mock_openai():
    openai = MagicMock()
    openai.model = "gpt-test"
    openai.generate_response = AsyncMock()
    return openai

@pytest.fixture
def orchestrator(mock_gemini, mock_openai):
    with patch('llm_orchestrator.get_llm_provider') as get_prov:
        def side_effect(name):
            if name == "gemini": return mock_gemini
            if name == "openai": return mock_openai
            raise ValueError("Invalido")
            
        get_prov.side_effect = side_effect
        os.environ["LLM_PROVIDER"] = "gemini"
        os.environ["LLM_FALLBACK_PROVIDER"] = "openai"
        return LLMOrchestrator()

# TESTE 1: Gemini sucesso -> OpenAI nao e chamado
def test_1_gemini_success(orchestrator, mock_gemini, mock_openai):
    async def run():
        mock_gemini.generate_response.return_value = LLMResponse(content="Success", tool_calls=None)
        res = await orchestrator.generate_response("sys", [], [])
        assert res.content == "Success"
        mock_gemini.generate_response.assert_called_once()
        mock_openai.generate_response.assert_not_called()
    asyncio.run(run())

# TESTE 2: Gemini 503 -> OpenAI e chamado
def test_2_gemini_503_fallback(orchestrator, mock_gemini, mock_openai):
    async def run():
        mock_gemini.generate_response.side_effect = LLMProviderError(LLMErrorType.PROVIDER_UNAVAILABLE, 503, "503")
        mock_openai.generate_response.return_value = LLMResponse(content="Fallback Success", tool_calls=None)
        res = await orchestrator.generate_response("sys", [], [])
        assert res.content == "Fallback Success"
        mock_gemini.generate_response.assert_called_once()
        mock_openai.generate_response.assert_called_once()
    asyncio.run(run())

# TESTE 3: Gemini 429 -> OpenAI e chamado
def test_3_gemini_429_fallback(orchestrator, mock_gemini, mock_openai):
    async def run():
        mock_gemini.generate_response.side_effect = LLMProviderError(LLMErrorType.RATE_LIMITED, 429, "429")
        mock_openai.generate_response.return_value = LLMResponse(content="Fallback OK", tool_calls=None)
        res = await orchestrator.generate_response("sys", [], [])
        assert res.content == "Fallback OK"
        mock_openai.generate_response.assert_called_once()
    asyncio.run(run())

# TESTE 4: Gemini timeout -> OpenAI e chamado
def test_4_gemini_timeout_fallback(orchestrator, mock_gemini, mock_openai):
    async def run():
        mock_gemini.generate_response.side_effect = LLMProviderError(LLMErrorType.TIMEOUT, 408, "timeout")
        mock_openai.generate_response.return_value = LLMResponse(content="Timeout Fallback", tool_calls=None)
        res = await orchestrator.generate_response("sys", [], [])
        assert res.content == "Timeout Fallback"
        mock_openai.generate_response.assert_called_once()
    asyncio.run(run())

# TESTE 5: Gemini 400 -> OpenAI NAO e chamado
def test_5_gemini_400_no_fallback(orchestrator, mock_gemini, mock_openai):
    async def run():
        mock_gemini.generate_response.side_effect = LLMProviderError(LLMErrorType.INVALID_REQUEST, 400, "400")
        with pytest.raises(LLMProviderError) as exc:
            await orchestrator.generate_response("sys", [], [])
        assert exc.value.error_type == LLMErrorType.INVALID_REQUEST
        mock_gemini.generate_response.assert_called_once()
        mock_openai.generate_response.assert_not_called()
    asyncio.run(run())

# TESTE 6: Gemini 401 -> OpenAI NAO e chamado
def test_6_gemini_401_no_fallback(orchestrator, mock_gemini, mock_openai):
    async def run():
        mock_gemini.generate_response.side_effect = LLMProviderError(LLMErrorType.AUTHENTICATION_ERROR, 401, "401")
        with pytest.raises(LLMProviderError) as exc:
            await orchestrator.generate_response("sys", [], [])
        assert exc.value.error_type == LLMErrorType.AUTHENTICATION_ERROR
        mock_openai.generate_response.assert_not_called()
    asyncio.run(run())

# TESTE 7: Gemini falha, OpenAI sucesso -> resposta do OpenAI
def test_7_gemini_fails_openai_success(orchestrator, mock_gemini, mock_openai):
    async def run():
        mock_gemini.generate_response.side_effect = LLMProviderError(LLMErrorType.PROVIDER_ERROR, 500, "Generic Error")
        mock_openai.generate_response.return_value = LLMResponse(content="OpenAI saved the day", tool_calls=None)
        res = await orchestrator.generate_response("sys", [], [])
        assert res.content == "OpenAI saved the day"
    asyncio.run(run())

# TESTE 8: Gemini falha, OpenAI falha -> erro final controlado
def test_8_both_fail(orchestrator, mock_gemini, mock_openai):
    async def run():
        mock_gemini.generate_response.side_effect = LLMProviderError(LLMErrorType.PROVIDER_UNAVAILABLE, 503, "503")
        mock_openai.generate_response.side_effect = LLMProviderError(LLMErrorType.RATE_LIMITED, 429, "OpenAI 429")
        with pytest.raises(LLMProviderError) as exc:
            await orchestrator.generate_response("sys", [], [])
        assert exc.value.error_type == LLMErrorType.RATE_LIMITED
        mock_openai.generate_response.assert_called_once()
    asyncio.run(run())

# TESTE 9: Gemini retorna Function Call -> fallback nao e acionado
def test_9_gemini_function_call(orchestrator, mock_gemini, mock_openai):
    async def run():
        from llm_provider import GenericToolCall
        tc = GenericToolCall(id="1", name="create_lead", arguments='{"nome":"Jardel"}')
        mock_gemini.generate_response.return_value = LLMResponse(content=None, tool_calls=[tc])
        res = await orchestrator.generate_response("sys", [], [])
        assert res.tool_calls[0].name == "create_lead"
        mock_openai.generate_response.assert_not_called()
    asyncio.run(run())

# TESTE 10: Nenhum fallback configurado
def test_10_no_fallback_configured(mock_gemini):
    async def run():
        with patch('llm_orchestrator.get_llm_provider') as get_prov:
            def side_effect(name):
                if name == "gemini": return mock_gemini
                return None
            get_prov.side_effect = side_effect
            os.environ["LLM_PROVIDER"] = "gemini"
            os.environ["LLM_FALLBACK_PROVIDER"] = ""
            orchestrator = LLMOrchestrator()
            
            mock_gemini.generate_response.side_effect = LLMProviderError(LLMErrorType.PROVIDER_UNAVAILABLE, 503, "503")
            with pytest.raises(LLMProviderError) as exc:
                await orchestrator.generate_response("sys", [], [])
            assert exc.value.error_type == LLMErrorType.PROVIDER_UNAVAILABLE
    asyncio.run(run())

# TESTE 11: Falha no meio de uma cadeia de tool call (fallback desativado)
def test_11_no_fallback_mid_chain(orchestrator, mock_gemini, mock_openai):
    async def run():
        messages = [
            ChatMessage(role="user", content="Test"),
            ChatMessage(role="assistant", content="calling tool"),
            ChatMessage(role="tool_result", content="result data")
        ]
        mock_gemini.generate_response.side_effect = LLMProviderError(LLMErrorType.PROVIDER_UNAVAILABLE, 503, "503")
        with pytest.raises(LLMProviderError) as exc:
            await orchestrator.generate_response("sys", messages, [])
        assert exc.value.error_type == LLMErrorType.PROVIDER_UNAVAILABLE
        mock_gemini.generate_response.assert_called_once()
        mock_openai.generate_response.assert_not_called()
    asyncio.run(run())
