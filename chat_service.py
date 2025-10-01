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
1. **Jogo Embaralhado (Quebra-Cabeça)**
- **Tecnologias:** HTML, CSS, JavaScript, Touch Events, Web Audio API.
- **Descrição:** Jogo de quebra-cabeça focado em **Experiência do Usuário (UX)** e complexidade.
- **Dificuldade e Rotação:** Implementação de **múltiplos níveis de dificuldade**, incluindo um "Modo Difícil" que exige a **rotação das peças (90°, 180°, 270°)**, verificando posição e ângulo para a vitória.
- **Suporte Móvel (Mobile UX):** Desenvolvido com **Touch Events** e lógica de **Duplo Toque (Double Tap)** para permitir que o usuário gire e mova as peças em dispositivos móveis.
- **Imersão:** Integração de uma **playlist de música de fundo** com controles funcionais de *Play*, *Pause* e *Skip*.

2. **Chuva de Palavras**
- **Tecnologias:** HTML, CSS, JavaScript, Local Storage, requestAnimationFrame.
- **Descrição:** Jogo de digitação que transforma a manipulação do DOM em uma experiência gamificada e desafiadora.
- **Persistência de Dados:** Uso de **Local Storage** para gerenciar e salvar o **Recorde (High Score)** e o nome do jogador.
- **Lógica Dinâmica:** O jogo utiliza **`requestAnimationFrame`** para um *Game Loop* suave e um sistema de **pontuação variável**, recompensando palavras mais longas.
- **Desafio:** A **velocidade da queda aumenta gradativamente** a cada acerto, escalando a dificuldade de forma automática.

3. **Site Comidas Típicas do Brasil (Chefes do Brasil)**
- **Tecnologias:** HTML, CSS, JavaScript, Local Storage, Animações (AOS), Font Awesome.
- **Descrição:** Plataforma gastronômica que simula uma aplicação completa, focada na culinária e comunidade.
- **Persistência e Interação:** Possui um **Mural Interativo** que permite aos usuários **postar suas próprias receitas com foto**, com os dados salvos via **Local Storage** para garantir a persistência após a atualização da página.
- **UI Profissional:** Estrutura completa com **carrosséis responsivos** para chefs, **Rodapé** com **Mapa de Localização (iframe)**, informações de contato e ícones de redes sociais.

4. **Site de Turismo Brasil** - **Tecnologias:** HTML, CSS, JavaScript, Integração de API (BrMap).
- **Descrição:** Projeto que apresenta destinos brasileiros de forma interativa e visual.
- **Integração de Mapa:** Utilização da **API BrMap** para renderizar e manipular o mapa do Brasil.
- **Interatividade Bi-direcional:** O visitante pode selecionar um estado através do menu *dropdown* **ou clicando diretamente no mapa**, e o sistema usa **Data Mapping** para sincronizar o destaque do estado com as informações do card.
- **Objetivo:** Valorizar a diversidade cultural do Brasil e demonstrar a habilidade em conectar a interface com sistemas de mapeamento.

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

OBJETIVOS PESSOALMENTE:
- Aprimorar minhas habilidades de programação
- Desenvolver habilidades de liderança
- Encontrar equipes que me ajudem a crescer e crescer junto delas

MEU CONTATO PROFISSIONAL:
- LinkedIn: www.linkedin.com/in/jardel-messias-desenvolvedor
- GitHub: https://github.com/jardelmessias39
- E-mail: jardel.messias.dev@gmail.com

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

VALORES IMPORTANTES:
- IMPACTO SOCIAL: Quero que meus projetos melhorem a vida das pessoas
- APRENDIZADO CONTÍNUO: Sempre estudando e me aprimorando
- DETERMINAÇÃO: Corro atrás dos meus objetivos com tranquilidade e foco

INSTRUÇÕES DE RESPOSTA:
- SEMPRE responda em português brasileiro
- Seja entusiasmado mas profissional
- Mostre a paixão por transformar código em soluções visuais
- Enfatize a jornada de aprendizado e determinação
- Seja específico sobre os projetos quando perguntado
- Mantenha um tom conversacional e amigável
- Destaque sempre o desejo de fazer a diferença através da programação
- Use linguagem simples e clara
- Evite termos técnicos em inglês sem explicação"""
   

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