import sys

with open('test_tool_calling.py', 'a', encoding='utf-8') as f:
    f.write('''

def test_tool_executor_schedule_201_success():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({"nome": "Maria", "email": "maria@email.com", "telefone": "123", "empresa": "Tech", "data_hora": "2026-10-10T10:00:00Z", "assunto": "Projeto", "observacoes": ""})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(201, json.dumps({"ok": True, "data": {"id": "456"}}))
            result_str = await executor.execute_tool("schedule_meeting", args)
            
            posted_json = mock_post.call_args[1]['json']
            assert 'data_hora' in posted_json
            assert 'assunto' in posted_json
            assert 'observacoes' in posted_json
            
            result = json.loads(result_str)
            assert result["ok"] is True
            assert "Reuniao agendada" in result["message"]
    asyncio.run(run())

def test_tool_executor_schedule_200_duplicate():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({"nome": "Maria", "email": "maria@email.com", "telefone": "123", "empresa": "Tech", "data_hora": "2026-10-10T10:00:00Z", "assunto": "Projeto"})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(200, json.dumps({"ok": True, "message": "Duplicado"}))
            result_str = await executor.execute_tool("schedule_meeting", args)
            result = json.loads(result_str)
            assert result["ok"] is True
            assert "duplicado" in result["message"].lower()
    asyncio.run(run())

def test_tool_executor_schedule_400():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(400, "")
            result_str = await executor.execute_tool("schedule_meeting", args)
            result = json.loads(result_str)
            assert result["ok"] is False
            assert result["error"]["code"] == "BAD_REQUEST"
    asyncio.run(run())

def test_tool_executor_schedule_schema():
    executor = ToolExecutor()
    tools = executor.get_tools()
    assert len(tools) == 2
    schedule_tool = next((t for t in tools if t["function"]["name"] == "schedule_meeting"), None)
    assert schedule_tool is not None
    assert "data_hora" in schedule_tool["function"]["parameters"]["required"]
''')
