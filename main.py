from fastapi import FastAPI, Header, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
from pydantic import BaseModel
from typing import List
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

# --- Modelos ---

class IndicadorIn(BaseModel):
    id: str
    secretaria: str
    departamento: str
    indicador: str
    dono: str
    tipo_dados: str
    comportamento: str
    tipo_info: str
    ano: int
    lancamentos: List[float] = [0]*12
    cor: str = "#002e6e"
    direcao: str = "cima"

class LancamentosUpdate(BaseModel):
    id: str
    lancamentos: List[float]

# --- Autenticação ---

def get_auth_user(authorization: str = Header(None), x_refresh_token: str = Header(None)):
    if not authorization or not x_refresh_token:
        raise HTTPException(status_code=401, detail="Credenciais não fornecidas")
    token = authorization.replace("Bearer ", "")
    supabase_user = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
    supabase_user.auth.set_session(token, x_refresh_token)
    return supabase_user

# --- Endpoints (espelham as funções .gs) ---

@app.get("/api/indicadores")
async def get_dados(user = Depends(get_auth_user)):
    """Equivalente a getDados() do Apps Script"""
    response = user.table("indicadores").select("*").execute()
    # Converte para o formato original (com 'lancamentos' como array)
    dados = []
    for row in response.data:
        dados.append({
            "id": row["id"],
            "secretaria": row["secretaria"],
            "departamento": row["departamento"],
            "indicador": row["indicador"],
            "dono": row["dono"],
            "tipoDados": row["tipo_dados"],
            "comportamento": row["comportamento"],
            "tipoInfo": row["tipo_info"],
            "ano": row["ano"],
            "lancamentos": [row["jan"], row["fev"], row["mar"], row["abr"], row["mai"], row["jun"], row["jul"], row["ago"], row["set"], row["out"], row["nov"], row["dez"]],
            "cor": row["cor"],
            "direcao": row["direcao"]
        })
    return {"indicadores": dados}

@app.post("/api/indicadores")
async def salvar_novo_indicador(ind: IndicadorIn, user = Depends(get_auth_user)):
    """Equivalente a salvarNovoIndicador() do Apps Script"""
    meses = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    row = {
        "id": ind.id,
        "secretaria": ind.secretaria,
        "departamento": ind.departamento,
        "indicador": ind.indicador,
        "dono": ind.dono,
        "tipo_dados": ind.tipo_dados,
        "comportamento": ind.comportamento,
        "tipo_info": ind.tipo_info,
        "ano": ind.ano,
        "cor": ind.cor,
        "direcao": ind.direcao
    }
    for i, mes in enumerate(meses):
        row[mes] = ind.lancamentos[i] if i < len(ind.lancamentos) else 0
    response = user.table("indicadores").insert(row).execute()
    return response.data[0]

@app.put("/api/indicadores/lancamentos/lote")
async def salvar_lote_lancamentos(lista: List[LancamentosUpdate], user = Depends(get_auth_user)):
    """Equivalente a salvarLoteLancamentos() do Apps Script"""
    meses = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    for item in lista:
        update_data = {meses[i]: item.lancamentos[i] for i in range(12)}
        user.table("indicadores").update(update_data).eq("id", item.id).execute()
    return {"ok": True}

@app.put("/api/indicadores/{id}")
async def atualizar_indicador_completo(id: str, ind: IndicadorIn, user = Depends(get_auth_user)):
    """Equivalente a atualizarIndicadorCompleto() do Apps Script"""
    meses = ["jan","fev","mar","abr","mai","jun","jul","ago","set","out","nov","dez"]
    row = {
        "id": ind.id,
        "secretaria": ind.secretaria,
        "departamento": ind.departamento,
        "indicador": ind.indicador,
        "dono": ind.dono,
        "tipo_dados": ind.tipo_dados,
        "comportamento": ind.comportamento,
        "tipo_info": ind.tipo_info,
        "ano": ind.ano,
        "cor": ind.cor,
        "direcao": ind.direcao
    }
    for i, mes in enumerate(meses):
        row[mes] = ind.lancamentos[i] if i < len(ind.lancamentos) else 0
    response = user.table("indicadores").update(row).eq("id", id).execute()
    if not response.data:
        raise HTTPException(status_code=404, detail="Indicador não encontrado")
    return response.data[0]

@app.delete("/api/indicadores/{id}")
async def deletar_indicador(id: str, user = Depends(get_auth_user)):
    """Equivalente a deletarIndicador() do Apps Script"""
    user.table("indicadores").delete().eq("id", id).execute()
    return {"ok": True}