from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SUPABASE_URL = os.environ["SUPABASE_URL"]
SUPABASE_ANON_KEY = os.environ["SUPABASE_ANON_KEY"]
supabase_admin = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

def get_current_user(token: str):
    """Valida o token e retorna o usuário. Lança exceção se inválido."""
    user = supabase_admin.auth.get_user(token.replace("Bearer ", ""))
    if not user or not user.user:
        raise HTTPException(status_code=401, detail="Token inválido ou expirado")
    return user.user

@app.get("/")
def home():
    return {"message": "Hello, World!"}

@app.get("/api/indicadores")
async def listar_indicadores(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")

    # Valida o token e obtém o usuário
    user = get_current_user(authorization)
    
    # Cria cliente autenticado para a consulta (respeita RLS)
    supabase_user = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    supabase_user.auth.set_session(user.id)

    response = supabase_user.table("indicadores").select("*").execute()
    return {"indicadores": response.data}