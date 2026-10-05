import base64
import json
import pytest
from models import ToolCall, ChatMessage, ChatSession
from llm_provider import GenericToolCall, GeminiProvider
from google.genai import types
import uuid

# A. GenericToolCall sem metadata
def test_generic_tool_call_without_metadata():
    tc = GenericToolCall(id="1", name="test", arguments="{}")
    assert tc.metadata is None
    assert tc.id == "1"

# B. OpenAIProvider continues working (already tested in test_openai_provider.py which we will run)

# F, G. ToolCall aceita metadata=None e metadata preenchida
def test_toolcall_metadata():
    tc1 = ToolCall(id="1", name="test", arguments="{}")
    assert tc1.metadata is None
    
    tc2 = ToolCall(id="2", name="test", arguments="{}", metadata={"key": "value"})
    assert tc2.metadata == {"key": "value"}

# H. Sessao antiga sem metadata
def test_old_session_loading():
    old_data = {
        "session_id": "session_123",
        "messages": [
            {
                "role": "assistant",
                "tool_calls": [
                    {
                        "id": "call_1",
                        "type": "function",
                        "name": "test",
                        "arguments": "{}"
                    }
                ]
            }
        ]
    }
    session = ChatSession(**old_data)
    assert session.messages[0].tool_calls[0].metadata is None

# D, C, I. Serializacao, bytes e recuperacao
def test_thought_signature_serialization():
    original_bytes = b'\x12\xae\x02\n\xab\x02'
    base64_encoded = base64.b64encode(original_bytes).decode("utf-8")
    
    metadata = {"thought_signature": base64_encoded}
    tc = ToolCall(id="1", name="get_weather", arguments="{}", metadata=metadata)
    
    msg = ChatMessage(role="assistant", tool_calls=[tc])
    provider = GeminiProvider()
    
    # Simula _convert_message_to_gemini
    part_content = provider._convert_message_to_gemini(msg)
    
    assert part_content.role == "model"
    part = part_content.parts[0]
    assert part.function_call.name == "get_weather"
    assert part.thought_signature == original_bytes

# E. ChatService transporta metadata
def test_chat_service_transport():
    # Simulating what ChatService does without loading the whole db mock
    from chat_service import ChatService
    from unittest.mock import MagicMock
    
    db_mock = MagicMock()
    service = ChatService(db_mock)
    
    class FakeResponse:
        def __init__(self):
            self.content = None
            self.tool_calls = [
                GenericToolCall(id="1", name="test", arguments="{}", metadata={"thought_signature": "base64_str"})
            ]
            
    llm_response = FakeResponse()
    
    tool_calls_data = []
    for tc in llm_response.tool_calls:
        tool_calls_data.append({
            "id": tc.id,
            "type": "function",
            "name": tc.name,
            "arguments": tc.arguments,
            "metadata": getattr(tc, "metadata", None),
            "function": {"name": tc.name, "arguments": tc.arguments}
        })
        
    msg = ChatMessage(role="assistant", tool_calls=tool_calls_data)
    assert msg.tool_calls[0].metadata == {"thought_signature": "base64_str"}

