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
        ChatMessage(role="user", content="Quero agendar uma reuniao pro dia 06/10/26 as 15hs. Meu nome é Jardel, a empresa é Empresa Teste, o email é teste@exemplo.com. Meu WhatsApp é (79) 99999-9999 e o assunto é desenvolvimento de SaaS.")
    ]
    
    print("Calling GeminiProvider com ferramentas usando gemini-3.5-flash...")
    try:
        contents = []
        for msg in messages:
            converted = provider._convert_message_to_gemini(msg)
            if contents is not None and converted:
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
            model="models/gemini-3.5-flash",
            contents=contents,
            config=config
        )
        
        print("Success!")
        if response.function_calls:
            print("Function Calls:", [f.name for f in response.function_calls])
            for fc in response.function_calls:
                print(f"Args: {fc.args}")
        if response.text:
            print("Text:", response.text)
            
    except Exception as e:
        print(f"Exception raised: {type(e).__name__}: {str(e)}")

if __name__ == '__main__':
    asyncio.run(debug_gemini_history())
