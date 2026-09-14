# JM Digital Identity System — Backend

**Stack:** FastAPI (Python) · MongoDB · OpenAI
**Localização:** `C:\Users\Jardel\projetos-jardel\meu-portfolio-backend`

---

## Requisitos
- Python 3.9+
- MongoDB

---

## 1. Instalação e Ambiente Virtual

O projeto utiliza um ambiente virtual (venv) para isolar as dependências.

### Ativação da venv (Windows):
```bash
# Na pasta do backend
venv\Scripts\activate
```

### Dependências necessárias:
As dependências estão listadas no arquivo `requirements.txt`.
Para instalá-las (com a venv ativada):
```bash
pip install -r requirements.txt
```

Principais dependências:
- `fastapi`, `uvicorn` (Servidor e Framework)
- `motor` (Driver assíncrono para MongoDB)
- `openai` (Integração com a IA)
- `pydantic` (Validação de dados)
- `python-dotenv` (Variáveis de ambiente)

---

## 2. Iniciar o Servidor FastAPI

Com a **venv ativada**, inicie o servidor com o comando correto do uvicorn:

```bash
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```
Alternativamente, se houver problemas de path, execute via python:
```bash
python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

- **Porta utilizada:** `8000`
- **Host:** `127.0.0.1` (localhost)

A documentação interativa da API (Swagger UI) pode ser acessada em: `http://localhost:8000/docs`

---

## 3. Variáveis de Ambiente

Crie um arquivo `.env` na raiz do backend baseado no `.env.exemple`.
As variáveis necessárias são:

- `MONGO_URL`: String de conexão (URI) do MongoDB. Utilizada para persistir o histórico de conversas (`conversas_portfolio`) e dados de sessão (`chat_sessions`).
- `DB_NAME`: Nome do banco de dados no MongoDB (ex: `meu-portfolio`).
- `OPENAI_API_KEY`: Chave de API da OpenAI para alimentar a inteligência do Consultor Digital (GPT-4o-mini).
- `CORS_ORIGINS`: (Opcional) URLs permitidas para requisições CORS em produção, separadas por vírgula (ex: `https://meudominio.com`). Em dev, o fallback é `*`.

> **AVISO DE SEGURANÇA:** O arquivo `.env` NUNCA deve ser commitado no repositório. Nunca exponha valores reais ou secrets publicamente.

---

## 4. Endpoint do Chatbot

O motor de IA opera principalmente através do endpoint de chat.

- **Rota:** `POST /api/chat`
- **Responsabilidade do Backend:**
  1. Validar e analisar a requisição.
  2. Executar validação ética de palavras proibidas (via `chat_service.verificar_etica`).
  3. Identificar a sessão ou criar uma nova se for o primeiro contato.
  4. Injetar o **Contexto do Consultor Digital** (System Prompt) que contém a identidade da marca, projetos, FAQ e diretrizes de atendimento.
  5. Limitar o histórico anexado para as últimas 20 mensagens para economia de tokens.
  6. Realizar a chamada segura à API da OpenAI (`AsyncOpenAI`).
  7. Salvar as mensagens originais no MongoDB.
  8. Retornar a resposta gerada de volta ao frontend.

**Request Schema (`ChatRequest`):**
```json
{
  "message": "string",
  "session_id": "string | null"
}
```

**Response Schema (`ChatResponse`):**
```json
{
  "response": "string",
  "session_id": "string"
}
```

---

## 5. Arquitetura (Fluxo Completo)

A arquitetura do JM Digital Identity System separa a UI do processamento lógico.

**O fluxo da conversa funciona da seguinte forma:**

1. **Frontend (React/Vite):** O usuário digita uma mensagem ou usa o microfone. O frontend envia a mensagem e o `session_id` para o backend via requisição HTTP POST, exibindo o status de loading.
2. **Backend (FastAPI):** Recebe o POST. Valida segurança e formatação (Pydantic). O `chat_service.py` anexa o **Contexto do Consultor Digital** à mensagem e recupera o histórico da sessão.
3. **OpenAI:** O FastAPI se comunica com a OpenAI via SDK, enviando o prompt unificado. A IA processa e devolve a resposta em texto.
4. **MongoDB:** A interação completa (Usuário + Bot + ID de sessão) é salva permanentemente no banco.
5. **Retorno:** A string da resposta retorna pelo FastAPI até o React, que remove o loading e exibe a mensagem na interface.

```
+--------------------+
|  React (Frontend)  |
|  - UI              |
|  - Web Speech API  |
|  - Estado Local    |
+---------+----------+
          |
    POST /api/chat
          |
          v
+---------+----------+
|  FastAPI (Backend) |
|  - Validação Ética |
|  - Contexto (RAG)  |
+----+---------+-----+
     |         |
     v         v
+----+---+ +---+-------+
| OpenAI | | MongoDB   |
| (LLM)  | | (Sessões) |
+--------+ +-----------+
```
