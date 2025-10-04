from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db, engine
from app.routers.auth import router as auth_router
from app.routers.tasks import router as tasks_router
from app.routers.categories import router as categories_router


app = FastAPI(title="Task Management API")

app.include_router(auth_router)
app.include_router(tasks_router)
app.include_router(categories_router)

@app.get("/health")
async def health_check():
    return {"status": "ok", "message": "API is running"}

@app.get("/health/db")
async def health_check_db(db: AsyncSession = Depends(get_db)):
    try:
        # Test DB connection
        result = await db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}

@app.on_event("shutdown")
async def shutdown():
    await engine.dispose()