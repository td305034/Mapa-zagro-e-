from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from app.database import engine

app = FastAPI(title="Mapa zagrożeń API")

@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.get("/db-check")
def db_check():
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        return {"db_connection": "ok", "result": result.scalar()}


app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)