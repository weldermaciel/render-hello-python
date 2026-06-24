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
async def listar_indicadores(authorization: str = Header(None)):
    if not authorization:
        raise HTTPException(status_code=401, detail="Token não fornecido")
    
    token = authorization.replace("Bearer ", "")
    
    try:
        # Verifica se o token é válido com o Supabase
        user = supabase.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Token inválido")
        
        # Para a consulta, usa o cliente com a chave anônima (já respeita RLS se ativado)
        response = supabase.table("indicadores").select("*").execute()
        return {"indicadores": response.data}
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"Erro ao processar requisição: {e}")
        raise HTTPException(status_code=500, detail="Erro interno do servidor")