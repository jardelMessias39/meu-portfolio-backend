import os
import asyncio
from dotenv import load_dotenv

# Load dotenv and ensure GEMINI_API_KEY is set
load_dotenv()
if "GEMANI_API_KEY" in os.environ and "GEMINI_API_KEY" not in os.environ:
    os.environ["GEMINI_API_KEY"] = os.environ["GEMANI_API_KEY"]

from llm_provider import GeminiProvider, GenericToolCall, LLMResponse
from models import ChatMessage
from tools_executor import ToolExecutor

async def run_tests():
    provider = GeminiProvider()
    tools_executor = ToolExecutor()
    tools_schemas = tools_executor.get_tools()

    print("=== TESTE A - Resposta Textual ===")
    messages = [ChatMessage(role="user", content="Oi, qual seu nome? Responda em uma frase.")]
    resp_text = await provider.generate_response("Você é o Assistente Gemini.", messages, tools=tools_schemas)
    print(f"Content: {resp_text.content}")
    print(f"Tool calls: {resp_text.tool_calls}")
    assert resp_text.content is not None and len(resp_text.content) > 0, "Conteudo nao pode ser vazio"

    print("\n=== TESTE B - Tool Calling ===")
    messages_tool = [ChatMessage(role="user", content="Gostaria de criar um lead. Meu nome é João, e-mail joao@test.com, telefone 12345 e preciso de automação.")]
    resp_tool = await provider.generate_response("Você é o Consultor.", messages_tool, tools=tools_schemas)
    print(f"Content: {resp_tool.content}")
    print(f"Tool calls: {resp_tool.tool_calls}")
    assert resp_tool.tool_calls is not None, "Deveria retornar uma tool call"
    assert len(resp_tool.tool_calls) > 0, "Deveria retornar pelo menos uma tool call"
    
    tc = resp_tool.tool_calls[0]
    print(f"Name: {tc.name}")
    print(f"ID: {tc.id}")
    print(f"Arguments: {tc.arguments}")
    assert tc.name == "create_lead", "O nome da tool call deve ser create_lead"
    assert tc.id is not None, "O ID nao pode ser None"
    # test se arguments eh um JSON valido
    import json
    args_dict = json.loads(tc.arguments)
    assert isinstance(args_dict, dict), "Argumentos devem ser decodificaveis como dict"

    print("\n=== TESTE C - Conversão de Histórico ===")
    messages_hist = [
        ChatMessage(role="user", content="Teste historico"),
        ChatMessage(role="assistant", content=None, tool_calls=[{
            "id": "call_legado",
            "type": "function",
            "name": "create_lead",
            "arguments": '{"nome": "Maria"}',
            "function": {"name": "create_lead", "arguments": '{"nome": "Maria"}'}
        }]),
        ChatMessage(role="tool_result", name="create_lead", content='{"ok": true}', tool_call_id="call_legado"),
        ChatMessage(role="user", content="Continuando...")
    ]
    resp_hist = await provider.generate_response("Você é o Consultor.", messages_hist, tools=tools_schemas)
    print(f"Histórico convertido com sucesso e nova resposta recebida: {resp_hist.content}")

if __name__ == "__main__":
    asyncio.run(run_tests())
