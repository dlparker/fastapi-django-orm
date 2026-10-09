import re

import pytest
from django.contrib.auth.models import User as AuthUser

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


async def test_admin_requires_login(api_client):
    async with api_client as ac:
        response = await ac.get("/d/admin/")
    assert response.status_code == 302
    assert response.headers["location"] == "/d/admin/login/?next=/d/admin/"


async def test_admin_static_files_are_served(api_client):
    async with api_client as ac:
        response = await ac.get("/static/admin/css/base.css")
    assert response.status_code == 200


async def test_admin_login(api_client):
    """Logging in exercises sessions, CSRF and URL reversing under /d"""
    await AuthUser.objects.acreate_superuser("admin", "admin@example.com", "pw")
    async with api_client as ac:
        response = await ac.get("/d/admin/login/")
        token = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
        response = await ac.post(
            "/d/admin/login/?next=/d/admin/",
            data={
                "csrfmiddlewaretoken": token.group(1),
                "username": "admin",
                "password": "pw",
                "next": "/d/admin/",
            },
        )
        assert response.status_code == 302
        assert response.headers["location"] == "/d/admin/"

        response = await ac.get("/d/admin/")
    assert response.status_code == 200
    assert "Site administration" in response.text
