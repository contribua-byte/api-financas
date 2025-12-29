from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class TextData(BaseModel):
    message: str

class ZapiWebhook(BaseModel):
    phone: str
    text: TextData

@app.get("/")
def inicio():
    return {"mensagem": "API WhatsApp rodando!"}

@app.post("/webhook")
async def webhook(dados: ZapiWebhook):
    telefone = dados.phone
    mensagem = dados.text.message

    return {
        "status": "ok",
        "telefone": telefone,
        "mensagem_recebida": mensagem
    }
