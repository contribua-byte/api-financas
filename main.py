from fastapi import FastAPI
from pydantic import BaseModel
import re

app = FastAPI()

# Lista de gastos em memória
gastos = []

class WebhookData(BaseModel):
    mensagem: str

@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças rodando!"}

def interpretar_mensagem(texto: str):
    # procura número na mensagem
    valor_match = re.search(r"(\d+([.,]\d+)?)", texto)
    if not valor_match:
        return None, None

    valor = float(valor_match.group(1).replace(",", "."))
    descricao = texto.replace(valor_match.group(1), "").strip()

    return valor, descricao

@app.post("/webhook")
async def webhook(dados: WebhookData):
    texto = dados.mensagem.lower()

    valor, descricao = interpretar_mensagem(texto)

    if valor is None:
        return {"status": "erro", "mensagem": "Não encontrei valor na mensagem."}

    gasto = {
        "valor": valor,
        "descricao": descricao
    }

    gastos.append(gasto)

    return {
        "status": "ok",
        "gasto": gasto,
        "total_registros": len(gastos)
    }

@app.get("/gastos")
def listar_gastos():
    return {
        "total": len(gastos),
        "gastos": gastos
    }
