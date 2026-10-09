import pytest

from app.core.models import Client

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


async def test_create_and_get_client(api_client):
    async with api_client as ac:
        response = await ac.post("/clients", json={"name": "alice"})
        assert response.status_code == 201
        client_id = response.json()["id"]
        assert response.json() == {"id": client_id, "name": "alice"}

        response = await ac.get(f"/clients/{client_id}")
    assert response.status_code == 200
    assert response.json() == {"id": client_id, "name": "alice"}


async def test_list_clients(api_client):
    await Client.objects.acreate(name="alice")
    await Client.objects.acreate(name="bob")
    async with api_client as ac:
        response = await ac.get("/clients")
    assert response.status_code == 200
    assert [u["name"] for u in response.json()] == ["alice", "bob"]


async def test_create_user_validates_input(api_client):
    async with api_client as ac:
        response = await ac.post("/clients", json={"name": ""})
    assert response.status_code == 422
    assert await Client.objects.acount() == 0


async def test_delete_client(api_client):
    client = await Client.objects.acreate(name="alice")
    async with api_client as ac:
        response = await ac.delete(f"/clients/{client.pk}")
        assert response.status_code == 204
        response = await ac.delete(f"/clients/{client.pk}")
    assert response.status_code == 404
    assert await Client.objects.acount() == 0


async def test_get_missing_client(api_client):
    async with api_client as ac:
        response = await ac.get("/clients/999")
    assert response.status_code == 404
