from fastapi import FastAPI, Request
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import re
import io

app = FastAPI()

# =========================
# ARMAZENAMENTO EM MEMÓRIA
# =========================
gastos = []

# =========================
# ROTAS BÁSICAS
# =========================
@app.get("/")
def inicio():
    return {"mensagem": "API de Finanças rodando!"}

# =========================
# FUNÇÃO AUXILIAR
# =========================
def interpretar_mensagem(texto: str):
    # Procura um número na mensagem (ex: 30, 30.50, 30,50)
    valor_match = re.search(r"(\d+([.,]\d+)?)", texto)
    if not valor_match:
        return None, None

    valor = float(valor_match.group(1).replace(",", "."))
    descricao = texto.replace(valor_match.group(1), "").strip()

    return valor, descricao

# =========================
# WEBHOOK WHATSAPP (OFICIAL)
# =========================
@app.post("/webhook")
async def webhook(request: Request):
    data = await request.json()

    # Log para debug no Render
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
        print("❌ ERRO AO PROCESSAR MENSAGEM:", e)
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

# =========================
# LISTAR GASTOS
# =========================
@app.get("/gastos")
def listar_gastos():
    return {
        "total": len(gastos),
        "gastos": gastos
    }

# =========================
# RESUMO
# =========================
@app.get("/resumo")
def resumo():
    soma = sum(g["valor"] for g in gastos)
    return {
        "total_registros": len(gastos),
        "soma": soma
    }

# =========================
# EXPORTAR CSV
# =========================
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