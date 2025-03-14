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
from src.models.db_models import ProjectBase, ProjectUpdate, TaskBase, Tasks, Users, Projects

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

async def create(s: SessionDep, entities: T) -> Union[T, List[T]]:
	s.add(entities) 
	s.commit()
	s.refresh(entities)
	return entities 

# async def update(entity: T, table: Type[T])
# async def delete()

#*
#*  Users table
#*

""" GET """
async def get_all_users(s: SessionDep) -> Optional[Sequence[Users]]:
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
async def create_user(s: SessionDep, user: Users) -> int:
	s.add(user)
	s.commit()
	s.refresh(user)
	return user.id

async def create_users(s: SessionDep, users: Union[List[Users], Sequence[Users]]) -> Sequence[int]:
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
	project = s.exec(query).first()
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
	
	project.changed_at = datetime.now(timezone.utc)
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

# async def create_tasks(tasks: Union[List[Tasks], Sequence[Tasks]]) -> :
  