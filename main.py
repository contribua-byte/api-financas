from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

# Lista em memória para guardar mensagens
registros = []

class WebhookData(BaseModel):
    mensagem: str

@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças rodando!"}

@app.post("/webhook")
async def webhook(dados: WebhookData):
    registros.append(dados.mensagem)

    return {
        "status": "ok",
        "total_registros": len(registros),
        "ultimo": dados.mensagem
    }

@app.get("/registros")
def listar_registros():
    return {
        "total": len(registros),
        "registros": registros
    }
