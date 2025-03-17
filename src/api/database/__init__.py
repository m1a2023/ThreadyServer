""" FastAPI imports """
from fastapi import APIRouter, Depends, Query, Request
""" Internal imports """
from .users import users_router

""" APIRouter added to upper router(api/__init__.py) """
router = APIRouter()

router.include_router(users_router)
# router.include_router(users_router)
# router.include_router(users_router)
