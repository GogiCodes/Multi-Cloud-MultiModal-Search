from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.router import router
from app.config import settings

app = FastAPI(
    title="Multi-Cloud Multimodal Product Search",
    description="A product search engine using Azure Vision, Google Gemini, and AWS Claude",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Frontend URLs
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(router)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "version": "1.0.0"}