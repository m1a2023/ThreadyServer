""" FastAPI imports """
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
""" SQLModel imports"""
from psycopg2 import OperationalError
from sqlmodel import select
""" SQLAlchemy imports """
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.exc import SQLAlchemyError
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
	try:
		users = await gen.get_all_users(s)
		if users is None:
			raise HTTPException(status_code=404, detail="Error getting users")
		return users	
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail="Error getting users")

@router.get("/{id}", dependencies=[Depends(get_db)], response_model=int)
async def get_user_by_id(s: SessionDep, id: int):
	try:
		user = await gen.get_user_by_id(s, id)
		if user is None:
			raise HTTPException(status_code=404, detail=f"Error getting user by id {id}")
		return user
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error getting user by id {id}: {str(e)}")

@router.get("/bat/", dependencies=[Depends(get_db)], response_model=List[Users])
async def get_users_by_ids(s: SessionDep, id: List[int] = Query(...)):
	try:
		users = await gen.get_users_by_ids(s, id)
		if users is None:
				raise HTTPException(status_code=404, detail="Error getting users by IDs")
		return users
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error getting users by IDs: {str(e)}")

@router.post("/", dependencies=[Depends(get_db)], response_model=int)
async def create_user(s: SessionDep, user: UserBase): 
	try:
		if s.exec(select(Users).where(Users.id == user.id)).first() is not None:
			return user.id
		return await gen.create_user(s, user)
	except SQLAlchemyError as e:
		s.rollback()
		raise HTTPException(status_code=500, detail=f"Error creating user: {str(e)}")

@router.post("/bat", dependencies=[Depends(get_db)], response_model=List[int])
async def create_users(s: SessionDep, users: List[UserBase]):
	try:
		ids = await gen.create_users(s, users)
		if ids is None:
			raise HTTPException(status_code=404, detail="Error creating users")
	except SQLAlchemyError as e:
		s.rollback()
		raise HTTPException(status_code=500, detail=f"Error creating users: {str(e)}")

@router.delete("/{id}", dependencies=[Depends(get_db)], response_model=Union[int, Any])
async def delete_user_by_id(s: SessionDep, id: int):
	try:
		_id = await gen.delete_user_by_id(s, id)
		if _id is None:
				raise HTTPException(status_code=404, detail=f"User with id {id} doesn't exist")
		return _id
	except SQLAlchemyError as e:
		s.rollback()
		raise HTTPException(status_code=500, detail=f"Error deleting user by id {id}: {str(e)}")
