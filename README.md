# Backend do portfólio JM Digital Identity System

Documentação técnica baseada exclusivamente no estado observável deste repositório. O projeto é uma API Python/FastAPI para o portfólio, com chatbot, persistência MongoDB e integrações de clima e sugestão de roupas.

## Objetivo e stack

- Python com FastAPI e Uvicorn.
- Pydantic para validação dos contratos observados.
- MongoDB via Motor/PyMongo.
- OpenAI `gpt-4o-mini` para o chatbot.
- OpenWeather para clima/previsão.
- Groq `llama-3.3-70b-versatile` para sugestão de roupas.
- `python-dotenv` para carregar variáveis de ambiente.

## Estrutura

- `server.py`: aplicação, CORS, ciclo de vida do MongoDB e rotas.
- `chat_service.py`: chatbot, prompt fixo, sessão, histórico, persistência e TTS desativado.
- `models.py`: modelos Pydantic.
- `requirements.txt`: dependências declaradas.
- `test_mongo.py`: diagnóstico manual de conexão MongoDB.
- `python test_env.py`: diagnóstico manual de variável OpenAI.
- `docs/`: auditoria técnica detalhada.

Não há frontend, `mock.ts`, Dockerfile, configuração Render ou CI/CD versionados neste workspace.

## API principal

Todas as rotas usam o prefixo `/api`:

- `GET /api/health`
- `GET /api/`
- `POST /api/chat`
- `POST /api/tts`
- `GET /api/status` e `POST /api/status`
- `GET /api/clima`
- `GET /api/previsao`
- `POST /api/sugerir`

O contrato real está em [docs/api.md](docs/api.md). O fluxo detalhado do chatbot está em [docs/chatbot.md](docs/chatbot.md).

## Chatbot

O endpoint `POST /api/chat` recebe `message` e `session_id` opcional. O serviço aplica filtro de termos, recupera ou cria sessão em `chat_sessions`, envia o prompt fixo e as últimas 20 mensagens à OpenAI, salva a sessão, registra a troca em `conversas_portfolio` e retorna `response` com `session_id`.

O conhecimento de CondutorPro e Encantos da Ana está presente como texto no prompt. Não há RAG comprovado: não existem embeddings, busca vetorial ou recuperação de documentos. TTS também não está funcional no estado atual; a função retorna `None`.

## Banco e configurações

As collections observadas são `chat_sessions`, `conversas_portfolio` e `status_checks`. O banco é selecionado por `DB_NAME` e a conexão por `MONGO_URL`; seus valores não são documentados.

Variáveis referenciadas pelo código: `MONGO_URL`, `DB_NAME`, `OPENAI_API_KEY`, `CORS_ORIGINS`, `OPENWEATHER_KEY`, `GROQ_KEY`, `ELEVEN_API_KEY` e `VOICE_ID`. Nenhum valor secreto é documentado. O `.env` é ignorado pelo Git; use [.env.exemple](.env.exemple) apenas como referência de nomes e placeholders.

## Execução local

Com as dependências instaladas e o ambiente configurado:

```text
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

A documentação interativa fica em `http://localhost:8000/docs` quando o servidor está em execução.

## Checks e testes

Não há suíte automatizada identificada. Os scripts existentes são diagnósticos manuais. Nesta auditoria, a compilação Python passou; a coleta via `pytest` falhou antes de coletar testes porque o Python global não tinha `pymongo` disponível. Veja [docs/testing.md](docs/testing.md).

## Deploy e estado atual

O comando local está documentado, mas não há configuração versionada de produção, Render, Docker, pipeline ou domínio. A arquitetura, integrações, segurança, evolução e decisões observáveis estão detalhadas em [docs/architecture.md](docs/architecture.md), [docs/integrations.md](docs/integrations.md), [docs/deployment.md](docs/deployment.md), [docs/security.md](docs/security.md), [docs/evolution.md](docs/evolution.md) e [docs/decisions.md](docs/decisions.md).

## Limitações e lacunas

- Frontend consumidor e `mock.ts` não estão neste workspace.
- Não há autenticação, autorização ou rate limiting observados.
- Não há índices, retenção, backup ou configuração externa do MongoDB versionados.
- Não há timeout/retry uniforme para chamadas externas.
- Não há testes de contrato, integração ou cobertura identificados.
- Deploy atual e configuração do provedor são não identificados.
