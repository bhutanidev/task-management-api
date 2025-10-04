from contextlib import asynccontextmanager

from fastapi import FastAPI, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.db import get_db, engine
from app.routers.auth import router as auth_router
from app.routers.tasks import router as tasks_router
from app.routers.categories import router as categories_router

from app.routers.auth import limiter
from slowapi.util import get_remote_address
from slowapi.middleware import SlowAPIMiddleware


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Code here runs before the application starts
    print("Application starting up...")
    
    yield  # Application is running
    
    # Shutdown: Code here runs when the application is shutting down
    print("Application shutting down...")
    await engine.dispose()


app = FastAPI(
    title="Task Management API",
    lifespan=lifespan
)

# Attach limiter to app
app.state.limiter = limiter
app.add_middleware(SlowAPIMiddleware)

# Routers
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
        await db.execute(text("SELECT 1"))
        return {"status": "ok", "message": "Database connected"}
    except Exception as e:
        return {"status": "error", "message": str(e)}