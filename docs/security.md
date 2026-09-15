# Segurança

## Secrets e configuração

Variáveis observadas: `MONGO_URL`, `DB_NAME`, `OPENAI_API_KEY`, `CORS_ORIGINS`, `OPENWEATHER_KEY`, `GROQ_KEY`, `ELEVEN_API_KEY` e `VOICE_ID`. Os valores não são documentados. `.env` está no `.gitignore`; o arquivo de exemplo usa placeholders.

O script `test_mongo.py` contém apenas uma URI de exemplo com placeholder de senha. Nenhum valor de credencial deve ser versionado ou reproduzido na documentação.

## Proteções observadas

- Pydantic valida os modelos de chat e status.
- O chatbot bloqueia uma lista literal de termos de risco antes da chamada à IA.
- CORS é configurável por ambiente.
- O cliente MongoDB é fechado no lifespan.

## Proteções não identificadas

Não há autenticação, autorização, rate limiting, quotas, CSRF, assinatura de webhook, auditoria de acesso ou política de rotação de secrets no código observado.

## Riscos técnicos identificados

- `allow_origins` usa `*` por fallback junto com `allow_credentials=True`; isso exige revisão da configuração efetiva do navegador e de produção.
- O endpoint de chat retorna `str(e)` em alguns erros `500`, podendo expor detalhes internos.
- Os logs incluem traceback do chat e mensagens de erro de persistência; não há política de mascaramento observada.
- Mensagens do usuário e respostas são persistidas em MongoDB sem retenção ou minimização documentada.
- A API de clima monta a URL com valores derivados da entrada e não define timeout explícito no `httpx.AsyncClient`.
- A rota `/api/sugerir` acessa chaves do objeto `clima` e campos da resposta externa sem normalização de erros.
- As APIs públicas não apresentam controles de abuso no código.

Estas são observações de auditoria, não correções aplicadas. Nenhum arquivo de código foi alterado para esta documentação.
