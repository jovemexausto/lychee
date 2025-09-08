from fastapi import FastAPI

# Esses tipos gão gerados automaticamente pelo Lychee
from models.message import Message

app = FastAPI()


@app.get("/", response_model=Message)
def read_root():
    return {"message": "Olá, Lychee!"}


@app.get("/health")
def get_health():
    return {"message": "ok"}


# Não precisamos invocar o uvicorn por conta própria, o Lychee faz isso
