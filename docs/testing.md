# Testes e checks

## Arquivos disponíveis

Não há diretório de testes nem funções `test_*` no tree versionado. `test_mongo.py` é um script manual de conexão/listagem do MongoDB e `python test_env.py` verifica a presença de `OPENAI_API_KEY` no ambiente.

## Checks executados nesta auditoria

- `python -m compileall -q server.py chat_service.py models.py "python test_env.py" test_mongo.py`: passou.
- `python -m pytest --collect-only -q`: falhou durante a coleta porque `test_mongo.py` importa `pymongo`, que não está instalado no Python global; nenhum teste foi coletado.

Não foram executados testes de integração contra MongoDB, OpenAI, Groq, OpenWeather ou TTS, para evitar efeitos externos e porque esta tarefa é somente de auditoria/documentação.

## Lint, build e cobertura

Não há configuração versionada de lint, build ou cobertura. Não foi identificado comando oficial para essas etapas. A compilação de bytecode foi usada apenas como check de sintaxe.

## Lacunas

Não há testes automatizados para contratos HTTP, validação de sessões, filtro ético, persistência, tratamento de falhas dos provedores, CORS ou rotas de clima. A cobertura é não identificada.
