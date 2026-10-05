import os
import pytest
from unittest.mock import patch
from llm_provider import get_llm_provider, OpenAIProvider, GeminiProvider, BaseLLMProvider

def test_get_llm_provider_openai():
    with patch.dict(os.environ, {"LLM_PROVIDER": "openai", "OPENAI_API_KEY": "fake-key"}):
        provider = get_llm_provider()
        assert isinstance(provider, OpenAIProvider)
        assert isinstance(provider, BaseLLMProvider)

def test_get_llm_provider_gemini():
    with patch.dict(os.environ, {"LLM_PROVIDER": "gemini", "GEMINI_API_KEY": "fake-key"}):
        provider = get_llm_provider()
        assert isinstance(provider, GeminiProvider)
        assert isinstance(provider, BaseLLMProvider)

def test_get_llm_provider_default():
    with patch.dict(os.environ, {"OPENAI_API_KEY": "fake-key"}):
        if "LLM_PROVIDER" in os.environ:
            del os.environ["LLM_PROVIDER"]
        provider = get_llm_provider()
        assert isinstance(provider, OpenAIProvider)
        assert isinstance(provider, BaseLLMProvider)

def test_get_llm_provider_invalid():
    with patch.dict(os.environ, {"LLM_PROVIDER": "anthropic"}):
        with pytest.raises(ValueError) as exc:
            get_llm_provider()
        assert "Provedor LLM invalido configurado" in str(exc.value)
