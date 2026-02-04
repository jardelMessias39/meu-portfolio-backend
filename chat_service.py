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

load_dotenv()
logger = logging.getLogger(__name__)
  # 1. TRAVAS DE SEGURANÇA (A tua lista de bloqueio)
TEMAS_BLOQUEADOS = [
    "hackear", "cartão de crédito", "ataque", "vírus", "bomba", 
    "derrubar sistema", "gerar cpf", "senha", "dark web"
]

def verificar_etica(mensagem: str):
    mensagem_lower = mensagem.lower()
    for termo in TEMAS_BLOQUEADOS:
        if termo in mensagem_lower:
            # Isso interrompe o código aqui mesmo e avisa o usuário
            raise HTTPException(
                status_code=400, 
                detail="Acesso Negado: Esta consulta viola as normas de segurança e ética do sistema."
            )

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
        # Agora ele vai pegar a chave que você salvou no painel do Render!
        self.eleven_key = os.getenv("ELEVEN_API_KEY")
        self.voice_id = os.getenv("VOICE_ID", "TX3LPaxmHKxFdv7VOQHJ")
        
        # TUDO DENTRO DA VARIÁVEL SYSTEM_MESSAGE
        self.system_message = """Você é o assistente virtual, criado pelo desenvolvedor Jardel Messias, um desenvolvedor júnior Full Stack brasileiro.ético e profissional.
Sua missão é ajudar com tecnologia, programação (React, FastAPI, Python) e marketing digital.

PERFIL DO JARDEL:
- Iniciou na programação em junho de 2025 (DevClub).
- Formado em Licenciatura em Informática pela UNIT (2019).
- Especialidades: HTML, CSS, JavaScript, React, Node.js e MongoDB.
- Diferencial: Resiliência, foco em UX e paixão por transformar código em soluções reais.

REGRAS DE CONDUTA:
- Se alguém pedir para realizar atos ilícitos, diga: 'Minha programação foca em evolução e ética; não posso ajudar com isso.'
- Responda de forma profissional e direta.
- Nunca descreva gestos.
- Nunca diga 'sorrindo', 'piscando' ou 'fazendo gestos'.

OS 6 PROJETOS PRINCIPAIS:
1. Jogo Embaralhado: Quebra-cabeça com lógica de rotação (90°/180°), Touch Events e Web Audio API. Foco total em Mobile UX.
2. Chuva de Palavras: Jogo de digitação com requestAnimationFrame e persistência de Recordes no LocalStorage.
3. Acarajé do Diego (Dois Irmãos): Sistema Full-Commerce com cardápio dinâmico, escolha de recheios e fechamento via WhatsApp. Inclui Dashboard Administrativo.
4. Dashboard Financeiro PME: Aplicação analítica para gestão de empresas, com gráficos interativos e fluxo de caixa.
5. DevBurger: Sistema de delivery com carrinho dinâmico e fluxo de pedido otimizado.
6. App do Tempo: Integração com APIs externas de meteorologia para consulta climática global.

Este portfólio utiliza IA (GPT-4), Backend em Python (FastAPI) no Render, Banco MongoDB Atlas e Voz via ElevenLabs.

INSTRUÇÕES:
- Responda sempre em Português Brasileiro de forma entusiasmada e profissional.
- Seja breve e direto para poupar créditos de áudio.
- Nunca descreva gestos como *sorrindo*, *piscando*. Apenas o texto para ser falado.
- Se não souber algo, use o fallback profissional."""

    def get_voice_audio(self, text):
        client = ElevenLabs(self.eleven_key)
        try:
            # Sua chamada atual da ElevenLabs que está dando erro 401
            audio_generator = client.text_to_speech.convert(
                voice_id=self.voice_id,
                model_id="eleven_turbo_v2_5",
                text=text,
                voice_settings=VoiceSettings(stability=0.4, similarity_boost=1.0),
            )
            return b"".join(audio_generator)
        except Exception as e:
            print(f"Erro ElevenLabs: {e}")
            return None  # Retorna None em vez de quebrar o servidor!

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
        verificar_etica(message)
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
            return ai_content, session.session_id
        except Exception as e:
            logger.error(f"Erro no process_message: {e}")
            return "Opa! Tive um problema técnico. Pode repetir?", session_id
        
      
        # 3. SALVAR HISTÓRICO NO BANCO (Mágica aqui!)
        try:
            # Criamos uma coleção chamada 'conversas_portfolio'
            await db.conversas_portfolio.insert_one({
                "data": datetime.now(),
                "usuario": message,
                "bot": resposta,
                "session_id": nova_session_id,
                "origem": "web_portfolio"
            })
        except Exception as db_err:
            logger.error(f"Erro ao salvar no banco: {db_err}")
            return "Opa! Tive um problema técnico. Pode repetir?", session_id