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
async def get_all_tasks_by_user_id(s: Session, user_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.user_id == user_id)
    return s.exec(query).all()

async def get_completed_tasks_by_user_id(s: Session, user_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.user_id == user_id, Tasks.status == TaskStatus.DONE)
    return s.exec(query).all()

async def get_tasks_in_progress_by_user_id(s: Session, user_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.user_id == user_id, Tasks.status == TaskStatus.IN_PROGRESS)
    return s.exec(query).all()

async def get_todo_tasks_by_user_id(s: Session, user_id: int) -> Sequence[Tasks]:
    query = select(Tasks).where(Tasks.user_id == user_id, Tasks.status == TaskStatus.TODO)
    return s.exec(query).all()

async def get_overdue_tasks_by_user_id(s: Session, user_id: int) -> Sequence[Tasks]:
    query_get_tasks = select(Tasks).where(Tasks.user_id == user_id, Tasks.status != TaskStatus.DONE and Tasks.deadline < datetime.now(timezone.utc))
    return s.exec(query_get_tasks).all()

async def get_task_allotted_time(task: Tasks) -> int:
    time = (task.deadline - task.created_at).total_seconds() / 3600
    return time

async def calculate_task_duration(task: Tasks) -> Dict:
    if task.status == TaskStatus.DONE:
        duration = (task.changed_at - task.created_at).total_seconds() / 3600
        return {"duration" : round(duration, 2), "is_done" : "true"}
    else:
        duration = (datetime.now() - task.created_at).total_seconds() / 3600 -2
        return {"duration" : round(duration, 2), "is_done" : "false"}

async def get_user_name_by_user_id(s: Session, user_id: int) -> str:
    query = select(Users).where(Users.id == user_id)
    user = s.exec(query).first()
    return user.name

async def get_most_time_duration_task(tasks: List[Tasks]) -> Optional[Tasks]:
    if not tasks:
        return {"error": "Нет задач для анализа", "title": None, "duration": 0.0}

    result = None
    result_duration = 0.0
    try:
        for task in tasks:
            res = await calculate_task_duration(task)

            if 'duration' not in res or not isinstance(res['duration'], (int, float)):
                continue

            task_duration = res['duration']

            if result is None or task_duration > result_duration:
                result_duration = task_duration
                result = task

        if result is None:
            return {"error": "Не удалось определить задачу", "title": None, "duration": 0.0}

        return {
            "title": result.title,
            "duration": result_duration,
            "error": None
        }

    except Exception as e:
        return {
            "error": f"Ошибка обработки: {str(e)}",
            "title": None,
            "duration": 0.0
        }

async def get_least_time_duration_task(tasks: List[Tasks]) -> Dict:
    if not tasks:
        return {"error": "Нет задач для анализа", "title": None, "duration": 0.0}

    result = None
    result_duration = 0.0

    try:
        for task in tasks:
            res = await calculate_task_duration(task)
            if 'duration' not in res or not isinstance(res['duration'], (int, float)):
                task_duration = res['duration']

            if result is None or task_duration < result_duration:
                result_duration = task_duration
                result = task

        if result is None:
            return {"error": "Не удалось определить задачу", "title": None, "duration": 0.0}

        return {
            "title": result.title,
            "duration": result_duration,
            "error": None
        }

    except Exception as e:
        return {
            "error": f"Ошибка обработки: {str(e)}",
            "title": None,
            "duration": 0.0
        }

