import json
import logging
import httpx
import os

logger = logging.getLogger(__name__)

class ToolExecutor:
    def __init__(self):
        # Definição do schema conforme o Tool Contract V1
        self.create_lead_schema = {
            "type": "function",
            "function": {
                "name": "create_lead",
                "description": "Registra um novo lead qualificado quando o usuário tiver fornecido nome, contato e detalhes do projeto ou necessidade.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nome": { "type": "string" },
                        "email": { "type": "string" },
                        "telefone": { "type": "string" },
                        "empresa": { "type": "string" },
                        "necessidade_identificada": { "type": "string" }
                    },
                    "required": ["nome", "email", "telefone", "necessidade_identificada"]
                }
            }
        }

    def get_tools(self):
        return [self.create_lead_schema]

    async def execute_tool(self, name: str, arguments: str) -> str:
        logger.info(f"ToolExecutor invocado para '{name}' com argumentos: {arguments}")
        
        if name == "create_lead":
            try:
                args = json.loads(arguments)
                integration_url = os.environ.get("INTEGRATION_LAYER_URL")
                api_key = os.environ.get("CONSULTOR_API_KEY")
                
                if not integration_url or not api_key:
                    logger.error("Variaveis de ambiente INTEGRATION_LAYER_URL ou CONSULTOR_API_KEY nao estao definidas.")
                    return json.dumps({"ok": False, "error": {"message": "Configuracao de integracao ausente."}})
                
                url = f"{integration_url.rstrip('/')}/backend/v1/tools/create_lead"
                headers = {
                    "X-API-Key": api_key,
                    "Content-Type": "application/json"
                }
                
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, json=args, headers=headers, timeout=10.0)
                    
                    if resp.status_code in [200, 201]:
                        # A Integration Layer retorna ok: true
                        return resp.text
                    elif resp.status_code == 400:
                        return json.dumps({"ok": False, "error": {"code": "BAD_REQUEST", "message": "Dados invalidos ou faltando. Peca ao usuario."}})
                    elif resp.status_code == 401:
                        logger.error("Integration Layer: 401 Unauthorized")
                        return json.dumps({"ok": False, "error": {"code": "UNAUTHORIZED", "message": "Nao autorizado (Erro interno)."}})
                    elif resp.status_code == 429:
                        return json.dumps({"ok": False, "error": {"code": "TOO_MANY_REQUESTS", "message": "Servico ocupado, tente mais tarde."}})
                    else:
                        logger.error(f"Integration Layer retornou {resp.status_code}: {resp.text}")
                        return json.dumps({"ok": False, "error": {"code": "SERVER_ERROR", "message": "Ocorreu um erro no servidor externo."}})

            except json.JSONDecodeError:
                return json.dumps({"ok": False, "error": {"message": "Invalid arguments format"}})
            except httpx.RequestError as exc:
                logger.error(f"Erro de rede ao conectar com Integration Layer: {exc}")
                return json.dumps({"ok": False, "error": {"message": "Network error, please try again later."}})
            except Exception as e:
                logger.error(f"Erro ao processar argumentos de create_lead: {e}")
                return json.dumps({"ok": False, "error": {"message": "Internal error", "details": str(e)}})
        
        return json.dumps({"ok": False, "error": {"message": f"Tool '{name}' not found"}})
