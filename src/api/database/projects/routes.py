""" FastAPI imports """
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
""" SQLModel imports"""
from sqlmodel import select
""" SQLAlchemy imports """
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.exc import SQLAlchemyError
""" typing imports """
from typing import Any, Dict, List, Optional, Union
""" Internal imports """
from core.db import SessionDep, get_db
from services import general_service as gen
from models.db_models import ProjectBase, ProjectUpdate, Projects


""" APIRouter added to upper router(db/__init__.py) """
router = APIRouter(prefix="/projects", tags=["/projects"])

@router.get("/", dependencies=[Depends(get_db)], response_model=List[Projects])
async def get_all_projects(s: SessionDep):
	try:
		projects = await gen.get_all_projects(s)
		if projects is None:
			raise HTTPException(status_code=404, detail="Error getting projects")
		return projects
	except SQLAlchemyError as e: 
		raise HTTPException(status_code=500, detail=f"Error getting project: {e}")

@router.get("/owner/{id}", dependencies=[Depends(get_db)], response_model=List[Projects])
async def get_project_by_owner_id(s: SessionDep, id: int):
	try:
		projects = await gen.get_projects_by_owner_id(s, id)
		if projects is None:
			raise HTTPException(status_code=404, detail=f"Error getting projects by owner_id {id}")
		return projects
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error getting projects by owner_id {id}: {str(e)}")

@router.get("/{id}", dependencies=[Depends(get_db)], response_model=Projects)
async def get_project_by_id(s: SessionDep, id: int):
	try:	
		project =  await gen.get_project_by_id(s, id)
		if project is None:
			raise HTTPException(status_code=404, detail=f"Error getting project by id {id}")
		return project
	except SQLAlchemyError as e :
		raise HTTPException(status_code=500, detail=f"Error getting project by id {id}: {str(e)}")

@router.post("/", dependencies=[Depends(get_db)], response_model=int)
async def create_project(s: SessionDep, project: ProjectBase):
	try: 
		return await gen.create_project(s, project)
	except SQLAlchemyError as e:
		s.rollback()
		raise HTTPException(status_code=500, detail=f"Error creating project: {str(e)}")

@router.delete("/{id}", dependencies=[Depends(get_db)], response_model=int)
async def delete_project_by_id(s: SessionDep, id: int):
	try:
		return await gen.delete_project_by_id(s, id)
	except SQLAlchemyError as e:
		s.rollback()
		raise HTTPException(status_code=500, detail=f"Error deleting project by id {id}: {str(e)}")

@router.delete("/owner/{id}", dependencies=[Depends(get_db)], response_model=List[int])
async def delete_projects_by_owner_id(s: SessionDep, owner_id: int):
	try:
		return await gen.delete_projects_by_owner_id(s, owner_id)
	except SQLAlchemyError as e:
		s.rollback()
		raise HTTPException(status_code=500, detail=f"Error deleting project by owner_id {id}: {str(e)}")

@router.put("/{id}", dependencies=[Depends(get_db)], response_model=int)
async def update_project_by_id(s: SessionDep, id: int, upd: ProjectUpdate = Body(...)):
	try:
		return await gen.update_project_by_id(s, id, upd)
	except SQLAlchemyError as e:
		s.rollback()
		raise HTTPException(status_code=500, detail=f"Error updating proejct by id {id}: {str(e)}")