from fastapi import FastAPI, APIRouter, HTTPException, Request, Body, Response
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from dotenv import load_dotenv
import os
import logging
import traceback
from datetime import datetime
from pathlib import Path
from contextlib import asynccontextmanager
from models import StatusCheck, StatusCheckCreate, ChatRequest, ChatResponse
from chat_service import ChatService
from typing import List

# Configurações iniciais
ROOT_DIR = Path(__file__).parent
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Conexão MongoDB
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Inicializa chat service
chat_service = ChatService(db)

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔄 Conectando ao MongoDB...")
    yield
    logger.info("🛑 Encerrando conexão com MongoDB...")
    client.close()

app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")

# Configuração de CORS (Liberado para facilitar no portfólio)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ROTAS ---

@api_router.get("/")
async def root():
    return {"message": "API do portfólio rodando!"}

@api_router.post("/tts")
async def get_audio(payload: dict):
    texto = payload.get("text")
    if not texto:
        return JSONResponse(content={"error": "Sem texto"}, status_code=400)

    # Nota: Lembre-se de adicionar 'self' no chat_service.py se necessário
    audio_content = await chat_service.get_voice_audio(texto)

    if audio_content:
        return Response(
            content=audio_content, 
            media_type="audio/mpeg"
        )
    return JSONResponse(content={"error": "Falha no áudio"}, status_code=500)

@api_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        session_id = data.get("session_id")

        if not message:
            raise HTTPException(status_code=400, detail="Mensagem vazia")

        # 🚀 AQUI ENTRA A TRAVA ÉTICA (Chama a função que você colocou no final do chat_service)
        await chat_service.verificar_etica(message) 

        # 1. Processa a mensagem com a IA (Só chega aqui se for ético!)
        resposta, nova_session_id = await chat_service.process_message(
            message=message,
            session_id=session_id
        )

        # 2. SALVAR HISTÓRICO NO BANCO (Mágica aqui!)
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

        return ChatResponse(response=resposta, session_id=nova_session_id)

    except Exception as e:
        logger.error(f"🔥 ERRO NO CHAT: {traceback.format_exc()}")
        return JSONResponse(
            status_code=500,
            content={"detail": f"Erro interno: {str(e)}"}
        )

# Outras rotas (Status)
@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    await db.status_checks.insert_one(status_obj.dict())
    return status_obj

# Inclusão do Router e Inicialização
app.include_router(api_router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)