from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WebhookData(BaseModel):
    mensagem: str

@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças rodando!"}

@app.post("/webhook")
async def webhook(dados: WebhookData):
    texto = dados.mensagem

    return {
        "status": "ok",
        "recebido": texto
    }
