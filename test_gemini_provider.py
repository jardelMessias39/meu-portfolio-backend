import pytest
import asyncio
import os
import json
from unittest.mock import patch, MagicMock, AsyncMock

# Mock environ before importing provider
os.environ["GEMINI_API_KEY"] = "fake-key"
from llm_provider import GeminiProvider, LLMResponse, GenericToolCall
from models import ChatMessage, ToolCall, ToolCallFunction
from google.genai import types

class MockPart:
    def __init__(self, text=None, function_call=None):
        self.text = text
        self.function_call = function_call

class MockContent:
    def __init__(self, parts):
        self.parts = parts

class MockCandidate:
    def __init__(self, content):
        self.content = content

class MockFunctionCall:
    def __init__(self, name, args):
        self.name = name
        self.args = args

class MockResponse:
    def __init__(self, text=None, function_calls=None, candidates=None):
        self.text = text
        self.function_calls = function_calls
        self.candidates = candidates or []

def test_gemini_normal_response():
    async def run():
        provider = GeminiProvider()
        
        with patch('google.genai.Client.aio') as mock_aio:
            mock_generate = AsyncMock()
            mock_generate.return_value = MockResponse(
                candidates=[MockCandidate(content=MockContent(parts=[MockPart(text="Olá, sou o Consultor Gemini.")]))]
            )
            provider.client.aio.models.generate_content = mock_generate
            
            response = await provider.generate_response("System Prompt", [], [])
            assert response.content == "Olá, sou o Consultor Gemini."
            assert response.tool_calls is None
    asyncio.run(run())

def test_gemini_function_call():
    async def run():
        provider = GeminiProvider()
        
        with patch('google.genai.Client.aio') as mock_aio:
            mock_generate = AsyncMock()
            mock_part = MockPart(function_call=MockFunctionCall(name="create_lead", args={"nome": "Teste"}))
            mock_generate.return_value = MockResponse(
                candidates=[MockCandidate(content=MockContent(parts=[mock_part]))]
            )
            provider.client.aio.models.generate_content = mock_generate
            
            response = await provider.generate_response("System", [], [])
            assert response.content is None
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0].name == "create_lead"
            assert response.tool_calls[0].arguments == '{"nome": "Teste"}'
            assert response.tool_calls[0].id is not None
    asyncio.run(run())

def test_gemini_multiple_function_calls():
    async def run():
        provider = GeminiProvider()
        
        with patch('google.genai.Client.aio') as mock_aio:
            mock_generate = AsyncMock()
            mock_part1 = MockPart(function_call=MockFunctionCall(name="tool1", args={"a": 1}))
            mock_part2 = MockPart(function_call=MockFunctionCall(name="tool2", args={"b": 2}))
            mock_generate.return_value = MockResponse(
                candidates=[MockCandidate(content=MockContent(parts=[mock_part1, mock_part2]))]
            )
            provider.client.aio.models.generate_content = mock_generate
            
            response = await provider.generate_response("System", [], [])
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 2
            assert response.tool_calls[0].name == "tool1"
            assert response.tool_calls[1].name == "tool2"
    asyncio.run(run())

def test_gemini_schema_conversion():
    provider = GeminiProvider()
    openai_tool = {
        "type": "function",
        "function": {
            "name": "test_tool",
            "description": "desc",
            "parameters": {"type": "object", "properties": {"a": {"type": "string"}}}
        }
    }
    
    gemini_tool = provider._convert_tool_to_gemini(openai_tool)
    assert gemini_tool is not None
    assert len(gemini_tool.function_declarations) == 1
    assert gemini_tool.function_declarations[0].name == "test_tool"

def test_gemini_legacy_history():
    provider = GeminiProvider()
    
    legacy_msg = ChatMessage(
        role="tool",
        name="test_tool",
        content='{"ok": true}',
        tool_call_id="call_abc"
    )
    
    gemini_msg = provider._convert_message_to_gemini(legacy_msg)
    assert gemini_msg is not None
    assert gemini_msg.role == "user" # Gemini treats function responses as user role
    assert len(gemini_msg.parts) == 1
    assert gemini_msg.parts[0].function_response is not None
    assert gemini_msg.parts[0].function_response.name == "test_tool"
    assert gemini_msg.parts[0].function_response.response == {"ok": True}

def test_gemini_error_handling():
    async def run():
        provider = GeminiProvider()
        
        with patch('google.genai.Client.aio') as mock_aio:
            mock_generate = AsyncMock()
            mock_generate.side_effect = Exception("503 UNAVAILABLE")
            provider.client.aio.models.generate_content = mock_generate
            
            from llm_provider import LLMProviderError, LLMErrorType
            import pytest
            with pytest.raises(LLMProviderError) as exc_info:
                await provider.generate_response("System Prompt", [], [])
            
            assert exc_info.value.error_type == LLMErrorType.PROVIDER_UNAVAILABLE
    asyncio.run(run())
