from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class WebhookData(BaseModel):
    texto: str

@app.get("/")
def inicio():
    return {"mensagem": "Minha API está funcionando!"}

@app.post("/webhook")
async def webhook(dados: WebhookData):
    return {
        "status": "recebido",
        "dados": dados.dict()
    }
