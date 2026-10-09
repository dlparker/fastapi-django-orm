from fastapi import APIRouter, HTTPException, status

from app.core.models import User
from app.core.schemas import UserIn, UserOut

router = APIRouter(prefix="/users", tags=["users"])


# Routes are `async def` and use the async ORM API (acreate, aget, ...).
# Calling the sync API (create, get, ...) here raises SynchronousOnlyOperation.


@router.get("", response_model=list[UserOut])
async def list_users():
    return [user async for user in User.objects.order_by("id")]


@router.post("", response_model=UserOut, status_code=status.HTTP_201_CREATED)
async def create_user(data: UserIn):
    return await User.objects.acreate(**data.model_dump())


@router.get("/{user_id}", response_model=UserOut)
async def get_user(user_id: int):
    try:
        return await User.objects.aget(pk=user_id)
    except User.DoesNotExist:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")


@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(user_id: int):
    deleted, _ = await User.objects.filter(pk=user_id).adelete()
    if not deleted:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "User not found")
