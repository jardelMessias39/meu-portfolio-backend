import pytest
from fastapi.testclient import TestClient
from server import app
from models import ChatRequest
from pydantic import ValidationError

client = TestClient(app)

def test_chat_request_max_length():
    # Test valid message
    req = ChatRequest(message="A" * 2000)
    assert req.message == "A" * 2000
    
    # Test message exceeding max_length
    with pytest.raises(ValidationError) as exc:
        ChatRequest(message="A" * 2001)
    assert "String should have at most 2000 characters" in str(exc.value)

def test_chat_route_sanitized_500():
    # We will simulate an internal error in the chat_service
    # by using a mock. The error should not leak in the detail.
    from unittest.mock import patch
    
    with patch("server.chat_service.process_message") as mock_process:
        mock_process.side_effect = Exception("SECRET_DB_ERROR_123")
        
        response = client.post("/api/chat", json={"message": "Hello"})
        assert response.status_code == 500
        
        # Verify the exception string doesn't leak to client
        json_resp = response.json()
        assert "SECRET_DB_ERROR_123" not in str(json_resp)
        assert json_resp["detail"] == "Erro interno no servidor."
