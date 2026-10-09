import pytest

from app.core.models import Client

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


async def test_get_hello_view(api_client):
    """Tests whether the view can use a Django model"""
    old_count = await Client.objects.acount()
    assert old_count == 0
    async with api_client as ac:
        response = await ac.get("/hello")
    assert response.status_code == 200
    new_count = await Client.objects.acount()
    assert new_count == 1
    assert response.json() == {"message": "Hello World, count: 1"}


async def test_clears_database_after_test(api_client):
    """Testing whether Django clears the database"""
    await test_get_hello_view(api_client)
