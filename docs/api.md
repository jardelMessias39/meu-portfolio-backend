# API real

A aplicação registra um router com prefixo `/api`. Não há autenticação ou autorização implementada nas rotas observadas.

## `GET /api/health`

Retorna `{"status": "ok"}`. Não acessa banco.

## `GET /api/`

Retorna `{"message": "API do portfólio rodando!"}`.

## `POST /api/chat`

### Request

Corpo JSON validado por `ChatRequest`:

- `message`: string obrigatória.
- `session_id`: string opcional; ausente ou `null` inicia uma sessão nova.

Mensagem vazia ou somente com espaços produz erro `400` com `detail` `Mensagem vazia`. Termos bloqueados pelo filtro ético também produzem `400`.

### Response

Corpo validado por `ChatResponse`:

- `response`: texto retornado pelo serviço/modelo, ou mensagem técnica de fallback.
- `session_id`: identificador da sessão usada ou criada.

Erros não tratados no endpoint são registrados e retornados como `500` com objeto contendo `detail`. O texto da exceção é incluído na resposta.

## `POST /api/tts`

Recebe um objeto JSON genérico com campo `text`. Sem texto retorna `400` e `{"error": "Sem texto"}`. A implementação atual do serviço de voz retorna `None`, então o endpoint retorna `500` e `{"error": "Falha no áudio"}`. Não há áudio funcional comprovado.

## `GET /api/status`

Consulta até 1000 documentos de `status_checks` e os valida como `StatusCheck`. Os campos observados são `id`, `client_name` e `timestamp`.

## `POST /api/status`

Recebe `StatusCheckCreate` com `client_name` obrigatório. O backend cria `id` e `timestamp`, insere o documento em `status_checks` e retorna `StatusCheck`.

## `GET /api/clima`

Parâmetro de query obrigatório: `cidade: str`. Consulta OpenWeather em `/data/2.5/weather`, usando `OPENWEATHER_KEY`, unidades métricas e idioma `pt_br`. Status diferente de 200 é convertido em `404` para cidade não encontrada; outras exceções são convertidas em objeto `{"erro": "..."}`.

## `GET /api/previsao`

Parâmetros de query obrigatórios: `lat: float` e `lon: float`. Consulta a previsão OpenWeather e retorna uma lista construída a partir dos itens de `12:00:00`, com campos `dataLabel`, `temp_max`, `sensacao`, `umidade`, `pressao`, `vento`, `icon`, `climaPrincipal`, `weather` e `fullDate`. Falha HTTP do provedor produz `500`.

## `POST /api/sugerir`

Recebe objeto genérico com campo `clima`, que precisa conter as chaves acessadas pelo prompt (`cidade`, `descricao` e `temp`). Consulta Groq em `https://api.groq.com/openai/v1/chat/completions`, modelo `llama-3.3-70b-versatile`, usando `GROQ_KEY`. Retorna `{"sugestao": ...}` a partir da primeira escolha da resposta do provedor. O formato de erro detalhado não é normalizado.

## Observações

Os arquivos do frontend e seus clientes HTTP não estão neste workspace. O endpoint realmente implementado para o chatbot é `POST /api/chat`; não é possível comprovar aqui qual frontend o consome nem se existe `mock.ts`.
