# Integrações

## MongoDB

Integração assíncrona via Motor/PyMongo para sessões, conversas e status. URI e banco são obtidos por `MONGO_URL` e `DB_NAME`.

## OpenAI

Integração principal do chatbot via `AsyncOpenAI`, autenticada por `OPENAI_API_KEY`, com o modelo `gpt-4o-mini`.

## Groq

A rota `POST /api/sugerir` chama a API compatível com OpenAI em `https://api.groq.com/openai/v1/chat/completions`, usando `GROQ_KEY` e o modelo `llama-3.3-70b-versatile`. Essa integração é independente do fluxo principal do chatbot.

## OpenWeather

As rotas `GET /api/clima` e `GET /api/previsao` acessam a API OpenWeather com `OPENWEATHER_KEY`. A primeira busca o clima atual por cidade; a segunda busca previsão por latitude e longitude.

## ElevenLabs / TTS

Há variáveis `ELEVEN_API_KEY` e `VOICE_ID` e referências históricas no Git, mas a implementação atual de `get_voice_audio` retorna `None` sem realizar chamada externa. TTS funcional não é comprovado no estado atual.

## Frontend

O backend expõe JSON e áudio potencial em `/api`, mas não há frontend neste workspace. O README anterior menciona React/Vite e Web Speech API, porém isso é informação não comprovada pelos arquivos atuais.

## Render, CI/CD e outros provedores

Não há arquivo de configuração Render, Dockerfile, workflow de CI/CD ou configuração de outro provedor no tree versionado atual. Um commit histórico chamado `Deploy final: Backend e Frontend conectados` existe, mas seu título não comprova a configuração presente.
