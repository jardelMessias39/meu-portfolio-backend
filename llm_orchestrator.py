import logging
import os
from typing import List, Dict, Any, Optional
from models import ChatMessage
from llm_provider import BaseLLMProvider, LLMResponse, get_llm_provider, LLMErrorType, LLMProviderError

logger = logging.getLogger(__name__)

class LLMOrchestrator:
    def __init__(self):
        # Allow setting providers explicitly if needed, but defaults to env vars
        self.primary_name = os.getenv("LLM_PROVIDER", "gemini").lower()
        self.fallback_name = os.getenv("LLM_FALLBACK_PROVIDER", "").lower()
        
        self.primary_provider = get_llm_provider(self.primary_name)
        self.fallback_provider = None
        if self.fallback_name:
            try:
                self.fallback_provider = get_llm_provider(self.fallback_name)
            except ValueError as e:
                logger.error(f"[LLM_ORCHESTRATOR] Erro ao carregar fallback: {e}")

    def is_mid_tool_call_chain(self, messages: List[ChatMessage]) -> bool:
        if not messages:
            return False
        return messages[-1].role == "tool_result"

    def is_eligible_for_fallback(self, error: LLMProviderError) -> bool:
        eligible_types = [
            LLMErrorType.PROVIDER_UNAVAILABLE,
            LLMErrorType.RATE_LIMITED,
            LLMErrorType.TIMEOUT,
            LLMErrorType.PROVIDER_ERROR
        ]
        return error.error_type in eligible_types

    async def generate_response(
        self,
        system_message: str,
        messages: List[ChatMessage],
        tools: List[Dict[str, Any]]
    ) -> LLMResponse:
        
        model_name = getattr(self.primary_provider, 'model', 'unknown')
        logger.info(f"[LLM_ORCHESTRATOR] primary={self.primary_name} model={model_name} status=calling")
        
        try:
            response = await self.primary_provider.generate_response(system_message, messages, tools)
            logger.info(f"[LLM_ORCHESTRATOR] provider={self.primary_name} status=success")
            return response
        except LLMProviderError as e:
            has_fallback = bool(self.fallback_provider)
            is_mid_chain = self.is_mid_tool_call_chain(messages)
            can_fallback = has_fallback and not is_mid_chain
            
            logger.warning(
                f"[LLM_ORCHESTRATOR] primary={self.primary_name} model={model_name} "
                f"status=provider_error error_type={e.error_type.value} "
                f"http_status={e.status_code} fallback={'yes' if can_fallback else 'no'}"
            )
            
            if can_fallback and self.is_eligible_for_fallback(e):
                fb_model_name = getattr(self.fallback_provider, 'model', 'unknown')
                logger.info(f"[LLM_ORCHESTRATOR] fallback={self.fallback_name} model={fb_model_name} status=calling")
                try:
                    fb_response = await self.fallback_provider.generate_response(system_message, messages, tools)
                    logger.info(f"[LLM_ORCHESTRATOR] provider={self.fallback_name} status=success")
                    return fb_response
                except LLMProviderError as fb_e:
                    logger.error(
                        f"[LLM_ORCHESTRATOR] provider={self.fallback_name} status=provider_error "
                        f"error_type={fb_e.error_type.value} http_status={fb_e.status_code}"
                    )
                    raise fb_e
                except Exception as fb_exc:
                    logger.error(f"[LLM_ORCHESTRATOR] provider={self.fallback_name} status=unexpected_error msg='{str(fb_exc)}'")
                    raise fb_exc
            
            # If no fallback or not eligible, raise original
            raise e
        except Exception as generic_e:
            logger.error(f"[LLM_ORCHESTRATOR] primary={self.primary_name} status=unexpected_error msg='{str(generic_e)}'")
            raise generic_e
