""" FastAPI imports """
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
""" SQLModel imports"""
from sqlmodel import select
""" SQLAlchemy imports """
from sqlalchemy.exc import SQLAlchemyError
""" typing imports """
from typing import Any, Dict, List, Optional, Union
""" Internal imports """
from core.db import SessionDep, get_db
from services import general_service as gen
from models.db_models import TeamBase, TeamUpdate, Teams


""" APIRouter added to upper router(db/__init__.py) """
router = APIRouter(prefix="/teams", tags=["/teams"])

@router.get("/", dependencies=[Depends(get_db)], response_model=List[Teams])
async def get_all_teams(s: SessionDep):
	try:
		teams = await gen.get_all_teams(s)
		if teams is None:
			raise HTTPException(status_code=404, detail="Error getting teams")
		return teams
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error getting teams: {str(e)}")

@router.get("/project/{id}", dependencies=[Depends(get_db)], response_model=List[Teams])
async def get_team_by_project_id(s: SessionDep, id: int):
	try:
		teams = await gen.get_team_by_project_id(s, id)
		if teams is None:
			raise HTTPException(status_code=404, detail=f"Error getting team by id {id}")
		return teams
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error getting team by project_id {id}: {str(e)}")

@router.get("/{id}", dependencies=[Depends(get_db)], response_model=Teams)
async def get_team_by_id(s: SessionDep, id: int):
	try:
		team = await gen.get_team_by_id(s, id)
		if team is None:	
			raise HTTPException(status_code=404, detail=f"Error getting team by id {id}")
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error getting team by id {id}: {str(e)}")

@router.post("/", dependencies=[Depends(get_db)], response_model=int)
async def create_team(s: SessionDep, team: TeamBase):
	try:
		return await gen.create_team(s, team)
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error creating team: {str(e)}")

@router.post("/user", dependencies=[Depends(get_db)], response_model=int)
async def add_user_to_team(s: SessionDep, team: TeamBase):
	try:
		return await gen.add_user_to_team(s, team)
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error creating teams: {str(e)}")

@router.put("/user/{user_id}/project/{project_id}", dependencies=[Depends(get_db)], response_model=int)
async def update_team_by_user_id_and_project_id(
  s: SessionDep, user_id: int, project_id: int, upd: TeamUpdate
  ):
	try:
		return await gen.update_team_by_(s=s, user_id=user_id, project_id=project_id, upd=upd)
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error updating team by user_id {id}: {str(e)}")

@router.put("/{id}", dependencies=[Depends(get_db)], response_model=int)
async def update_team_by_id(s: SessionDep, id: int, upd: TeamUpdate):
	try:
		return await gen.update_team_by_(s=s, team_id=id, upd=upd)
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error updating team by team_id {id}: {str(e)}")

@router.delete("/user/{user_id}/project/{project_id}", dependencies=[Depends(get_db)], response_model=int)
async def delete_team_by_user_id_and_project_id(
  s: SessionDep, user_id: int, project_id: int
  ):
	try: return await gen.delete_team_by_(s, user_id=user_id, project_id=project_id)
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error deleting team by user_id {user_id} and project_id {project_id}: {str(e)}")

@router.delete("/{id}", dependencies=[Depends(get_db)], response_model=int)
async def delete_team_by_id(s: SessionDep, id: int):
	try:
		return await gen.delete_team_by_(s, team_id=id)
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error deleting team by id {id}: {str(e)}")