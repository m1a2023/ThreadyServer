""" FastAPI imports """
from fastapi import APIRouter
""" Internal imports """
from api import database
from api import llm


db_router = APIRouter(prefix="/db", tags=["/db"])
db_router.include_router(database.router)

llm_router = APIRouter(prefix="/llm", tags=["/llm"])
llm_router.include_router(llm.router)

""" APIRouter added to upper router(src/main.py) """
router = APIRouter(prefix="/api", tags=["/api"])
router.include_router(db_router)
router.include_router(llm_router)