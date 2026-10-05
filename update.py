import sys

with open('tools_executor.py', 'r', encoding='utf-8') as f:
    content = f.read()

schedule_schema = '''
        self.schedule_meeting_schema = {
            "type": "function",
            "function": {
                "name": "schedule_meeting",
                "description": "Agenda uma solicitacao de reuniao com Jardel quando o usuario demonstrar interesse em conversar/reunir-se.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "nome": { "type": "string" },
                        "email": { "type": "string" },
                        "telefone": { "type": "string" },
                        "empresa": { "type": "string" },
                        "data_hora": { "type": "string", "description": "Data e hora no formato ISO 8601 com timezone (obrigatoriamente no futuro)" },
                        "assunto": { "type": "string" },
                        "observacoes": { "type": "string" }
                    },
                    "required": ["nome", "email", "telefone", "empresa", "data_hora", "assunto"]
                }
            }
        }
'''

content = content.replace('        self.create_lead_schema = {', schedule_schema.lstrip('\\n') + '\\n        self.create_lead_schema = {')
content = content.replace('return [self.create_lead_schema]', 'return [self.create_lead_schema, self.schedule_meeting_schema]')

schedule_execution = '''
        elif name == "schedule_meeting":
            try:
                args = json.loads(arguments)
                integration_url = os.environ.get("INTEGRATION_LAYER_URL")
                api_key = os.environ.get("CONSULTOR_API_KEY")
                
                if not integration_url or not api_key:
                    logger.error(f"Variaveis de ambiente nao estao definidas.")
                    return json.dumps({
                        "ok": False, 
                        "error": {
                            "message": "Configuracao de integracao ausente."
                        }
                    })
                
                url = f"{integration_url.rstrip('/')}/backend/v1/tools/schedule_meeting"
                headers = {
                    "X-API-Key": api_key,
                    "Content-Type": "application/json"
                }
                
                async with httpx.AsyncClient() as client:
                    resp = await client.post(url, json=args, headers=headers, timeout=10.0)
                    
                    if resp.status_code == 201:
                        return json.dumps({"ok": True, "message": "Reuniao agendada com sucesso.", "data": resp.text})
                    elif resp.status_code == 200:
                        return json.dumps({"ok": True, "message": "Agendamento duplicado. Ja havia sido registrado.", "data": resp.text})
                    elif resp.status_code == 400:
                        return json.dumps({"ok": False, "error": {"code": "BAD_REQUEST", "message": "Dados invalidos, em falta ou data no passado. Peca correcao."}})
                    elif resp.status_code == 401:
                        return json.dumps({"ok": False, "error": {"code": "UNAUTHORIZED", "message": "Nao autorizado (Erro interno)."}})
                    elif resp.status_code == 429:
                        return json.dumps({"ok": False, "error": {"code": "TOO_MANY_REQUESTS", "message": "Servico ocupado, tente mais tarde."}})
                    else:
                        return json.dumps({"ok": False, "error": {"code": "SERVER_ERROR", "message": "Ocorreu um erro no servidor externo."}})

            except json.JSONDecodeError:
                return json.dumps({"ok": False, "error": {"message": "Invalid arguments format"}})
            except Exception as e:
                return json.dumps({"ok": False, "error": {"message": "Internal error", "details": str(e)}})
'''

content = content.replace('        return json.dumps({"ok": False, "error": {"message": f"Tool \'{name}\' not found"}})', schedule_execution.lstrip('\\n') + '\\n        return json.dumps({"ok": False, "error": {"message": f"Tool \'{name}\' not found"}})')

with open('tools_executor.py', 'w', encoding='utf-8') as f:
    f.write(content)
