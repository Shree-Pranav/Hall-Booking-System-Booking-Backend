from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession

from src.core.exceptions import BaseAppException
from src.config.settings import settings
from src.data.clients.postgres_client import get_or_create_engine
from src.api.rest.routes.health import router as health_router
from src.api.rest.routes.hall import router as hall_router
from src.api.rest.routes.facility import router as facility_router
from src.api.rest.routes.favorite import router as favorite_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting up the application...")
    engine = await get_or_create_engine()
    
    
    yield
    await engine.dispose()
    print("Shutting down the application...")


app = FastAPI(title="Hall Booking System core backend service", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


@app.exception_handler(BaseAppException)
async def base_app_exception_handler(request, exc: BaseAppException):
    """Handle custom application exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content=exc.to_dict(),
    )


@app.get("/")
async def root():
    return {"message": "Welcome to the Hall Booking System API!"}


app.include_router(health_router)
app.include_router(hall_router)
app.include_router(facility_router)
app.include_router(favorite_router)