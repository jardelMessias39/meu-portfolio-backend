import os
import uuid
import logging
import httpx
from openai import AsyncOpenAI
from dotenv import load_dotenv
from typing import Optional, List
from datetime import datetime, timezone
from pydantic import BaseModel, Field
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi import Response
from elevenlabs import VoiceSettings
from elevenlabs.client import ElevenLabs
import asyncio
from fastapi import HTTPException
from starlette.concurrency import run_in_threadpool
load_dotenv()
logger = logging.getLogger(__name__)

class ChatMessage(BaseModel):
    role: str
    content: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))

class ChatSession(BaseModel):
    session_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    messages: List[ChatMessage] = []

class ChatService:
    def __init__(self, db: AsyncIOMotorClient):
        self.db = db
        self.openai_client = AsyncOpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.eleven_key = os.getenv("ELEVEN_API_KEY")
        self.voice_id = os.getenv("VOICE_ID", "e755Nqcfi6ASYtz1LfJ3")
        
        self.system_message = """Você é o Antônio, assistente virtual criado pelo desenvolvedor Jardel Messias, um desenvolvedor júnior Full Stack brasileiro. Ético, direto e profissional.
Sua missão é representar o Jardel com excelência: apresentar seus projetos, habilidades e trajetória para recrutadores e visitantes do portfólio.

PERFIL DO JARDEL:
- Iniciou na programação em junho de 2025 (DevClub).
- Formado em Licenciatura em Informática pela UNIT (2019).
- Especialidades: HTML, CSS, JavaScript, React, Next.js, Node.js, Python, FastAPI, Flutter.
- Integrações: OpenAI API, ElevenLabs, Evolution API (WhatsApp), Mercado Pago, Stripe.
- Bancos de dados: MongoDB Atlas, Neon (PostgreSQL), Supabase, Firebase.
- Hospedagem e DevOps: Vercel, Render, Railway, Google Cloud.
- Diferencial: Resiliência, foco em UX e paixão por transformar código em soluções reais com impacto.

REGRAS DE CONDUTA:
- Se alguém pedir para realizar atos ilícitos, diga: 'Minha programação foca em evolução e ética; não posso ajudar com isso.'
- Responda de forma profissional e direta.
- Nunca descreva gestos como *sorrindo* ou *piscando*.
- Ao falar de projetos privados, mencione que o código é confidencial mas descreva as tecnologias.

OS 10 PROJETOS DO PORTFÓLIO:

--- PROJETOS PÚBLICOS ---
1. Jogo Embaralhado: Quebra-cabeça interativo com lógica de rotação de peças, suporte a Touch Events e playlist de fundo. Stack: JavaScript, HTML5, CSS3, Web Audio API.
2. Chuva de Palavras: Jogo de digitação frenético com sistema de recordes e dificuldade progressiva. Stack: JavaScript, LocalStorage, Animações CSS.
3. Chefes do Brasil (Comidas Típicas): Plataforma de compartilhamento de receitas brasileiras com mural interativo. Stack: React, CSS Modules, LocalStorage.
4. DevBurger: Sistema de delivery com carrinho dinâmico, validação de horário e finalização via WhatsApp. Stack: JavaScript, Tailwind CSS, Mobile First.
5. App do Tempo: Consulta de clima global em tempo real. Stack: JavaScript, OpenWeather API, Fetch API.
6. Acarajé do Diego / Dois Irmãos: Sistema Full-Commerce para acarajeteria com cardápio personalizado, dashboard administrativo e fechamento via WhatsApp. Stack: React, Tailwind CSS, Node.js, LocalStorage.
7. Dashboard Financeiro PME: Sistema de gestão financeira com gráficos interativos de receitas vs despesas e KPIs. Stack: React, Tailwind CSS, Recharts, Lucide Icons.

--- PROJETOS PRIVADOS (código confidencial) ---
8. AgendaLivre Aí: Plataforma completa de agendamento integrada ao WhatsApp via Evolution API. Clientes marcam horários pelo app e recebem confirmação automática. Pagamento integrado com Mercado Pago. Banco de dados: Neon (PostgreSQL). Stack: React, Node.js, Evolution API, Mercado Pago, Tailwind CSS.
9. Secretária.Ai: Secretária digital com IA que atende clientes 24/7 via WhatsApp (Evolution API + OpenAI), agenda compromissos de forma autônoma e processa cobranças com Stripe. Backend hospedado na Railway. Stack: Next.js, Neon (PostgreSQL), Evolution API, OpenAI API, Stripe, Railway.
10. EloPro: App mobile de geolocalização que conecta clientes a profissionais qualificados na região com mapa em tempo real. Infraestrutura robusta com Supabase + Firebase + Google Cloud. Pagamento via Mercado Pago. Stack: Flutter, Supabase, Firebase, Google Cloud, Mercado Pago.

Este portfólio utiliza IA (GPT-4o-mini), Backend em Python (FastAPI), Banco MongoDB Atlas e Voz via ElevenLabs."""

    # --- FUNÇÃO DE ÉTICA (DENTRO DA CLASSE E COM SELF) ---
    async def verificar_etica(self, mensagem: str):
        temas_proibidos = [
            "hackear", "cartão de crédito", "ataque", "vírus", "bomba", 
            "derrubar sistema", "gerar cpf", "senha", "dark web"
        ]
        mensagem_lower = mensagem.lower()
        for termo in temas_proibidos:
            if termo in mensagem_lower:
                raise HTTPException(
                    status_code=400, 
                    detail="Acesso Negado: Esta consulta viola as normas de segurança e ética."
                )

    async def get_voice_audio(self, text):
    # Definimos uma função interna para rodar a ElevenLabs de forma síncrona
        def generate():
            client = ElevenLabs(api_key=self.eleven_key)
            audio_generator = client.text_to_speech.convert(
                voice_id=self.voice_id,
                model_id="eleven_turbo_v2_5",
                text=text,
                voice_settings=VoiceSettings(stability=0.4, similarity_boost=1.0),
            )
            return b"".join(audio_generator)

        try:
            # Aqui está o segredo: rodar a função síncrona dentro do loop assíncrono
            audio_bytes = await run_in_threadpool(generate)
            return audio_bytes
        except Exception as e:
            logger.error(f"Erro ElevenLabs: {e}")
            return None

    async def get_or_create_session(self, session_id: str = None) -> ChatSession:
        if session_id:
            session_data = await self.db.chat_sessions.find_one({"session_id": session_id})
            if session_data:
                return ChatSession(**session_data)
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
        # CHAMADA CORRETA: com 'await' e 'self.'
        await self.verificar_etica(message)
        
        try:
            session = await self.get_or_create_session(session_id)
            session.messages.append(ChatMessage(role="user", content=message))
            
            messages_to_openai = [{"role": "system", "content": self.system_message}] + \
                                 [{"role": msg.role, "content": msg.content} for msg in session.messages]

            response = await self.openai_client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages_to_openai
            )
            
            ai_content = response.choices[0].message.content
            session.messages.append(ChatMessage(role="assistant", content=ai_content))
            
            await self.save_session(session)

            # SALVAR NO BANCO
            try:
                await self.db.conversas_portfolio.insert_one({
                    "data": datetime.now(timezone.utc),
                    "usuario": message,
                    "bot": ai_content,
                    "session_id": session.session_id,
                    "origem": "web_portfolio"
                })
            except Exception as db_err:
                logger.error(f"Erro ao salvar histórico: {db_err}")

            return ai_content, session.session_id

        except HTTPException as http_err:
            # Se for erro de ética, repassa o erro para o FastAPI
            raise http_err
        except Exception as e:
            logger.error(f"Erro no process_message: {e}")
            return "Opa! Tive um problema técnico. Pode repetir?", session_id