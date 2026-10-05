import sys

with open('test_tool_calling.py', 'a', encoding='utf-8') as f:
    f.write('''

def test_tool_executor_schedule_401():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(401, "")
            result_str = await executor.execute_tool("schedule_meeting", args)
            result = json.loads(result_str)
            assert result["ok"] is False
            assert result["error"]["code"] == "UNAUTHORIZED"
    asyncio.run(run())

def test_tool_executor_schedule_429():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(429, "")
            result_str = await executor.execute_tool("schedule_meeting", args)
            result = json.loads(result_str)
            assert result["ok"] is False
            assert result["error"]["code"] == "TOO_MANY_REQUESTS"
    asyncio.run(run())

def test_tool_executor_schedule_500():
    async def run():
        executor = ToolExecutor()
        args = json.dumps({})
        
        with patch('httpx.AsyncClient.post') as mock_post:
            mock_post.return_value = MockResponse(500, "Internal Error")
            result_str = await executor.execute_tool("schedule_meeting", args)
            result = json.loads(result_str)
            assert result["ok"] is False
            assert result["error"]["code"] == "SERVER_ERROR"
    asyncio.run(run())
''')
