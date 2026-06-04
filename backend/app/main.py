from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()

from app.api.v1 import modernize, health, verify


app = FastAPI(
    title="Legacy Coder V1",
    version="1.0.0",
    description="API for legacy code modernization, pipeline execution, and verification",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],    
)

app.include_router(modernize.router , prefix="/api/v1", tags=["Modernize"])
app.include_router(health.router , prefix="/api/v1", tags=["Health"])
app.include_router(verify.router , prefix="/api/v1", tags=["Verify"])

@app.get("/")
def root():
    return {
        "message": "Welcome to Legacy Coder API",
        "docs": "/docs",
        "openapi": "/openapi.json",
        "pipeline_endpoint": "/api/v1/modernize/pipeline",
    }


@app.get("/api/v1/endpoints")
def list_endpoints():
    return {
        "health": "GET /api/v1/health",
        "modernize": "POST /api/v1/modernize/",
        "pipeline": "POST /api/v1/modernize/pipeline",
        "verify_rewrite": "POST /api/v1/verify/rewrite",
    }