from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WebhookData(BaseModel):
    mensagem: str
    usuario: str

@app.get("/")
def inicio():
    return {"mensagem": "Deu certo!"}


@app.post("/webhook")
async def webhook(dados: WebhookData):
    texto = dados.mensagem
    usuario = dados.usuario

    return {
        "status": "ok",
        "resposta": f"Mensagem '{texto}' recebida do usuário {usuario}."
    }
