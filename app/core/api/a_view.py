from fastapi import APIRouter

from app.core.models import Client

router = APIRouter()


@router.get("/hello")
async def hello():
    await Client.objects.acreate(name="random")
    return {"message": f"Hello World, count: {await Client.objects.acount()}"}
