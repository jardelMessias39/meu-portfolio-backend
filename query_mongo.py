import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv

load_dotenv()
mongo_url = os.environ.get('MONGO_URL')
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ.get('DB_NAME', 'test_db')]

async def get_latest_session():
    # Encontra as ultimas interacoes
    cursor = db.chat_sessions.find().sort('updated_at', -1).limit(5)
    docs = await cursor.to_list(length=5)
    for doc in docs:
        print('Session:', doc['session_id'])
        for msg in doc['messages']:
            print(f"[{msg.get('role')}] content: {msg.get('content')} | tool_calls: {msg.get('tool_calls')} | tool_call_id: {msg.get('tool_call_id')} | name: {msg.get('name')}")
        print('---')

asyncio.run(get_latest_session())
