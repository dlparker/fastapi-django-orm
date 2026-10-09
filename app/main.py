from django import setup as django_setup
from django.core.handlers.asgi import ASGIHandler
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates


def get_asgi_application():
    """
    The public interface to Django's ASGI support. Return an ASGI 3 callable.

    Avoids making django.core.handlers.ASGIHandler a public API, in case the
    internal implementation changes or moves in the future.
    """
    django_setup(set_prefix=False)
    return ASGIHandler()


# Django must be set up before importing anything that touches models
application = get_asgi_application()

from app.core.api import router  # noqa: E402

fast = FastAPI(title="My app", openapi_url=f"/openapi.json")
fast.include_router(router)
fast.mount("/static", StaticFiles(directory="static"), name="static")
fast.mount("/d", application)
templates = Jinja2Templates(directory="templates")
