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
from models.db_models import TaskBase, TaskUpdate, Tasks, ReminderBase, ReminderUpdate, Reminders


""" APIRouter added to upper router(db/__init__.py) """
router = APIRouter(prefix="/tasks", tags=["/tasks"])

@router.get("/", dependencies=[Depends(get_db)], response_model=List[Tasks])
async def get_all_tasks(s: SessionDep):
	try:
		tasks = await gen.get_all_tasks(s)
		if tasks is None:
			raise HTTPException(status_code=404, detail="Error getting tasks")
		return tasks
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error getting tasks: {str(e)}")

@router.get("/project/{id}", dependencies=[Depends(get_db)], response_model=List[Tasks])
async def get_all_tasks_by_project_id(s: SessionDep, id: int):
	try:
		tasks = await gen.get_all_task_by_project_id(s, id)
		if tasks is None:
			raise HTTPException(status_code=404, detail=f"Error getting tasks by project_id {id}")
		return tasks
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Erorr getting tasks by project_id {id}: {str(e)}")

@router.get("/{id}", dependencies=[Depends(get_db)], response_model=Tasks)
async def get_task_by_id(s: SessionDep, id: int):
	try:
		task = await gen.get_task_by_id(s, id)
		if task is None:
			raise HTTPException(status_code=404, detail=f"Error getting tasks by project_id {id}")
		return task
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Erorr getting tasks by project_id {id}: {str(e)}")

@router.post("/", dependencies=[Depends(get_db)], response_model=int)
async def create_task(s: SessionDep, task: TaskBase, reminder: ReminderBase):
	try:
		await gen.create_remider(s, reminder)
		return await gen.create_task(s, task)
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")

@router.post("/bat/", dependencies=[Depends(get_db)], response_model=List[int])
async def create_tasks(s: SessionDep, tasks: List[TaskBase]):
	try:
		ids = await gen.create_tasks(s, tasks)
		if ids is None:
			raise HTTPException(status_code=404, detail="Error creation tasks")
		return ids
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error creating tasks: {str(e)}")

@router.put("/{id}", dependencies=[Depends(get_db)], response_model=int)
async def update_task_by_id(s: SessionDep, id: int, updTask: TaskUpdate, updReminder: ReminderUpdate):
	try:
		await gen.update_reminder_by_task_id(s, id, updReminder)
		return await gen.update_task_by_id(s, id, updTask)
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error updating task by id {id}: {str(e)}")

@router.delete("/{id}", dependencies=[Depends(get_db)], response_model=int)
async def delete_task_by_id(s: SessionDep, id: int):
	try:
		await gen.delete_reminder_by_task_id(s, id)
		return await gen.delete_task_by_id(s, id)
	except SQLAlchemyError as e:
		raise HTTPException(status_code=500, detail=f"Error deleting task by id {id}: {str(e)}")
