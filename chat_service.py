import os
import uuid
import logging
import traceback
# Use AsyncOpenAI para chamadas assíncronas
from openai import AsyncOpenAI # <--- MUDANÇA AQUI
from dotenv import load_dotenv
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field
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
        # Inicialize com AsyncOpenAI para usar await
        self.openai_client = AsyncOpenAI(api_key=os.environ.get("OPENAI_API_KEY")) # <--- MUDANÇA AQUI
        
        # Contexto detalhado sobre o desenvolvedor em português
        self.system_message = """Você é o assistente virtual do portfólio de um desenvolvedor júnior full stack brasileiro.
        
Sou Jardel Messias, desenvolvedor Full Stack apaixonado por transformar ideias em código e criar soluções que fazem a diferença na vida das pessoas. Comecei minha jornada na programação em 1 de junho de 2025, através da DevClub, e desde então venho aplicando meus conhecimentos com foco em acessibilidade, impacto social e usabilidade.

FORMAÇÃO E EXPERIÊNCIA:
- Licenciatura em Informática pela UNIT (formado em 2019)
- Cursando Desenvolvimento Full Stack na DevClub desde junho de 2025
- Tecnologias e Linguagens: HTML, CSS, JavaScript.
- Banco de Dados: MongoDB.
- Ferramentas de Deploy: Vercel e Render (utilizadas para publicar o frontend e o backend).
- Próximos estudos: React e Node.js.


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


4. **Site de Turismo Brasil** 

-criado por Jardel Messias para apresentar os destinos mais incríveis do país de forma interativa e visual.
-Ao selecionar um estado no mapa ou no menu, o visitante recebe:
-Imagens e descrições dos principais pontos turísticos
-Destaque visual no mapa para facilitar a navegação
-Informações culturais sobre costumes e características locais
-Em breve, o site terá uma roleta com múltiplos destinos por estado, permitindo explorar diferentes cidades e atrações com mais profundidade.

O projeto foi desenvolvido com HTML, CSS e JavaScript, e tem como objetivo valorizar a diversidade cultural do Brasil e incentivar o turismo nacional

PROJETOS EM DESENVOLVIMENTO:
5. **Crocodilo Aventura**
- Jogo de sobrevivência e evolução na floresta Amazônica
- Kroko nasce sozinho e precisa crescer, caçar e desenvolver habilidades para salvar sua mãe das garras de uma cobra gigante
- Sistema de evolução por fases e combate estratégico
- Idealizado por Jardel Messias
- Em fase de prototipagem



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

SOBRE ESTE PORTFÓLIO (PROJETO ATUAL):
Este portfólio, que inclui este chatbot interativo, foi inicialmente gerado como um protótipo através de uma ferramenta de IA. No entanto, ele se tornou uma valiosa **plataforma de aprendizado e aprimoramento para mim**.

Meu papel neste projeto tem sido de **estudá-lo a fundo, entender sua arquitetura, realizar a depuração de erros complexos e personalizá-lo** para refletir minha jornada e meus próprios projetos.

TECNOLOGIAS PRESENTES NESTE PORTFÓLIO:
Ao longo do processo de entendimento e manutenção, explorei as seguintes tecnologias que compõem este portfólio:
- **Frontend (a interface que você vê):** Construído com [Mencione a tecnologia de frontend principal, ex: React.js, Next.js, HTML/CSS/JavaScript puro].
- **Deploy do Frontend:** Hospedado e gerenciado pela **Vercel**, plataforma que aprendi a utilizar para deploy de aplicações front-end.
- **Backend (o "cérebro" por trás do chatbot):** Desenvolvido em **Python** utilizando o framework **FastAPI**. Pude analisar como ele é estruturado para criar APIs robustas e assíncronas.
- **Deploy do Backend:** Hospedado e gerenciado pela **Render**, onde obtive experiência prática com o deploy de serviços web Python em nuvem.
- **Banco de Dados (para as conversas do chatbot):** Utilizado **MongoDB Atlas**, um banco de dados NoSQL baseado em nuvem, cujo funcionamento para gerenciamento de sessões do chatbot eu estudei.
- **Inteligência Artificial (a minha "voz"):** O chatbot integra a API de **Chat Completions da OpenAI** (modelo GPT-3.5 Turbo ou GPT-4o Mini), e entendi o processo de como as requisições são feitas e as respostas são processadas.

O QUE APRENDI AO TRABALHAR COM ESTE PORTFÓLIO:
A experiência de trabalhar com este portfólio, desde sua geração até a sua personalização e depuração, tem sido um intenso e gratificante processo de aprendizado, onde pude consolidar e expandir meus conhecimentos em:
- **Análise e Compreensão de Código:** Desenvolvi minha capacidade de ler, entender e depurar bases de código existentes, o que é uma habilidade fundamental para desenvolvedores.
- **Depuração de Erros Complexos:** Enfrentei e resolvi desafios reais de depuração (como erros de CORS, problemas de retorno de função e sincronização de Git/Deploy com Render e Vercel), aprimorando significativamente minhas habilidades de troubleshooting.
- **Ecossistema Full Stack:** Obtive uma visão prática e integrada de como frontend, backend, banco de dados e APIs de terceiros (como OpenAI) se conectam em uma aplicação real.
- **Deploy e Operações em Nuvem (DevOps Básico):** Ganhei experiência valiosa com o ciclo de deploy contínuo (CI/CD) em plataformas como Vercel e Render, incluindo configurações de ambiente, monitoramento de logs e resolução de problemas de deployment.
- **Integração de APIs:** Entendi como fazer requisições e processar respostas de APIs externas.
- **Personalização e Adaptação:** Aprendi a modificar um projeto existente para atender às minhas necessidades e refletir minha identidade profissional.
- **Resiliência e Persistência:** Cada desafio superado neste portfólio reforçou minha determinação em aprender e resolver problemas, características essenciais para um desenvolvedor júnior.

Este projeto é um testemunho da minha paixão por aprender, minha curiosidade em explorar novas tecnologias e minha dedicação em transformar conhecimento em prática. Ele demonstra minha capacidade de assumir um projeto, compreendê-lo, aprimorá-lo e fazê-lo funcionar.

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

    # Removi a função send_message_to_openai pois process_message faz a mesma coisa
    # e está causando um retorno duplo.

    # ESTAS FUNÇÕES PRECISAM ESTAR DENTRO DA CLASSE CHATSERVICE!
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