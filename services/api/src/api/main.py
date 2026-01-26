from fastapi import FastAPI
from sqlalchemy import text

from db.session import SessionLocal

app = FastAPI()

@app.get("/")
def health():
    return {"status": "ok"}

@app.get("/db-ping")
async def db_ping():
    async with SessionLocal() as session:
        v = await session.execute(text("select 1"))
        return {"db": v.scalar_one()}
