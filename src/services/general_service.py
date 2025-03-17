""" SQLModel imports """
from sqlalchemy import ColumnElement
from sqlmodel import Session, select
""" typing imports """
from typing import List, Optional, Sequence, Type, TypeVar, Union
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
  Tasks, TeamBase, 
  TeamRoles, 
  TeamUpdate, 
  Teams,
  UserBase, Users, Projects
)

""" Util """
async def is_present_by_id(s: SessionDep, table: type, id: int) -> bool:
	return s.exec(select(table).where(table.id == id)).first() is not None

""" GET """
T = TypeVar("T")
async def get( 
			s: SessionDep,
			table: Type[T], 
			filters: Optional[List[ColumnElement]],
			single: bool
		) -> Optional[Union[T, Sequence[T]]]:
		q = select(table)
		if filters:
			q = q.where(*filters)
		
		result = s.exec(q)
		return result.first() if single else result.all()

""" CREATE """
async def create(s: SessionDep, entities: T) -> Union[T, List[T]]:
	s.add(entities) 
	s.commit()
	s.refresh(entities)
	return entities

""" UPDATE """
""" DELETE """

#*
#*  Users table
#*

""" GET """
async def get_all_users(s: SessionDep) -> Sequence[Users]:
	return s.exec(select(Users)).all()

async def get_user_by_id(s: SessionDep, id: int) -> Optional[Users]:
	return s.exec(select(Users).where(Users.id == id)).first()

async def get_users_by_ids(
		s: SessionDep, ids: Union[List[int], Sequence[int]]
  ) -> Sequence[Users]:
	users: Sequence[Users] = []
	for id in ids: 
		user = await get_user_by_id(s=s, id=id)
		if user: 
			users.append(user)
	return users 

""" CREATE """
async def create_user(s: SessionDep, user: UserBase) -> int:
	s.add(user)
	s.commit()
	s.refresh(user)
	return user.id

async def create_users(s: SessionDep, users: Union[List[UserBase], Sequence[UserBase]]) -> Sequence[int]:
	_users: List[int] = []
	for user in users:
		s.add(user)
		s.commit()
		s.refresh(user)
		_users.append(user.id)
	return _users

""" DELETE """
async def delete_user_by_id(s: SessionDep, id: int) -> int:
	query = select(Users).where(Users.id == id)
	user = s.exec(query).first()
	s.delete(user)
	s.commit()
	return id 


#*
#*  Projects table
#*

""" GET """
async def get_all_projects(s: SessionDep) -> Sequence[Projects]:
	return s.exec(select(Projects)).all()

async def get_all_projects_by_user(s: SessionDep, user: Users) -> Sequence[Projects]:
	return s.exec(select(Projects).where(Projects.owner_id == user.id)).all()

async def get_all_projects_owner_id(s: SessionDep, owner_id: int) -> Sequence[Projects]:
	return s.exec(select(Projects).where(Projects.owner_id == owner_id)).all()

async def get_project_by_id(s: SessionDep, id: int) -> Optional[Projects]:
	return s.exec(select(Projects).where(Projects.id == id)).first()

""" CREATE """
async def create_project(s: SessionDep, project: ProjectBase) -> int:
	project = Projects(**project.model_dump())
	s.add(project)
	s.commit()
	s.refresh(project)
	return project.id

""" DELETE """
async def delete_project_by_id(s: SessionDep, project_id: int) -> int:
	query = select(Projects).where(Projects.id == project_id)
	project = s.exec(query).one()
	s.delete(project)
	s.commit()
	return project_id

async def delete_projects_by_user(s: SessionDep, user: Users) -> Sequence[int]:
		proj_ids: List[int]
		query = select(Projects).where(Projects.owner_id == user.id)
		projects = s.exec(query).all()
		proj_ids = [ proj.id for proj in projects ]
		s.delete(projects)
		s.commit()
		return proj_ids 

""" UPDATE """
async def update_project_by_id(s: SessionDep, update: ProjectUpdate, project_id: int) -> int:
	query = select(Projects).where(Projects.id == project_id)
	project = s.exec(query).one()
	
	if update.new_title is not None:
		project.title = update.new_title
	if update.new_description is not None: 
		project.description = update.new_description
	
	s.commit()
	s.refresh(project) 
	return project.id
	

#*
#*	Tasks table
#* 
""" GET """
async def get_all_task_by_project_id(s: SessionDep, project_id: int) -> Sequence[Tasks]:
	return s.exec(select(Tasks).where(Tasks.project_id == project_id)).all()

async def get_task_by_id(s: SessionDep, id: int) -> Optional[Tasks]:
	return s.exec(select(Tasks).where(Tasks.id == id)).first()
  
""" CREATE """
async def create_task(s: SessionDep, task: TaskBase) -> int:
	task = Tasks(**task.model_dump())
	s.add(task)
	s.commit()
	s.refresh(task)
	return task.id

async def create_tasks(s: SessionDep, tasks: Union[List[TaskBase], Sequence[TaskBase]]) -> Sequence[int]:
	tasks = [ Tasks(**_task.model_dump()) for _task in tasks ]
	s.add_all(tasks)
	s.commit()
	s.refresh(tasks)
	return tuple( task.id for task in tasks )

""" UPDATE """
async def update_task(s: SessionDep, task_id: int, upd: TaskUpdate) -> int:
	q = select(Tasks).where(Tasks.id == task_id)
	task = s.exec(q).one()
	
	if upd.new_title is not None:
		task.title = upd.new_title
	if upd.new_description is not None:
		task.description = upd.new_description
	if upd.new_deadline is not None:
		task.deadline = upd.new_deadline
	if upd.new_priority is not None:
		task.priority = upd.new_priority
	if upd.new_status is not None:
		task.status = upd.new_status
	if upd.new_user_id is not None:
		task.user_id = upd.new_user_id
	
	s.commit()
	s.refresh(task)
	return task.id

""" DELETE """
async def delete_task(s: SessionDep, task_id: int) -> int:
	q = select(Tasks).where(Tasks.id == task_id)
	task = s.exec(q).one()
	s.delete(task)
	s.commit()
	return task_id


#*
#*	Teams table 
#* 
""" GET """
async def get_team_by_project_id(s: SessionDep, project_id: int) -> Teams:
	return s.exec(select(Teams).where(Teams.project_id == project_id)).one()

async def get_team_by_id(s: SessionDep, id: int) -> Teams:
	return s.exec(select(Teams).where(Teams.id == id)).one()

""" CREATE """
async def create_team(s: SessionDep, team: TeamBase) -> int:
	team = Teams(**team.model_dump())
	s.add(team)
	s.commit()
	s.refresh(team)
	return team.id

async def add_user_to_team(s: SessionDep, team: TeamBase) -> int:
	team = Teams(**team.model_dump())
	team.role = TeamRoles.USER
	s.add(team)
	s.commit()
	s.refresh(team)
	return team.id

""" UPDATE """
async def update_team_by_(
  s: SessionDep, project_id: Optional[int], team_id: Optional[int], upd: TeamUpdate
  ) -> int:
	q = select(Teams)
	if project_id is not None: 
		q = q.where(Teams.project_id == project_id)
	if team_id is not None:
		q = q.where(Teams.id == team_id)
	
	team = s.exec(q).one()
	team.role = upd.role
	
	s.commit()
	s.refresh(team)
	return team.id

""" DELETE """
async def delete_team_by_(s: SessionDep, team_id: int) -> int:
	q = select(Teams).where(Teams.id == team_id)
	team = s.exec(q).one()
	s.delete(team)
	s.commit()
	return team_id