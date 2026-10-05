# -*- coding: utf-8 -*-
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
from llm_provider import GeminiProvider, LLMResponse
from models import ChatMessage

async def run_text_test():
    provider = GeminiProvider()
    
    print("=== TESTE REAL - Resposta Textual ===")
    messages = [ChatMessage(role="user", content="Oi, responda apenas: 'Funcionou!'")]
    resp = await provider.generate_response("Voce e um bot de teste.", messages, tools=[])
    
    print(f"Content: {resp.content}")
    print(f"Tool calls: {resp.tool_calls}")
    
    if resp.content is not None and len(resp.content) > 0:
        print("\nSUCESSO: LLMResponse valido e conteudo textual retornado.")
    else:
        print("\nFALHA: Conteudo vazio ou erro na requisicao.")

if __name__ == "__main__":
    asyncio.run(run_text_test())
