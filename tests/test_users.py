import pytest

from app.core.models import User

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


async def test_create_and_get_user(client):
    async with client as ac:
        response = await ac.post("/users", json={"name": "alice"})
        assert response.status_code == 201
        user_id = response.json()["id"]
        assert response.json() == {"id": user_id, "name": "alice"}

        response = await ac.get(f"/users/{user_id}")
    assert response.status_code == 200
    assert response.json() == {"id": user_id, "name": "alice"}


async def test_list_users(client):
    await User.objects.acreate(name="alice")
    await User.objects.acreate(name="bob")
    async with client as ac:
        response = await ac.get("/users")
    assert response.status_code == 200
    assert [u["name"] for u in response.json()] == ["alice", "bob"]


async def test_create_user_validates_input(client):
    async with client as ac:
        response = await ac.post("/users", json={"name": ""})
    assert response.status_code == 422
    assert await User.objects.acount() == 0


async def test_delete_user(client):
    user = await User.objects.acreate(name="alice")
    async with client as ac:
        response = await ac.delete(f"/users/{user.pk}")
        assert response.status_code == 204
        response = await ac.delete(f"/users/{user.pk}")
    assert response.status_code == 404
    assert await User.objects.acount() == 0


async def test_get_missing_user(client):
    async with client as ac:
        response = await ac.get("/users/999")
    assert response.status_code == 404
