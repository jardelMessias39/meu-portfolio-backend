import pytest
from tools_executor import ToolExecutor
import json
import asyncio
import os
from unittest.mock import patch, MagicMock

# Define variaveis fake
os.environ["INTEGRATION_LAYER_URL"] = "http://fake-integration.com"
os.environ["CONSULTOR_API_KEY"] = "fake-key"

class MockResponse:
    def __init__(self, status_code, text):
        self.status_code = status_code
        self.text = text

def test_tool_executor_201_success():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({"nome": "João", "email": "joao@email.com", "telefone": "123", "empresa": "Empresa", "necessidade_identificada": "Site"})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(201, json.dumps({"ok": True, "data": {"id": "123"}}))
            result_str = await executor.execute_tool("create_lead", args)
            
            # Verificar se os campos foram passados corretamente para o post HTTP
            posted_json = mock_post.call_args[1]['json']
            assert 'nome' in posted_json
            assert 'telefone' in posted_json
            assert 'necessidade_identificada' in posted_json
            assert 'name' not in posted_json
            assert 'phone' not in posted_json
            
            result = json.loads(result_str)
            assert result["ok"] is True
    asyncio.run(run())

def test_tool_executor_400_bad_request():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(400, "")
            result_str = await executor.execute_tool("create_lead", args)
            result = json.loads(result_str)
            assert result["ok"] is False
            assert result["error"]["code"] == "BAD_REQUEST"
    asyncio.run(run())

def test_tool_executor_401_unauthorized():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(401, "")
            result_str = await executor.execute_tool("create_lead", args)
            result = json.loads(result_str)
            assert result["ok"] is False
            assert result["error"]["code"] == "UNAUTHORIZED"
    asyncio.run(run())

def test_tool_executor_429_too_many_requests():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(429, "")
            result_str = await executor.execute_tool("create_lead", args)
            result = json.loads(result_str)
            assert result["ok"] is False
            assert result["error"]["code"] == "TOO_MANY_REQUESTS"
    asyncio.run(run())

def test_tool_executor_500_server_error():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(500, "Internal Error")
            result_str = await executor.execute_tool("create_lead", args)
            result = json.loads(result_str)
            assert result["ok"] is False
            assert result["error"]["code"] == "SERVER_ERROR"
    asyncio.run(run())

