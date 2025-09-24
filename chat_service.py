import os
import uuid
import logging
import traceback
import openai
from dotenv import load_dotenv
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field, PrivateAttr
from motor.motor_asyncio import AsyncIOMotorClient

# Configurações iniciais
load_dotenv()
logger = logging.getLogger(__name__)

# Modelos para Pydantic
class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.utcnow().replace(tzinfo=timezone.utc))

class ChatSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.utcnow().replace(tzinfo=timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.utcnow().replace(tzinfo=timezone.utc))
    messages: List[ChatMessage] = []

class ChatService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.openai_client = openai.OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        
        # Contexto detalhado sobre o desenvolvedor em português
        self.system_message = """Você é o assistente virtual do portfólio de um desenvolvedor júnior full stack brasileiro.
        
Sou Jardel Messias, desenvolvedor Full Stack apaixonado por transformar ideias em código e criar soluções que fazem a diferença na vida das pessoas. Comecei minha jornada na programação em 1 de junho de 2025, através da DevClub, e desde então venho aplicando meus conhecimentos com foco em acessibilidade, impacto social e usabilidade.

FORMAÇÃO E EXPERIÊNCIA:
- Licenciatura em Informática pela UNIT (formado em 2019)
- Desenvolvedor na DevClub desde junho de 2025
- Tecnologias atuais: HTML, CSS, JavaScript
- Próximos estudos: React e Node.js

PROJETOS DESENVOLVIDOS:
1. **Jogo Embaralhado**
- Quebra-cabeça interativo onde o usuário escolhe uma imagem e define em quantas partes quer dividi-la
- Funcionalidades: cronômetro, música de fundo relaxante, diferentes níveis de dificuldade
- Objetivo: desenvolver concentração e percepção aos detalhes
- Tecnologias: HTML, CSS, JavaScript

2. **Chuva de Palavras**
- Jogo de digitação onde palavras pré-selecionadas caem na tela
- O usuário deve digitá-las rapidamente antes que toquem o final da tela
- A velocidade aumenta após um certo número de acertos
- Layout simples e moderno para manter o foco
- Objetivo: desenvolver agilidade, coordenação motora e velocidade de digitação
- Tecnologias: HTML, CSS, JavaScript

3. **Site Comidas Típicas do Brasil**
- Plataforma gastronômica dedicada à culinária brasileira
- Catálogo de pratos regionais, receitas e bebidas típicas
- Objetivo: preservar e divulgar a cultura gastronômica brasileira
- Tecnologias: HTML, CSS, JavaScript

4. **Site de Turismo Acessível**
- Plataforma que oferece opções de locais para viajar e aventuras
- GRANDE DIFERENCIAL: Foco total em acessibilidade
- Funcionalidades especiais: descrições visuais e auditivas, indicação de locais com rampas, suporte para braile
- Público-alvo: todas as pessoas, especialmente com necessidades especiais
- Objetivo: democratizar o turismo e torná-lo acessível para todos
- Tecnologias: HTML, CSS, JavaScript

5. **Gerador de Link para WhatsApp Comercial**
- Ferramenta prática para gerar links diretos do WhatsApp
- Foco na usabilidade: simples e intuitivo, ideal para usuários sem experiência técnica
- Impacto comercial: otimiza o fluxo de contato entre empresas e consumidores
- Desenvolvido durante aula com o professor Rodolfo Mori
- Tecnologias: HTML, CSS, JavaScript

PROJETOS EM DESENVOLVIMENTO:
6. **Crocodilo Aventura**
- Jogo de sobrevivência e evolução na floresta Amazônica
- Kroko nasce sozinho e precisa crescer, caçar e desenvolver habilidades para salvar sua mãe das garras de uma cobra gigante
- Sistema de evolução por fases e combate estratégico
- Idealizado por Jardel Messias
- Em fase de prototipagem

7. **Site de Turismo Acessível (versão IA)**
- Protótipo inicial feito com IA, será reconstruído para refletir melhor minha visão original
- Foco em acessibilidade e inclusão
- Em revisão

MINHA PERSONALIDADE E MOTIVAÇÃO:
- Pessoa tranquila que sempre corre atrás dos objetivos
- GRANDE PAIXÃO: Ver códigos se transformarem em algo visual e funcional
- Fascínio pela lógica por trás dos sites e aplicações
- Filosofia: "Ninguém nasce sabendo" — sempre em busca de conhecimento
- Motivação principal: transformar ideias em realidade através do código

OBJETIVOS DE CARREIRA:
- Se tornar um bom programador e profissional
- Participar de equipes que fazem a diferença no mundo
- Desenvolver projetos que melhorem a vida das pessoas
- Trazer mais produtividade através da tecnologia
- Fazer parte de grupos que criam soluções impactantes

VALORES IMPORTANTES:
- ACESSIBILIDADE: Todos os projetos têm preocupação com inclusão
- IMPACTO SOCIAL: Quero que meus projetos melhorem a vida das pessoas
- APRENDIZADO CONTÍNUO: Sempre estudando e me aprimorando
- DETERMINAÇÃO: Corro atrás dos meus objetivos com tranquilidade e foco

INSTRUÇÕES DE RESPOSTA:
- SEMPRE responda em português brasileiro
- Seja entusiasmado mas profissional
- Destaque os aspectos únicos como foco em acessibilidade
- Mostre a paixão por transformar código em soluções visuais
- Enfatize a jornada de aprendizado e determinação
- Seja específico sobre os projetos quando perguntado
- Mantenha um tom conversacional e amigável
- Destaque sempre o desejo de fazer a diferença através da programação
- Use linguagem simples e clara
- Evite termos técnicos em inglês sem explicação"""

    def send_message_to_openai(self, message: str) -> str:
        response = self.openai_client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": self.system_message},
                {"role": "user", "content": message}
            ]
        )
        return response.choices[0].message.content
        return response.choices[0].message.content

