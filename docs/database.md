# Banco de dados

## MongoDB

**FATO OBSERVADO:** `server.py` carrega `MONGO_URL`, cria `AsyncIOMotorClient` e seleciona o banco pelo valor de `DB_NAME`. O nome concreto configurado em ambiente não é documentado aqui.

O cliente é encerrado no lifespan da aplicação. Não há health check explícito do banco no startup; o endpoint `/api/health` apenas retorna status.

## Collections observadas

### `chat_sessions`

Documento compatível com `ChatSession`:

- `session_id`: string UUID.
- `created_at`: datetime.
- `updated_at`: datetime.
- `messages`: lista de objetos com `role`, `content` e `timestamp`.

Operações: `find_one` por `session_id`, `insert_one` na criação e `update_one` com `upsert=True` após uma resposta.

### `conversas_portfolio`

Documento inserido após a resposta do chatbot:

- `data`: datetime UTC.
- `usuario`: mensagem enviada.
- `bot`: resposta gerada.
- `session_id`: identificador da sessão.
- `origem`: `web_portfolio`.

Não há leitura dessa collection no código observado.

### `status_checks`

Usada pelas rotas de status. O documento contém `id`, `client_name` e `timestamp`. `GET /api/status` lê até 1000 documentos; `POST /api/status` insere um novo documento.

## Índices e relações

Não há criação ou declaração de índices no repositório. A relação entre as collections do chatbot é o campo `session_id`, mas não há foreign key nem validação de integridade observada.

## O que não está versionado

Não estão versionados o nome efetivo do banco, credenciais, dados reais, índices criados no servidor, políticas de retenção, backups, configuração do Atlas ou permissões de usuário.

O script `test_mongo.py` contém uma URI de exemplo com placeholder de senha e tenta listar bancos, mas não faz parte do fluxo da aplicação.
