from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from app.config import settings
from app.routers import patients, doctor


app = FastAPI(
    title="OPD Queue Management API",
    description="Hospital OPD queue management system",
    version="1.0.0",
    debug=settings.debug
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(patients.router)
app.include_router(doctor.router)

@app.on_event("startup")
async def startup():
    logger.info("OPD Queue API starting up")


@app.on_event("shutdown")
async def shutdown():
    logger.info("OPD Queue API shutting down")


@app.get("/health")
def health():
    return {
        "status": "ok",
        "app": "OPD Queue Management API",
        "version": "1.0.0"
    }