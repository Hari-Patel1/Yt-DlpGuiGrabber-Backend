from fastapi import APIRouter, Request

router = APIRouter()

@router.get("/ping")
def ping():
    return {"message": "pong"}

@router.post("/echo")
async def echo(request: Request):
    data = await request.json()
    return {"you_sent": data}