from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi import status as http_status
from fastapi.responses import JSONResponse

from app import database
from app.routers import users


@asynccontextmanager
async def lifespan(_: FastAPI):
    database.connect_database()
    try:
        yield
    finally:
        database.close_database()


app = FastAPI(
    title="User Service",
    description="Microservice responsible for user management",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(users.router)


@app.get("/")
def root():
    return {
        "service": "User Service",
        "message": "User Service is running successfully",
    }


@app.get("/health")
def health_check():
    healthy = database.check_database_connection()
    if not healthy:
        return JSONResponse(
            status_code=http_status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"service": "user-service", "status": "unhealthy"},
        )
    return {
        "service": "user-service",
        "status": "healthy",
    }