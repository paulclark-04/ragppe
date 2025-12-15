from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.routes import router as api_router

app = FastAPI(title="MultiSummarizer API", version="0.1.0")

# CORS Configuration
origins = [
    "http://localhost:5173",  # Vite default port
    "http://localhost:5174",  # Vite fallback port
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
async def root():
    return {"message": "Welcome to MultiSummarizer API"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
