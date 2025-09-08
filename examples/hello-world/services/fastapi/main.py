import uvicorn  # type: ignore
from fastapi import FastAPI  # type: ignore
from models.message import Message

app = FastAPI()


@app.get("/", response_model=Message)
def read_root():
    return {"message": "Hello, Lychee!"}


@app.get("/health")
def get_health():
    return {"message": "ok"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
