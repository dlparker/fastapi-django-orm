from fastapi import APIRouter, HTTPException, status

from app.core.models import Client
from app.core.schemas import ClientIn, ClientOut

router = APIRouter(prefix="/clients", tags=["clients"])


# Routes are `async def` and use the async ORM API (acreate, aget, ...).
# Calling the sync API (create, get, ...) here raises SynchronousOnlyOperation.


@router.get("", response_model=list[ClientOut])
async def list_clients():
    return [client async for client in Client.objects.order_by("id")]


@router.post("", response_model=ClientOut, status_code=status.HTTP_201_CREATED)
async def create_client(data: ClientIn):
    return await Client.objects.acreate(**data.model_dump())


@router.get("/{client_id}", response_model=ClientOut)
async def get_client(client_id: int):
    try:
        return await Client.objects.aget(pk=client_id)
    except Client.DoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client not found")


@router.delete("/{client_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_client(client_id: int):
    deleted, _ = await Client.objects.filter(pk=client_id).adelete()
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Client not found")
