from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware


from src.api.middleware.error_handler import register_exception_handlers
from src.config.settings import settings
from src.data.clients.postgres_client import get_or_create_engine
from src.observability.logging.logger import configure_logging, get_logger, log_function
from src.api.rest.routes.health import router as health_router
from src.api.rest.routes.hall import router as hall_router
from src.api.rest.routes.facility import router as facility_router
from src.api.rest.routes.favorite import router as favorite_router
from src.api.rest.routes.booking import router as booking_router
from src.api.rest.routes.search import router as search_router
from src.api.rest.routes.notifications import router as notifications_router


configure_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting up the application")
    engine = await get_or_create_engine()
    
    
    yield
    await engine.dispose()
    logger.info("Shutting down the application")


app = FastAPI(title="Hall Booking System core backend service", lifespan=lifespan)

register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/")
@log_function(logger)
async def root():
    return {"message": "Welcome to the Hall Booking System API!"}


app.include_router(health_router)
app.include_router(hall_router)
app.include_router(facility_router)
app.include_router(favorite_router)
app.include_router(booking_router)
app.include_router(search_router)
app.include_router(notifications_router)
