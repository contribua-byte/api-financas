from fastapi import FastAPI, Request
from pydantic import BaseModel
from fastapi.responses import StreamingResponse
import re
import io

app = FastAPI()

# TOKEN de verificação do WhatsApp (use o mesmo na Meta)
VERIFY_TOKEN = "financas_api_2025"

# Lista de gastos em memória
gastos = []

class WebhookData(BaseModel):
    mensagem: str


@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças rodando!"}


# 🔹 Endpoint usado pela Meta para verificar o webhook
@app.get("/webhook")
async def verificar_webhook(request: Request):
    params = request.query_params

    hub_mode = params.get("hub.mode")
    hub_token = params.get("hub.verify_token")
    hub_challenge = params.get("hub.challenge")

    if hub_mode == "subscribe" and hub_token == VERIFY_TOKEN:
        return int(hub_challenge)

    return {"erro": "Token inválido"}


def interpretar_mensagem(texto: str):
    valor_match = re.search(r"(\d+([.,]\d+)?)", texto)
    if not valor_match:
        return None, None

    valor = float(valor_match.group(1).replace(",", "."))
    descricao = texto.replace(valor_match.group(1), "").strip()

    return valor, descricao


# 🔹 Endpoint que vai receber mensagens (WhatsApp no futuro)
@@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    print("📩 PAYLOAD RECEBIDO:", data)

    try:
        entry = data.get("entry", [])
        if not entry:
            return {"status": "sem_entry"}

        changes = entry[0].get("changes", [])
        if not changes:
            return {"status": "sem_changes"}

        value = changes[0].get("value", {})

        messages = value.get("messages")
        if not messages:
            return {"status": "evento_sem_mensagem"}

        mensagem = messages[0]["text"]["body"]

    except Exception as e:
        print("❌ ERRO AO LER MENSAGEM:", e)
        return {"status": "erro_parse"}

    texto = mensagem.lower()

    valor, descricao = interpretar_mensagem(texto)

    if valor is None:
        return {"status": "sem_valor"}

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


@app.get("/resumo")
def resumo():
    soma = sum(g["valor"] for g in gastos)
    return {
        "total_registros": len(gastos),
        "soma": soma
    }


@app.get("/exportar")
def exportar():
    output = io.StringIO()
    output.write("valor,descricao\n")

    for g in gastos:
        output.write(f"{g['valor']},{g['descricao']}\n")

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=gastos.csv"}
    )