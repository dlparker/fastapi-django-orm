from asgiref.sync import ThreadSensitiveContext
from django.core import signals
from django.core.handlers.asgi import ASGIHandler


class DjangoDBMiddleware:
    """
    Gives each FastAPI request the database handling Django's own ASGI
    handler provides, which FastAPI routes otherwise never get.

    - Each request runs inside its own ThreadSensitiveContext, so the async
      ORM (``acreate``, ``aget``, ...) uses a per-request thread instead of
      one thread shared by the whole process.
    - Django's request_started/request_finished signals are sent around the
      request. Their receivers close connections that are past CONN_MAX_AGE
      or unusable (and reset the DEBUG query log), so connections don't leak
      or go stale.

    Only the async ORM API is covered. Sync ORM calls made directly in a
    plain ``def`` route run on FastAPI's threadpool, outside this context,
    and their connections are never cleaned up; wrap such code in
    ``asgiref.sync.sync_to_async`` and call it from an ``async def`` route.
    """

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] not in ("http", "websocket"):
            await self.app(scope, receive, send)
            return

        async with ThreadSensitiveContext():
            await signals.request_started.asend(sender=ASGIHandler, scope=scope)
            try:
                await self.app(scope, receive, send)
            finally:
                await signals.request_finished.asend(sender=ASGIHandler)
