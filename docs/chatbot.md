# Chatbot

## Classificação das evidências

- **FATO OBSERVADO:** comportamento diretamente implementado em `server.py`, `chat_service.py` ou `models.py`.
- **INFORMAÇÃO EXTERNA:** referência presente em comentário, README ou texto do prompt, mas não comprovada por uma integração local.
- **LACUNA:** não existe evidência no workspace.
- **HIPÓTESE:** interpretação que exige confirmação fora do repositório.

## Fluxo real

O endpoint é `POST /api/chat`. O corpo tem `message` obrigatório e `session_id` opcional. FastAPI valida o corpo com `ChatRequest`, rejeita mensagem vazia, chama `process_message` e responde com `ChatResponse` contendo `response` e `session_id`.

O serviço verifica termos proibidos, recupera ou cria a sessão, adiciona a mensagem do usuário, envia ao modelo o system prompt mais as últimas 20 mensagens, acrescenta a resposta do assistente, salva a sessão e registra a troca em `conversas_portfolio`.

## Sessão e memória

**FATO OBSERVADO:** a sessão é criada em `get_or_create_session`, com UUID e timestamps. Um `session_id` existente é buscado em `chat_sessions`; se não for encontrado, uma sessão nova é criada. A sessão é atualizada com `upsert=True` após a resposta da IA.

**FATO OBSERVADO:** existe memória persistida de conversa. O histórico completo da sessão fica no documento `chat_sessions`, mas somente as últimas 20 mensagens são enviadas à OpenAI. A coleção `conversas_portfolio` recebe também a mensagem do usuário, a resposta do bot, o identificador da sessão, data e `origem: web_portfolio`.

**LACUNA:** não há expiração, limite de tamanho do documento, paginação ou política de retenção versionados.

## Prompt e conhecimento

**FATO OBSERVADO:** o prompt é uma string fixa em `ChatService.system_message`. Ele define identidade de Jardel Messias, localização e contatos, trajetória, stack, serviços, perguntas frequentes e regras de conduta.

**FATO OBSERVADO:** o conhecimento embutido no prompt cita Secretária.AI, AgendaLivreAI, Acarajé do Diego / Dois Irmãos, EloPro, CondutorPro, Encantos da Ana e Dashboard Financeiro PME. CondutorPro e Encantos da Ana estão presentes explicitamente no prompt, com descrições, stacks e URLs de demo.

**INFORMAÇÃO EXTERNA:** os resultados e características dos projetos são afirmações textuais do prompt; este backend não contém implementações desses projetos nem um mecanismo local para verificá-las.

**FATO OBSERVADO:** não há consulta a documentos, embeddings, chunking, busca semântica, índice vetorial ou ferramenta de recuperação. Portanto, não há RAG implementado de forma comprovável. O README anterior chamava o contexto de “RAG”, mas o código atual mostra prompt estático mais histórico de sessão.

**LACUNA:** não há evidência neste workspace de dados recebidos de `mock.ts`; o arquivo não está versionado aqui.

## Provedor e modelo

**FATO OBSERVADO:** o chatbot usa `AsyncOpenAI` com `OPENAI_API_KEY` e chama `gpt-4o-mini`. A rota `/api/sugerir` é uma integração separada com Groq e não é o motor do chatbot principal.

## Segurança de conteúdo e erros

O filtro procura substrings como `hackear`, `cartão de crédito`, `ataque`, `vírus`, `bomba`, `derrubar sistema`, `gerar cpf`, `senha` e `dark web`, lançando `HTTPException(400)`.

Exceções gerais no processamento são registradas e substituídas por `Opa! Tive um problema técnico. Pode repetir?`, mantendo o `session_id` recebido no retorno do fallback. O endpoint também possui um `except` abrangente que retorna `500` com o texto da exceção.

**LACUNA:** não há timeout, retry, circuit breaker ou tratamento específico para falha da OpenAI. O comportamento exato quando o provedor devolve conteúdo nulo não é protegido no código.

## TTS

**FATO OBSERVADO:** `server.py` expõe `POST /api/tts`, e o serviço possui `get_voice_audio`. Porém a função registra que TTS está desativado na v1.0 e retorna `None`; nenhuma chamada ElevenLabs é feita no caminho atual. `ELEVEN_API_KEY` e `VOICE_ID` são lidos pelo serviço, mas não tornam a síntese funcional.

## Limitações

- Prompt grande e mantido diretamente no código.
- Conhecimento não é recuperado de fonte externa ou base vetorial.
- Não há autenticação, rate limiting ou controle de abuso específico no endpoint.
- O frontend consumidor não está disponível para confirmar o contrato de integração ponta a ponta.