async def get_developer_report(s: Session, user_id: int) -> Dict:
    tasks = await get_completed_tasks_by_user_id(s, user_id)
    overdue_tasks = await get_overdue_tasks_by_user_id(s, user_id)
    all_tasks = await get_all_tasks_by_user_id(s, user_id)
    total_in_progress_tasks = await get_tasks_in_progress_by_user_id(s, user_id)
    total_todo_tasks = await get_todo_tasks_by_user_id(s, user_id)
    developer_name = await get_user_name_by_user_id(s, user_id)
    total_time = 0.0

    dificult = await get_most_time_duration_task(tasks)
    easy = await get_least_time_duration_task(tasks)

    all_users_tasks_duration = {}

    tasks = await get_all_tasks_by_user_id(s, user_id)

    for task in tasks:
        task_info = await calculate_task_duration(task)
        all_users_tasks_duration[task.title] = {
            "duration": task_info['duration'],
            "is_done": task_info['is_done'],
            "allotted_time" : await get_task_allotted_time(task)
        }
        total_time += task_info['duration']

    return {
        "developer_id": user_id,
        "developer_name" : developer_name,
        "all_tasks" : len(all_tasks),
        "total_completed_tasks": len(tasks),
        "total_in_progress_tasks": len(total_in_progress_tasks),
        "total_todo_tasks" : len(total_todo_tasks),
        "total_overdue_tasks" : len(overdue_tasks),
        "all_users_tasks_duration": all_users_tasks_duration,
        "most_dificult_task": dificult,
        "the_easiest_task" : easy,
        "total_hours_worked": round(total_time, 2),
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
        return {"name": "Нет разработчиков", "quantity": 0}
    else:
        for user in users:
            quantity = len(await get_completed_tasks_by_user_id(s, user.id))

            if quantity > max_task_quantity:
                max_task_quantity = quantity
                developer = user

    if developer == None:
        return {"name": "Не определено", "quantity": 0}

    return {"name" : developer.name, "quantity" : max_task_quantity}

async def get_most_flawed_developer(s: Session, users: List[Users]) -> Optional[Dict]:
    max_task_quantity = 100000
    developer = None

    if users is None:
        return {"name": "Нет разработчиков", "quantity": 0}
    else:
        for user in users:
            quantity = len(await get_overdue_tasks_by_user_id(s, user.id))

            if quantity < max_task_quantity:
                max_task_quantity = quantity
                developer = user

    if developer == None:
        return {"name": "Не определено", "quantity": 0}

    return {"name" : developer.name, "quantity" : max_task_quantity}

async def get_most_valuable_developer(s: Session, users: List[Users]) -> Optional[Dict]:
    if not Users:
        return None

    max_effectiveness = 0
    developer = None
    has_valid_developers = False

    for user in users:
        overdue_quantity = len(await get_overdue_tasks_by_user_id(s, user.id))
        quantity = len(await get_all_tasks_by_user_id(s, user.id))

        if quantity == 0:
            continue

        effectiveness = 100 - ((overdue_quantity/quantity) * 100)
        has_valid_developers = True

        if max_effectiveness <= effectiveness:
            max_effectiveness = effectiveness
            developer = user

    if not has_valid_developers or developer is None:
        return {"name": "Не определено", "effectiveness": 0}

    return {"name" : developer.name, "effectiveness" : max_effectiveness}

async def get_project_report(s: Session, project_id: int) -> Dict:
    project_title = await get_project_title_by_project_id(s, project_id)
    total_quantity_of_tasks = len(await get_all_tasks_by_project_id(s, project_id))
    quantity_of_compleated_tasks = len(await get_compleated_tasks_by_project_id(s, project_id))
    quantity_of_tasks_in_progress = len(await get_tasks_in_progress_by_project_id(s, project_id))
    quantity_of_todo_tasks = len(await get_todo_tasks_by_project_id(s, project_id))
    quantity_of_overdue_tasks = len(await get_overdue_tasks_by_project_id(s, project_id))

    users = await get_developers_by_project_id(s, project_id)
    print(users)
    most_valuable_developer = await get_most_valuable_developer(s, users)
    most_productive_developer = await get_most_productive_developer(s, users)
    most_flawed_developer = await get_most_flawed_developer(s, users)

    all_tasks_in_project_with_duration = {}
    tasks = await get_all_tasks_by_project_id(s, project_id)
    for task in tasks:
        task_info = await calculate_task_duration(task)
        all_tasks_in_project_with_duration[task.title] = {
            "duration": task_info['duration'],
            "is_done": task_info['is_done'],
            "allotted_time" : await get_task_allotted_time(task)
        }


    return {
        "project_id" : project_id,
        "project_title" : project_title,
        "total_quantity_of_tasks" : total_quantity_of_tasks,
        "quantity_of_completed_tasks" : quantity_of_compleated_tasks,
        "quantity_of_tasks_in_progress" : quantity_of_tasks_in_progress,
        "quantity_of_todo_tasks" : quantity_of_todo_tasks,
        "quantity_of_overdue_tasks" : quantity_of_overdue_tasks,
        "most_valuable_developer" : most_valuable_developer,
        "most_productive_developer" : most_productive_developer,
        "most_flawed_developer" : most_flawed_developer,
        "all_tasks_in_project_with_duration" : all_tasks_in_project_with_duration
    }
