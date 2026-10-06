# -*- coding: utf-8 -*-
import os
import asyncio
from dotenv import load_dotenv

load_dotenv()
from llm_provider import GeminiProvider
from models import ChatMessage
from tools_executor import ToolExecutor

async def debug_gemini_history():
    provider = GeminiProvider()
    executor = ToolExecutor()
    tools = executor.get_tools()
    
    messages = [
        ChatMessage(role="user", content="Quero contratar você para desenvolver um sistema para minha empresa. Meu nome é Jardel, minha empresa é Empresa Teste e meu email é teste@exemplo.com. Meu WhatsApp é (79) 99999-9999 e quero desenvolver um sistema SaaS"),
        ChatMessage(role="assistant", content="Olá, Jardel! Excelente iniciativa. Desenvolver um SaaS focado na automação... Já anotei todas as informações. Se preferir agendar, informe o dia e horário."),
        ChatMessage(role="user", content="perfeito agende para mim pro dia 06/10/26 as 15hs")
    ]
    
    print("Calling GeminiProvider com ferramentas...")
    try:
        contents = []
        for msg in messages:
            converted = provider._convert_message_to_gemini(msg)
            if converted:
                contents.append(converted)
                
        gemini_tools = []
        if tools:
            for t in tools:
                gemini_tool = provider._convert_tool_to_gemini(t)
                if gemini_tool:
                    gemini_tools.append(gemini_tool)
                    
        from google.genai import types
        config = types.GenerateContentConfig(
            system_instruction="Você é o consultor...",
            tools=gemini_tools if gemini_tools else None
        )
        
        response = await provider.client.aio.models.generate_content(
            model=provider.model,
            contents=contents,
            config=config
        )
        
        print("Success!")
        if response.function_calls:
            print("Function Calls:", [f.name for f in response.function_calls])
        if response.text:
            print("Text:", response.text)
            
    except Exception as e:
        print(f"Exception raised: {type(e).__name__}: {str(e)}")

if __name__ == '__main__':
    asyncio.run(debug_gemini_history())
