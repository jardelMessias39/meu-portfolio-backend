import asyncio
import os
import json
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
from chat_service import ChatService

load_dotenv()

async def run_tests():
    mongo_url = os.environ.get('MONGO_URL')
    if not mongo_url:
        print("MONGO_URL not found")
        return
    
    client = AsyncIOMotorClient(mongo_url)
    db = client[os.environ.get('DB_NAME', 'test_db')]
    chat_service = ChatService(db)

    print("=== TESTE 1: Conversa normal ===")
    response, session_id = await chat_service.process_message("OlÃ¡, qual Ã© a sua stack de tecnologia?")
    print(f"User: OlÃ¡, qual Ã© a sua stack de tecnologia?")
    print(f"Bot: {response}\n")
    
    session = await chat_service.get_or_create_session(session_id)
    # Deve ter 2 mensagens: user e assistant
    assert len(session.messages) == 2, f"Expected 2 messages, got {len(session.messages)}"
    assert getattr(session.messages[-1], "tool_calls", None) is None, "Should not have tool_calls"
    print("âœ… TESTE 1 PASSOU\n")

    print("=== TESTE 2: Lead incompleto ===")
    response, session_id2 = await chat_service.process_message("Quero registrar um lead")
    print(f"User: Quero registrar um lead")
    print(f"Bot: {response}\n")
    
    session2 = await chat_service.get_or_create_session(session_id2)
    assert getattr(session2.messages[-1], "tool_calls", None) is None, "Should not have tool_calls prematurely"
    print("âœ… TESTE 2 PASSOU\n")

    print("=== TESTE 3 e 4: Lead completo & PersistÃªncia ===")
    response, session_id3 = await chat_service.process_message("Quero registrar um lead. Nome: Teste, Email: teste@teste.com, Telefone: 9999999, Empresa: Test Corp, Necessidade: Sistema Web")
    print(f"User: Quero registrar um lead com dados...")
    print(f"Bot: {response}\n")
    
    session3 = await chat_service.get_or_create_session(session_id3)
    # HistÃ³rico no MongoDB deve conter:
    # 1. user: Quero registrar um lead...
    # 2. assistant com tool_calls
    # 3. tool com resultado
    # 4. assistant com resposta final
    assert len(session3.messages) == 4, f"Expected 4 messages, got {len(session3.messages)}"
    assert getattr(session3.messages[1], "tool_calls", None) is not None, "Message 2 should contain tool_calls"
    assert session3.messages[2].role == "tool", "Message 3 should be tool result"
    assert session3.messages[3].role == "assistant", "Message 4 should be final response"
    print("âœ… TESTE 3 e 4 PASSOU\n")

    print("=== TESTE 5: Reentrada ===")
    # Manda mais uma mensagem na mesma sessÃ£o
    response, session_id3_novo = await chat_service.process_message("Qual Ã© a stack mesmo?", session_id3)
    print(f"User: Qual Ã© a stack mesmo?")
    print(f"Bot: {response}\n")
    
    session3_re = await chat_service.get_or_create_session(session_id3)
    # +2 messages
    assert len(session3_re.messages) == 6, f"Expected 6 messages, got {len(session3_re.messages)}"
    print("âœ… TESTE 5 PASSOU\n")
    
    # Cleanup opcional para nÃ£o sujar banco de dados (pular no teste real ou deletar por session_id)
    await db.chat_sessions.delete_one({"session_id": session_id})
    await db.chat_sessions.delete_one({"session_id": session_id2})
    await db.chat_sessions.delete_one({"session_id": session_id3})

    
    print("ðŸŽ‰ TODOS OS TESTES PASSARAM!")

if __name__ == "__main__":
    asyncio.run(run_tests())
