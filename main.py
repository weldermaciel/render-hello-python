from fastapi import Header, HTTPException
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
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.get("/")
def home():
    return {"message": "Hello, World!"}

@app.get("/api/indicadores")
async def listar_indicadores(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")

    token = authorization.replace("Bearer ", "")

    # Cria um cliente autenticado com o token do usuário
    supabase_user = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    supabase_user.auth.set_session(token)  # Define a sessão do usuário

    # Agora o Supabase reconhece o usuário e aplica o RLS
    response = supabase_user.table("indicadores").select("*").execute()
    return {"indicadores": response.data}