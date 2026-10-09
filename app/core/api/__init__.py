from fastapi import APIRouter

from .a_view import router as a_router
from .clients import router as clients_router

router = APIRouter()
router.include_router(a_router)
router.include_router(clients_router)
