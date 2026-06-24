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

SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_ANON_KEY = os.environ.get("SUPABASE_ANON_KEY")
supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)

@app.get("/")
def home():
    return {"message": "Hello, World!"}

@app.get("/api/indicadores")
async def listar_indicadores(
    authorization: str = Header(None),
    x_refresh_token: str = Header(None)
):
    if not authorization or not x_refresh_token:
        raise HTTPException(status_code=401, detail="Tokens não fornecidos")

    access_token = authorization.replace("Bearer ", "")

    try:
        # Cria um cliente autenticado com os dois tokens
        supabase_user = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        supabase_user.auth.set_session(access_token, x_refresh_token)

        # Agora o RLS enxerga o auth.uid() corretamente
        response = supabase_user.table("indicadores").select("*").execute()
        return {"indicadores": response.data}

    except Exception as e:
        print(f"Erro ao consultar indicadores: {e}")
        raise HTTPException(status_code=401, detail="Sessão inválida ou expirada")