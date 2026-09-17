from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api import predict, auth
from app.ml.inference import ml_service
from app.db.session import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize MongoDB connection and indexes
    init_db()
    
    # Load ML Model and preprocessing rulebooks
    ml_service.load_model()
    
    yield

app = FastAPI(title="OptiChain Unified Backend", lifespan=lifespan)

# CORS configuration for React/Vite
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API Routers
app.include_router(auth.router, prefix="/api/auth", tags=["Auth"])
app.include_router(predict.router, prefix="/api", tags=["Machine Learning"])

@app.get("/api/health", tags=["Health"])
def health_check():
    return {"status": "OptiChain FastAPI backend with MongoDB Atlas & ML Inference is active"}