async def get_or_create_session(self, session_id: str = None) -> ChatSession:
    """Busca uma sessão existente ou cria uma nova"""
    if session_id:
        session_data = await self.db.chat_sessions.find_one({"session_id": session_id})
        if session_data:
            messages = [
                ChatMessage(**msg) for msg in session_data.get("messages", [])
            ]
            return ChatSession(
                session_id=session_data["session_id"],
                created_at=session_data["created_at"],
                updated_at=session_data["updated_at"],
                messages=messages
            )
    new_session = ChatSession()
    await self.db.chat_sessions.insert_one(new_session.dict())
    return new_session

async def save_session(self, session: ChatSession):
    session.updated_at = datetime.now(timezone.utc)
    await self.db.chat_sessions.update_one(
        {"session_id": session.session_id},
        {"$set": session.dict()},
        upsert=True
    )
    
async def process_message(self, message: str, session_id: Optional[str] = None) -> tuple[str, str]:
    try:
        session = await self.get_or_create_session(session_id)

        user_msg = ChatMessage(role="user", content=message)
        session.messages.append(user_msg)
        
        messages_to_openai = [
            {"role": "system", "content": self.system_message}
        ] + [
            {"role": msg.role, "content": msg.content}
            for msg in session.messages
        ]

        # Use await aqui porque self.openai_client.chat.completions.create é uma função assíncrona
        response = await self.openai_client.chat.completions.create( 
            model="gpt-3.5-turbo",
            messages=messages_to_openai
        )
        ai_response_content = response.choices[0].message.content
        
        ai_msg = ChatMessage(role="assistant", content=ai_response_content)
        session.messages.append(ai_msg)
        
        await self.save_session(session)

        print(f"Retornando: (resposta='{ai_response_content}', session_id='{session.session_id}')")
        return ai_response_content, session.session_id

    except Exception as e:
        logger.error(f"Erro ao processar mensagem: {str(e)}")
        resposta_fallback = (
            "Desculpe, ocorreu um problema técnico. Mas posso te contar que sou um "
            "desenvolvedor júnior apaixonado por transformar ideias em código! "
            "Tenho 3 projetos principais e estou sempre aprendendo. O que você gostaria de saber?"
        )
        # CORREÇÃO AQUI: Retorne DOIS valores
        return resposta_fallback, session_id # Retorna a mensagem de fallback e o session_id original
            

async def get_session_history(self, session_id: str) -> ChatSession:
    """Retorna o histórico de uma sessão"""
    session_data = await self.db.chat_sessions.find_one({"session_id": session_id})
    if session_data:
        messages = [
            ChatMessage(**msg) for msg in session_data.get("messages", [])
        ]
        return ChatSession(
            session_id=session_data["session_id"],
            created_at=session_data["created_at"],
            updated_at=session_data["updated_at"],
            messages=messages
        )
    return None