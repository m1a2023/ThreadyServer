""" FastAPI imports """
from fastapi import APIRouter, Depends, Query, Request
""" typing imports """
from typing import Any, List, Optional, Union
""" Internal imports """
from core.db import SessionDep, get_db
from services import general_service as gen
from models.db_models import UserBase, Users


""" APIRouter added to upper router(db/__init__.py) """
router = APIRouter(prefix="/users", tags=["/users"])

@router.get("/", dependencies=[Depends(get_db)], response_model=List[Users])
async def get_all_users(s: SessionDep) -> Any:
	return await gen.get_all_users(s)
	
@router.get("/{id}", dependencies=[Depends(get_db)], response_model=Users)
async def get_user_by_id(s: SessionDep, id: int):
	return await gen.get_user_by_id(s, id)

@router.get("/", dependencies=[Depends(get_db)], response_model=List[Users])
async def get_users_by_ids(s: SessionDep, id: List[int] = Query(...)):
	return await gen.get_users_by_ids(s, id)

@router.post("/", dependencies=[Depends(get_db)], response_model=int)
async def create_user(s: SessionDep, user: UserBase): 
	""" 
	`user` is json body.
	#### Example body:
	`{"id": 1, "name": "thready"}`
 """
	return await gen.create_user(s, user)
