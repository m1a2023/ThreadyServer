""" FastAPI imports """
from fastapi import APIRouter, Body, Depends, Query, Request
""" SQLModel imports"""
from psycopg2 import OperationalError
from sqlmodel import select
""" SQLAlchemy imports """
from sqlalchemy.orm.exc import UnmappedInstanceError
""" typing imports """
from typing import Any, List, Optional, Union
""" Internal imports """
from core.db import SessionDep, get_db
from services import general_service as gen
from models.db_models import UserBase, Users


""" APIRouter added to upper router(db/__init__.py) """
router = APIRouter(prefix="/users", tags=["/users"])

@router.get("/", dependencies=[Depends(get_db)], response_model=List[Users])
async def get_all_users(s: SessionDep):
	return await gen.get_all_users(s)
	
@router.get("/{id}", dependencies=[Depends(get_db)], response_model=Union[int, Any])
async def get_user_by_id(s: SessionDep, id: int):
	user =  await gen.get_user_by_id(s, id)
	if user is None:
		return { "error": rf"user with id {id} doesn't exist" }
	return user

@router.get("/bat/", dependencies=[Depends(get_db)], response_model=List[Users])
async def get_users_by_ids(s: SessionDep, id: List[int] = Query(...)):
	return await gen.get_users_by_ids(s, id)

@router.post("/", dependencies=[Depends(get_db)], response_model=int)
async def create_user(s: SessionDep, user: UserBase): 
	""" 
	`user` is json body.
	#### Example body:
	`{"id": 1, "name": "thready"}`
 """
	if s.exec(select(Users).where(Users.id == user.id)).first() is not None:
		return user.id
	return await gen.create_user(s, user)

@router.post("/bat", dependencies=[Depends(get_db)], response_model=List[int])
async def create_users(s: SessionDep, users:  List[UserBase]):
	"""
 	`users` is json body.
  #### Example body: 
	`[ {"id": 1, "name": "thready"}, {"id": 2, "name": "bot"} ]
  """
	return await gen.create_users(s, users)

@router.delete("/{id}", dependencies=[Depends(get_db)], response_model=Union[int, Any])
async def delete_user_by_id(s: SessionDep, id: int):
	try:
		_id = await gen.delete_user_by_id(s, id)
		return _id
	except UnmappedInstanceError:
		return {"error": rf"user with id {id} doesn't exist"}
	
