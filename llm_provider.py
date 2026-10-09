from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
import os
import logging
import base64
from openai import AsyncOpenAI
from models import ChatMessage

logger = logging.getLogger(__name__)
from enum import Enum

class LLMErrorType(Enum):
    PROVIDER_UNAVAILABLE = "PROVIDER_UNAVAILABLE"
    RATE_LIMITED = "RATE_LIMITED"
    AUTHENTICATION_ERROR = "AUTHENTICATION_ERROR"
    INVALID_REQUEST = "INVALID_REQUEST"
    PROVIDER_NOT_FOUND = "PROVIDER_NOT_FOUND"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    TIMEOUT = "TIMEOUT"

class LLMProviderError(Exception):
    def __init__(self, error_type: LLMErrorType, status_code: int, message: str, original_exc: Exception = None):
        self.error_type = error_type
        self.status_code = status_code
        self.message = message
        self.original_exc = original_exc
        super().__init__(self.message)

class GenericToolCall(BaseModel):
    id: str
    name: str
    arguments: str
    metadata: Optional[Dict[str, Any]] = None

class LLMResponse(BaseModel):
    content: Optional[str] = None
    tool_calls: Optional[List[GenericToolCall]] = None

class BaseLLMProvider(ABC):
    @abstractmethod
    async def generate_response(
        self,
        system_message: str,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        pass

class OpenAIProvider(BaseLLMProvider):
    def __init__(self):
        self.client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = "gpt-4o-mini"

    def _convert_message_to_openai(self, msg: ChatMessage) -> Dict[str, Any]:
        msg_dict = {"role": msg.role, "content": msg.content}
        
        if msg.role == "tool_result":
            msg_dict["role"] = "tool"
            msg_dict["tool_call_id"] = msg.tool_call_id
            msg_dict["name"] = msg.name

        if msg.tool_calls:
            msg_dict["tool_calls"] = []
            for tc in msg.tool_calls:
                name = tc.name or (tc.function.name if tc.function else "")
                args = tc.arguments or (tc.function.arguments if tc.function else "")
                msg_dict["tool_calls"].append({
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": name,
                        "arguments": args
                    }
                })
        
        return {k: v for k, v in msg_dict.items() if v is not None}

    async def generate_response(
        self,
        system_message: str,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        messages_to_openai = [{"role": "system", "content": system_message}]
        
        for msg in messages:
            messages_to_openai.append(self._convert_message_to_openai(msg))
            
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=messages_to_openai,
                tools=tools if tools else None
            )
        except Exception as e:
            error_str = str(e).lower()
            if "503" in error_str or "502" in error_str:
                raise LLMProviderError(LLMErrorType.PROVIDER_UNAVAILABLE, 503, str(e), e)
            elif "429" in error_str or "rate limit" in error_str:
                raise LLMProviderError(LLMErrorType.RATE_LIMITED, 429, str(e), e)
            elif "401" in error_str or "403" in error_str:
                raise LLMProviderError(LLMErrorType.AUTHENTICATION_ERROR, 401, str(e), e)
            elif "400" in error_str:
                raise LLMProviderError(LLMErrorType.INVALID_REQUEST, 400, str(e), e)
            elif "timeout" in error_str:
                raise LLMProviderError(LLMErrorType.TIMEOUT, 408, str(e), e)
            else:
                raise LLMProviderError(LLMErrorType.PROVIDER_ERROR, 500, str(e), e)
        
        response_message = response.choices[0].message
        
        generic_tool_calls = None
        if response_message.tool_calls:
            generic_tool_calls = []
            for tc in response_message.tool_calls:
                generic_tool_calls.append(
                    GenericToolCall(
                        id=tc.id,
                        name=tc.function.name,
                        arguments=tc.function.arguments
                    )
                )
                
        return LLMResponse(
            content=response_message.content,
            tool_calls=generic_tool_calls
        )
import uuid
import json
from google import genai
from google.genai import types

