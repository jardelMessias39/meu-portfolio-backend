import pytest
import asyncio
import os
from unittest.mock import patch, MagicMock

os.environ["OPENAI_API_KEY"] = "fake-key"
from llm_provider import OpenAIProvider, LLMResponse, GenericToolCall
from models import ChatMessage

class MockMessage:
    def __init__(self, content, tool_calls=None):
        self.content = content
        self.tool_calls = tool_calls

class MockChoice:
    def __init__(self, message):
        self.message = message

class MockResponse:
    def __init__(self, choices):
        self.choices = choices

class MockToolCallFunction:
    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments

class MockToolCall:
    def __init__(self, id, function):
        self.id = id
        self.function = function

from unittest.mock import patch, AsyncMock

def test_normal_response_no_tool():
    async def run():
        provider = OpenAIProvider()
        
        with patch('openai.resources.chat.completions.AsyncCompletions.create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = MockResponse(
                choices=[MockChoice(MockMessage(content="Olá, sou o Consultor."))]
            )
            
            response = await provider.generate_response("System Prompt", [], [])
            assert response.content == "Olá, sou o Consultor."
            assert response.tool_calls is None
    asyncio.run(run())

def test_tool_call_response():
    async def run():
        provider = OpenAIProvider()
        
        with patch('openai.resources.chat.completions.AsyncCompletions.create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = MockResponse(
                choices=[MockChoice(MockMessage(
                    content=None,
                    tool_calls=[MockToolCall(
                        id="call_123",
                        function=MockToolCallFunction(name="create_lead", arguments='{"nome": "Teste"}')
                    )]
                ))]
            )
            
            response = await provider.generate_response("System Prompt", [], [])
            assert response.content is None
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 1
            assert response.tool_calls[0].id == "call_123"
            assert response.tool_calls[0].name == "create_lead"
            assert response.tool_calls[0].arguments == '{"nome": "Teste"}'
    asyncio.run(run())

def test_openai_error():
    async def run():
        provider = OpenAIProvider()
        
        with patch('openai.resources.chat.completions.AsyncCompletions.create', new_callable=AsyncMock) as mock_create:
            mock_create.side_effect = Exception("503 Service Unavailable")
            
            from llm_provider import LLMProviderError, LLMErrorType
            with pytest.raises(LLMProviderError) as exc_info:
                await provider.generate_response("System Prompt", [], [])
                
            assert exc_info.value.error_type == LLMErrorType.PROVIDER_UNAVAILABLE
    asyncio.run(run())

def test_multiple_tool_calls():
    async def run():
        provider = OpenAIProvider()
        
        with patch('openai.resources.chat.completions.AsyncCompletions.create', new_callable=AsyncMock) as mock_create:
            mock_create.return_value = MockResponse(
                choices=[MockChoice(MockMessage(
                    content=None,
                    tool_calls=[
                        MockToolCall(id="call_1", function=MockToolCallFunction(name="tool1", arguments="{}")),
                        MockToolCall(id="call_2", function=MockToolCallFunction(name="tool2", arguments="{}"))
                    ]
                ))]
            )
            
            response = await provider.generate_response("System", [], [])
            assert response.tool_calls is not None
            assert len(response.tool_calls) == 2
            assert response.tool_calls[0].id == "call_1"
            assert response.tool_calls[1].id == "call_2"
    asyncio.run(run())
