from fastapi import FastAPI
from src.routes import test
from src.routes import yt_dlp_service

app = FastAPI(title="Flutter Backend API")

# Include your routes
app.include_router(test.router)
app.include_router(yt_dlp_service.router)

@app.get("/")
def root():
    return {"message": "Backend is running"}
