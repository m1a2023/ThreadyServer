""" SQLModel imports """
from sqlalchemy import ColumnElement
from sqlmodel import Session, and_, select
""" typing imports """
from typing import List, Optional, Sequence, Type, TypeVar, Union, Dict
""" datetime imports """
from datetime import datetime, timezone
""" Internal imports """
from core import db
from core.db import SessionDep
from models.db_models import (
  ProjectBase,
  ProjectUpdate,
  TaskBase,
  TaskUpdate,
  Tasks,TaskStatus, TeamBase,
  TeamRoles,
  TeamUpdate,
  Teams,
  UserBase, Users, Projects
)

""" Util """
async def is_present_by_id(s: SessionDep, table: type, id: int) -> bool:
	return s.exec(select(table).where(table.id == id)).first() is not None

"""Get report on developer"""

async def get_completed_tasks_by_user_id(s: Session, user_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.user_id == user_id, Tasks.status == TaskStatus.DONE)
    return s.exec(query).all()

async def get_overdue_tasks_by_user_id(s: Session, user_id: int) -> Sequence[Tasks]:
    query_get_tasks = select(Tasks).where(Tasks.user_id == user_id, Tasks.status != TaskStatus.DONE and Tasks.deadline < datetime.now(timezone.utc))
    #query_get_overdue_duration = select(Tasks.deadline)
    return s.exec(query_get_tasks).all()

async def get_all_tasks_by_user_id(s: Session, user_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.user_id == user_id)
    return s.exec(query).all()

async def calculate_task_duration(task: Tasks) -> Optional[float]:
    if task.status == TaskStatus.DONE and task.changed_at:
        duration = (task.changed_at - task.created_at).total_seconds() / 3600
        return round(duration, 2)
    return None

async def get_user_name_by_user_id(s: Session, user_id: int) -> str:
    query = select(Users).where(Users.id == user_id)
    user = s.exec(query).first()
    return user.name

async def get_most_time_duration_task(tasks: List[Tasks]) -> Optional[Tasks]:
    result = None
    result_duration = 0.0
    for task in tasks:
        task_duration = await calculate_task_duration(task)
        if result == None:
            result_duration = task_duration
            result = task
        else:
            if result_duration < task_duration:
                result_duration = task_duration
                result = task
    return {result.title : result_duration}

async def get_least_time_duration_task(tasks: List[Tasks]) -> Dict:
    result = None
    result_duration = 0.0
    for task in tasks:
        task_duration = await calculate_task_duration(task)
        if result == None:
            result_duration = task_duration
            result = task
        else:
            if result_duration > task_duration:
                result_duration = task_duration
                result = task
    return {result.title : result_duration}

async def get_developer_report(s: Session, user_id: int) -> Dict:
    tasks = await get_completed_tasks_by_user_id(s, user_id)
    overdue_tasks = await get_overdue_tasks_by_user_id(s, user_id)
    developer_name = await get_user_name_by_user_id(s, user_id)
    total_time = 0.0
    task_durations = {}

    dificult = await get_most_time_duration_task(tasks)
    easy = await get_least_time_duration_task(tasks)

    for task in tasks:
        duration = await calculate_task_duration(task)
        if duration:
            task_durations[task.id] = duration
            total_time += duration

    return {
        #еще можно разделить список просроченных задач на выолненые/невыполненые
        #и писать на сколько конкретно они просрочены
        "developer_id": user_id,
        "developer_name" : developer_name,
        "total_completed_tasks": len(tasks),
        "total_overdue_tasks" : len(overdue_tasks),
        "compleated_task_durations": task_durations,
        "most dificult task": dificult,
        "the easiest task" : easy,
        "total_hours_worked": round(total_time, 2)
    }

"""Get report on project"""
async def get_project_title_by_project_id(s:Session, project_id: int) -> str:
    query = select(Projects).where(Projects.id == project_id)
    project = s.exec(query).first()
    return project.title

