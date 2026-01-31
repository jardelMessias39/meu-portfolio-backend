from fastapi import FastAPI, APIRouter, HTTPException, Request, Body
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient
import os
import logging
from pathlib import Path
from contextlib import asynccontextmanager
from models import StatusCheck, StatusCheckCreate, ChatRequest, ChatResponse
from chat_service import ChatService
import traceback
from typing import List
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from fastapi import Response

ROOT_DIR = Path(__file__).parent
load_dotenv()
print("MONGO_URL:", os.getenv("MONGO_URL"))
print("DB_NAME:", os.getenv("DB_NAME"))
print("OPENAI_API_KEY:", os.getenv("OPENAI_API_KEY"))


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# MongoDB connection
mongo_url = os.environ['MONGO_URL']
client = AsyncIOMotorClient(mongo_url)
db = client[os.environ['DB_NAME']]

# Initialize chat service
chat_service = ChatService(db)

# Lifespan manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("🔄 Conectando ao MongoDB...")
    yield
    logger.info("🛑 Encerrando conexão com MongoDB...")
    client.close()

# Create app and router
app = FastAPI(lifespan=lifespan)
api_router = APIRouter(prefix="/api")
# 1. Primeiro: Inclua o router no APP


# Pega a URL do Render (Environment Variables) ou usa o seu domínio oficial
frontend_url = os.environ.get("FRONTEND_URL", "meu-portfolio-jardel-yde8.vercel.app")

origins = [
    frontend_url,
    "https://jardelmessias.com",
    "meu-portfolio-jardel-yde8.vercel.app",
    "http://localhost:3000",
    "http://localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Isso aqui permite que QUALQUER link da Vercel acesse o chat
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Rotas
@api_router.get("/")
async def root():
    return {"message": "API do portfólio rodando!"}
# Mude de @app.post("/api/tts") para:
@api_router.post("/tts") # O prefixo /api já vem do router
async def get_audio(payload: dict):
    texto = payload.get("text")
    if not texto:
        return JSONResponse(content={"error": "Sem texto"}, status_code=400)

    audio_content = await chat_service.get_voice_audio(texto)

    if audio_content:
        return Response(
            content=audio_content, 
            media_type="audio/mpeg",
            headers={
                "Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Methods": "POST, OPTIONS",
                "Access-Control-Allow-Headers": "*"
            }
        )
    return JSONResponse(content={"error": "Falha no áudio"}, status_code=500)
@api_router.get("/status", response_model=List[StatusCheck])
async def get_status_checks():
    status_checks = await db.status_checks.find().to_list(1000)
    return [StatusCheck(**status_check) for status_check in status_checks]

@api_router.post("/status", response_model=StatusCheck)
async def create_status_check(input: StatusCheckCreate):
    status_dict = input.dict()
    status_obj = StatusCheck(**status_dict)
    _ = await db.status_checks.insert_one(status_obj.dict())
    return status_obj




# Certifique-se que o chat_service recebe o 'db'
chat_service = ChatService(db) 

@api_router.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request: Request):
    try:
        data = await request.json()
        message = data.get("message")
        session_id = data.get("session_id")

        if not message:
            raise HTTPException(status_code=400, detail="Mensagem vazia")

        # O process_message deve ser assíncrono (await)
        resposta, nova_session_id = await chat_service.process_message(
            message=message,
            session_id=session_id
        )
        
        return ChatResponse(response=resposta, session_id=nova_session_id)

    except Exception as e:
        print(f"🔥 ERRO NO CHAT: {traceback.format_exc()}") # Isso vai mostrar o erro real no terminal
        return JSONResponse(
            status_code=500,
            content={"detail": f"Erro interno: {str(e)}"}
        )
async def get_chat_session(session_id: str):
    try:
        sessao = await chat_service.get_session_history(session_id)
        if not sessao:
            raise HTTPException(status_code=404, detail="Sessão não encontrada")
        print("Retornando:", (sessao, sessao.session_id))
        return {
            "session_id": sessao.session_id,
            "messages": [
                {
                    "role": msg.role,
                    "content": msg.content,
                    "timestamp": msg.timestamp.isoformat()
                }
                for msg in sessao.messages
            ]
        }
    except HTTPException:
        raise


# Inclua o router APENAS depois de todas as rotas estarem definidas
app.include_router(api_router)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)