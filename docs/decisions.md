# Decisões observáveis

Este documento registra escolhas que podem ser deduzidas diretamente do estado atual do código. Não substitui um ADR formal.

## FastAPI com router `/api`

A aplicação usa FastAPI e concentra as rotas em um `APIRouter` com prefixo `/api`.

## MongoDB assíncrono

O servidor cria `AsyncIOMotorClient` e o serviço usa operações assíncronas para sessões, conversas e status.

## Contexto fixo no prompt

O conhecimento do consultor digital é mantido como uma string `system_message` no serviço. Não há evidência de um repositório de documentos ou recuperação vetorial.

## Janela de histórico

O serviço mantém a sessão completa em `chat_sessions`, mas limita a janela enviada ao modelo às últimas 20 mensagens.

## Persistência duplicada do chatbot

A sessão completa é salva em `chat_sessions`, enquanto cada troca também é registrada em `conversas_portfolio` com campos resumidos.

## TTS desativado

O endpoint foi mantido, mas `get_voice_audio` retorna `None` e registra que a voz está desativada na v1.0.

## Lacuna de formalização

Não há arquivos ADR, diagramas versionados, contrato OpenAPI exportado, política de retenção, decisão formal de autenticação ou configuração de deploy versionada. As razões dessas escolhas não podem ser comprovadas pelo workspace.
