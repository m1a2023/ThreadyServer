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
from models.db_models import ReminderBase, ReminderUpdate, Reminders


""" APIRouter added to upper router(db/__init__.py) """
router = APIRouter(prefix="/reminders", tags=["/reminders"])

@router.get("/", dependencies=[Depends(get_db)], response_model=List[Reminders])
async def get_all_reminders(s: SessionDep):
    try:
        reminders = await gen.get_all_reminders(s)
        if reminders is None:
            raise HTTPException(status_code=404, detail="Error getting reminders")
        return reminders
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error getting remiders: {str(e)}")

@router.get("/bat/", dependencies=[Depends(get_db)], response_model=List[Reminders])
async def get_reminders_by_project_ids(s: SessionDep, project_ids: List[int] = Query(...)):
    try:
        reminders = await gen.get_reminders_by_project_ids(s, project_ids)
        if reminders is None:
            raise HTTPException(status_code=404, detail="Error getting reminders by IDs")
        return reminders
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Error getting reminders by IDs: {str(e)}")

@router.delete("/{task_id}", dependencies=[Depends(get_db)], response_model=int)
async def delete_reminder_by_task_id(s: SessionDep, task_id: int):
    try:
        return await gen.delete_reminder_by_task_id(s, task_id)
    except SQLAlchemyError as e:
	    raise HTTPException(status_code=500, detail=f"Error deleting task by id {id}: {str(e)}")