async def get_developers_by_project_id(s: Session, project_id: int) -> Sequence[Users]:
    query = select(Users).join(Teams, Teams.user_id == Users.id).where(Teams.project_id == project_id)
    return s.exec(query).all()

async def get_all_tasks_by_project_id(s: Session, project_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.project_id == project_id)
    return s.exec(query).all()

async def get_compleated_tasks_by_project_id(s: Session, project_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.project_id == project_id, Tasks.status == TaskStatus.DONE)
    return s.exec(query).all()

async def get_tasks_in_progress_by_project_id(s: Session, project_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.project_id == project_id, Tasks.status == TaskStatus.IN_PROGRESS)
    return s.exec(query).all()

async def get_todo_tasks_by_project_id(s: Session, project_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.project_id == project_id, Tasks.status == TaskStatus.TODO)
    return s.exec(query).all()

async def get_overdue_tasks_by_project_id(s: Session, project_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.project_id == project_id, Tasks.status != TaskStatus.DONE and Tasks.deadline < datetime.now(timezone.utc))
    return s.exec(query).all()

async def get_most_productive_developer(s: Session, users: List[Users]) -> Optional[Dict]:
    max_task_quantity = 0
    developer = None

    if users is None:
        return None
    else:
        for user in users:
            quantity = len(await get_completed_tasks_by_user_id(s, user.id))

            if quantity > max_task_quantity:
                max_task_quantity = quantity
                developer = user

    return {developer.name : max_task_quantity}

async def get_most_flawed_developer(s: Session, users: List[Users]) -> Optional[Dict]:
    max_task_quantity = 100000
    developer = None

    if users is None:
        return None
    else:
        for user in users:
            quantity = len(await get_overdue_tasks_by_user_id(s, user.id))

            if quantity < max_task_quantity:
                max_task_quantity = quantity
                developer = user

    return {developer.name : max_task_quantity}

async def get_most_valuable_developer(s: Session, users: List[Users]) -> Optional[Dict]:
    if not Users:
        return None

    max_effectiveness = 0
    developer = None

    for user in users:
        overdue_quantity = len(await get_overdue_tasks_by_user_id(s, user.id))
        quantity = len(await get_all_tasks_by_user_id(s, user.id))
        effectiveness = 100 - ((overdue_quantity/quantity) * 100)

        if max_effectiveness <= effectiveness:
            max_effectiveness = effectiveness
            developer = user

    return {developer.name : max_effectiveness}

async def get_project_report(s: Session, project_id: int) -> Dict:
    project_title = await get_project_title_by_project_id(s, project_id)
    total_quantity_of_tasks = len(await get_all_tasks_by_project_id(s, project_id))
    quantity_of_compleated_tasks = len(await get_compleated_tasks_by_project_id(s, project_id))
    quantity_of_tasks_in_progress = len(await get_tasks_in_progress_by_project_id(s, project_id))
    quantity_of_todo_tasks = len(await get_todo_tasks_by_project_id(s, project_id))
    quantity_of_overdue_tasks = len(await get_overdue_tasks_by_project_id(s, project_id))

    users = await get_developers_by_project_id(s, project_id)
    most_valuable_developer = await get_most_valuable_developer(s, users)
    most_productive_developer = await get_most_productive_developer(s, users)
    most_flawed_developer = await get_most_flawed_developer(s, users)

    return {
        "project_id" : project_id,
        "project_title" : project_title,
        "total_quantity_of_tasks" : total_quantity_of_tasks,
        "quantity_of_compleated_tasks" : quantity_of_compleated_tasks,
        "quantity_of_tasks_in_progress" : quantity_of_tasks_in_progress,
        "quantity_of_todo_tasks" : quantity_of_todo_tasks,
        "quantity_of_overdue_tasks" : quantity_of_overdue_tasks,
        "most_valuable_developer" : most_valuable_developer,
        "most_productive_developer" : most_productive_developer,
        "most_flawed_developer" : most_flawed_developer
    }