class GeminiProvider(BaseLLMProvider):
    def __init__(self):
        self.client = genai.Client(api_key=os.getenv("GEMINI_API_KEY", "dummy"))
        self.model = os.getenv("GEMINI_MODEL", "gemini-2.5-flash")

    def _convert_tool_to_gemini(self, tool_dict: Dict[str, Any]) -> types.Tool:
        if tool_dict.get("type") == "function":
            func = tool_dict.get("function", {})
            return types.Tool(
                function_declarations=[
                    types.FunctionDeclaration(
                        name=func.get("name"),
                        description=func.get("description"),
                        parameters=func.get("parameters")
                    )
                ]
            )
        return None

    def _convert_message_to_gemini(self, msg: ChatMessage) -> Optional[types.Content]:
        if msg.role == "user":
            return types.Content(role="user", parts=[types.Part.from_text(text=msg.content or "")])
        
        elif msg.role == "assistant":
            parts = []
            if msg.content:
                parts.append(types.Part.from_text(text=msg.content))
            
            if msg.tool_calls:
                for tc in msg.tool_calls:
                    name = tc.name or (tc.function.name if tc.function else "")
                    args_str = tc.arguments or (tc.function.arguments if tc.function else "{}")
                    try:
                        args = json.loads(args_str)
                    except:
                        args = {}
                    part = types.Part.from_function_call(name=name, args=args)
                    if getattr(tc, 'metadata', None) and tc.metadata.get("thought_signature"):
                        part.thought_signature = base64.b64decode(tc.metadata["thought_signature"])
                    parts.append(part)
            
            if not parts:
                parts.append(types.Part.from_text(text=""))
                
            return types.Content(role="model", parts=parts)
            
        elif msg.role in ["tool", "tool_result"]:
            name = msg.name or "unknown_function"
            content = msg.content or "{}"
            try:
                response_dict = json.loads(content)
            except:
                response_dict = {"result": content}
                
            return types.Content(
                role="user", 
                parts=[types.Part.from_function_response(name=name, response=response_dict)]
            )
        
        return None

    async def generate_response(
        self,
        system_message: str,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        contents = []
        for msg in messages:
            converted = self._convert_message_to_gemini(msg)
            if converted:
                contents.append(converted)
                
        gemini_tools = []
        if tools:
            for t in tools:
                gemini_tool = self._convert_tool_to_gemini(t)
                if gemini_tool:
                    gemini_tools.append(gemini_tool)
                    
        config = types.GenerateContentConfig(
            system_instruction=system_message,
            tools=gemini_tools if gemini_tools else None
        )
        
        try:
            response = await self.client.aio.models.generate_content(
                model=self.model,
                contents=contents,
                config=config
            )
        except Exception as e:
            error_str = str(e).lower()
            if "503" in error_str or "unavailable" in error_str:
                raise LLMProviderError(LLMErrorType.PROVIDER_UNAVAILABLE, 503, str(e), e)
            elif "429" in error_str or "quota" in error_str:
                raise LLMProviderError(LLMErrorType.RATE_LIMITED, 429, str(e), e)
            elif "400" in error_str or "invalid" in error_str:
                raise LLMProviderError(LLMErrorType.INVALID_REQUEST, 400, str(e), e)
            elif "401" in error_str or "403" in error_str or "permission" in error_str:
                raise LLMProviderError(LLMErrorType.AUTHENTICATION_ERROR, 401, str(e), e)
            elif "timeout" in error_str:
                raise LLMProviderError(LLMErrorType.TIMEOUT, 408, str(e), e)
            else:
                raise LLMProviderError(LLMErrorType.PROVIDER_ERROR, 500, str(e), e)
        
        generic_tool_calls = None
        text_content = None
        
        if response.candidates and response.candidates[0].content and response.candidates[0].content.parts:
            parts = response.candidates[0].content.parts
            for p in parts:
                if p.function_call:
                    if generic_tool_calls is None:
                        generic_tool_calls = []
                    
                    fc_metadata = None
                    if getattr(p, "thought_signature", None):
                        fc_metadata = {
                            "thought_signature": base64.b64encode(p.thought_signature).decode("utf-8")
                        }
                        
                    fc_id = getattr(p.function_call, "id", None) or str(uuid.uuid4())
                    
                    generic_tool_calls.append(
                        GenericToolCall(
                            id=fc_id,
                            name=p.function_call.name,
                            arguments=json.dumps(p.function_call.args) if p.function_call.args else "{}",
                            metadata=fc_metadata
                        )
                    )
                
                if p.text:
                    if text_content is None:
                        text_content = ""
                    text_content += p.text
            
        return LLMResponse(
            content=text_content,
            tool_calls=generic_tool_calls
        )

def get_llm_provider(provider_name: str = None) -> BaseLLMProvider:
    if not provider_name:
        provider_name = os.getenv("LLM_PROVIDER", "openai").lower()
    else:
        provider_name = provider_name.lower()
    
    if provider_name == "openai":
        return OpenAIProvider()
    elif provider_name == "gemini":
        return GeminiProvider()
    else:
        raise ValueError(f"Provedor LLM invalido configurado: '{provider_name}'. Valores aceitos: 'openai', 'gemini'.")
