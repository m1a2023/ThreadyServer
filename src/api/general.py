""" FastAPI imports """
from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
""" httpx import """
import httpx
""" typing imports """
from typing import Optional, Union
""" Internal imports """
from src.core.db import get_db
from services import llm_service as llm

""" APIRouter added to general """
router = APIRouter(prefix="/db/", tags=["/db/"])

# @router.get("/users/", dependencies=[Depends(get_db)])
# async def get_all_users():
	