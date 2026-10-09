import asyncio
import threading

import pytest
from asgiref.sync import sync_to_async
from django.core import signals
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from app.core.models import User
from app.db import DjangoDBMiddleware

pytestmark = [pytest.mark.django_db(transaction=True), pytest.mark.asyncio]


@pytest.fixture()
def recorder():
    """Records which thread each request's signals and ORM calls run on"""
    events = []

    def on_started(**kwargs):
        events.append(("started", threading.get_ident()))

    def on_finished(**kwargs):
        events.append(("finished", threading.get_ident()))

    signals.request_started.connect(on_started)
    signals.request_finished.connect(on_finished)
    yield events
    signals.request_started.disconnect(on_started)
    signals.request_finished.disconnect(on_finished)


@pytest.fixture()
def probe_client(recorder) -> AsyncClient:
    app = FastAPI()
    app.add_middleware(DjangoDBMiddleware)

    @app.get("/probe")
    async def probe():
        def query():
            User.objects.count()
            return threading.get_ident()

        recorder.append(("orm", await sync_to_async(query)()))
        # Keep requests overlapping so they can't share a thread by chance
        await asyncio.sleep(0.05)
        return {}

    return AsyncClient(transport=ASGITransport(app=app), base_url="http://testserver")


async def test_cleanup_runs_on_the_requests_orm_thread(probe_client, recorder):
    """Connections are thread-local, so cleanup must happen on the ORM thread"""
    async with probe_client as ac:
        response = await ac.get("/probe")
    assert response.status_code == 200
    assert [name for name, _ in recorder] == ["started", "orm", "finished"]
    assert len({thread for _, thread in recorder}) == 1


async def test_concurrent_requests_get_separate_orm_threads(probe_client, recorder):
    async with probe_client as ac:
        responses = await asyncio.gather(*[ac.get("/probe") for _ in range(5)])
    assert all(r.status_code == 200 for r in responses)
    orm_threads = {thread for name, thread in recorder if name == "orm"}
    assert len(orm_threads) == 5
