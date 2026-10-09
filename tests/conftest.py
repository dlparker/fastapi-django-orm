import pytest
from httpx import ASGITransport, AsyncClient

from app.main import fast


@pytest.fixture()
def client() -> AsyncClient:
    return AsyncClient(transport=ASGITransport(app=fast), base_url="http://testserver")
