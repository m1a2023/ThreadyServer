""" FastAPI imports """
from re import L
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
""" SQLModel imports"""
from sqlmodel import select
""" SQLAlchemy imports """
from sqlalchemy.orm.exc import UnmappedInstanceError
""" typing imports """
from typing import Any, Dict, List, Optional, Union
""" Internal imports """
from core.db import SessionDep, get_db
from services import general_service as gen
from models.db_models import ProjectBase, ProjectUpdate, Projects


""" APIRouter added to upper router(db/__init__.py) """
router = APIRouter(prefix="/projects", tags=["/projects"])

@router.get("/", dependencies=[Depends(get_db)], response_model=Union[List[Projects], Dict])
async def get_all_projects(s: SessionDep):
	return await gen.get_all_projects(s)

@router.get("/{id}", dependencies=[Depends(get_db)], response_model=Union[Projects, Dict])
async def get_project_by_id(s: SessionDep, id: int):
	project = await gen.get_project_by_id(s, id)
	if project is None:
		raise HTTPException(status_code=404, detail=f"Project with id {id} doesn't exist")
	return project

@router.get("/owner/{id}", dependencies=[Depends(get_db)], response_model=Union[List[Projects], Dict])
async def get_projects_by_owner_id(s: SessionDep, id: int):
	projects = await gen.get_projects_by_owner_id(s, id)
	if projects is None:
		raise HTTPException(status_code=404, detail=f"Project with owner_id {id} doesn't exist")
	return projects

@router.post("/", dependencies=[Depends(get_db)], response_model=Union[int, Dict])
async def create_project(s: SessionDep, project: ProjectBase):
	id = await gen.create_project(s, project)
	return id

@router.delete("/{id}", dependencies=[Depends(get_db)], response_model=int)
async def delete_project_by_id(s: SessionDep, id: int):
	id = await gen.delete_project_by_id(s, id)
	if id is None:
		return { "error" : "deleting project process has crashed" }
	return id

@router.delete("/owner/{id}}", dependencies=[Depends(get_db)], response_model=List[int])
async def delete_projects_by_owner_id(s: SessionDep, owner_id: int):
	ids = await gen.delete_projects_by_owner_id(s, owner_id)
	if id is None:
		return { "error" : "deleting project procecess has crashed" }	
	return ids

@router.put("/{id}", dependencies=[Depends(get_db)], response_model=int)
async def update_project_by_id(s: SessionDep, project_id: int, upd: ProjectUpdate):
	id =  await gen.update_project_by_id(s, project_id, upd)
	if id is None:
		return { "error" : "updating project has crasged" }
	return id
