from fastapi import FastAPI
from src.routes import test

app = FastAPI(title="Flutter Backend API")

# Include your routes
app.include_router(test.router)

@app.get("/")
def root():
    return {"message": "Backend is running"}
