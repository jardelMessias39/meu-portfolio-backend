# Arquitetura atual

## Escopo da evidência

Esta descrição foi produzida a partir dos arquivos versionados deste workspace. O frontend, a infraestrutura do provedor e configurações externas não estão versionados aqui; portanto não são tratados como fatos do backend sem evidência local.

## Componentes

- `server.py`: cria a aplicação FastAPI, configura o ciclo de vida do cliente MongoDB, registra o router `/api`, CORS e endpoints de chat, TTS, status e clima.
- `models.py`: define os modelos Pydantic usados por chat, sessões e status.
- `chat_service.py`: implementa o serviço de chatbot, prompt fixo, filtro de termos, sessões MongoDB, chamada à OpenAI, histórico e TTS desativado.
- `requirements.txt`: declara dependências Python.
- `test_mongo.py` e `python test_env.py`: scripts auxiliares de diagnóstico, não uma suíte de testes.

## Fluxo comprovado do chatbot

1. Um cliente externo faz `POST /api/chat` com `message` e, opcionalmente, `session_id`.
2. FastAPI valida o corpo com `ChatRequest`.
3. `chat_endpoint` rejeita mensagem vazia e chama `ChatService.process_message`.
4. O serviço aplica a lista literal de termos proibidos.
5. Se houver `session_id`, o serviço consulta `chat_sessions`; se não encontrar uma sessão, cria UUID, timestamps e documento nessa collection.
6. A mensagem do usuário é adicionada à sessão. As últimas 20 mensagens são combinadas com o `system_message` fixo.
7. O cliente assíncrono da OpenAI chama o modelo `gpt-4o-mini`.
8. A resposta do modelo é adicionada à sessão, que é atualizada em `chat_sessions`.
9. Um resumo de cada troca é inserido em `conversas_portfolio`.
10. FastAPI retorna `response` e `session_id`.

## Fronteiras

No repositório há código do backend e um exemplo de variáveis. Não há código de frontend, `mock.ts`, Dockerfile, configuração Render, workflow de CI/CD ou definição de infraestrutura. A existência e o contrato de um frontend consumidor são, portanto, não identificados neste workspace.

## Dependências externas observadas

- MongoDB via Motor/PyMongo.
- OpenAI via SDK assíncrono.
- Groq via HTTP na rota de sugestão de clima.
- OpenWeather via HTTP nas rotas de clima.
- ElevenLabs é referenciado por variáveis no serviço, mas a função de áudio retorna `None` e não chama o provedor na versão atual.
