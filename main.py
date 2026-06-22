from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware  # <-- adicione essa linha

app = FastAPI()

# Adicione esse bloco depois de criar o app
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Em produção, troque "*" pelo domínio do Vercel
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def hello():
    return {"message": "Hello, World!"}