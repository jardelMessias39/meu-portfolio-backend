# Deploy e execução

## Execução local observada

O README versionado orienta iniciar com:

```text
uvicorn server:app --host 127.0.0.1 --port 8000 --reload
```

Também registra a alternativa `python -m uvicorn server:app --host 127.0.0.1 --port 8000 --reload` e a documentação em `/docs`. O comando de inicialização de produção não está versionado.

## Configuração

`python-dotenv` carrega `.env` na inicialização. O arquivo `.env` é ignorado pelo Git. O exemplo versionado contém placeholders para `MONGO_URL`, `DB_NAME` e `BACKEND_URL`; o código também usa `OPENAI_API_KEY`, `CORS_ORIGINS`, `OPENWEATHER_KEY`, `GROQ_KEY`, `ELEVEN_API_KEY` e `VOICE_ID` em diferentes caminhos.

## Porta e host

A porta `8000` e o host `127.0.0.1` são comprovados apenas pelo comando documentado para desenvolvimento local. Não há evidência versionada de porta, host ou health check configurados em um provedor externo.

## CORS

O backend usa `CORS_ORIGINS`, separado por vírgulas, com fallback `*`; permite credenciais, métodos e headers. A configuração externa de produção não está versionada.

## Render, build e deploy

Não há `render.yaml`, Dockerfile, Procfile, workflow ou pipeline CI/CD no tree atual. O projeto não possui etapa de build identificada; é uma aplicação Python executada pelo Uvicorn. Deploy atual, domínio e URL pública são não identificados.

## Limites da documentação

O Git contém um commit histórico com mensagem relacionada a deploy, mas não contém os artefatos necessários para reconstruir ou validar esse deploy. Portanto, qualquer configuração de provedor deve ser consultada fora deste repositório.
