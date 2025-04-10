""" SQLModel imports """
from enum import StrEnum
from sqlalchemy import ColumnElement
from sqlmodel import Session, and_, asc, between, desc, select, col
#from sympy import ExactQuotientFailed
""" typing imports """
from typing import List, Optional, Sequence, Type, TypeVar, Union
""" datetime imports """
from datetime import datetime, timezone
""" Internal imports """
from core import db
from core.db import SessionDep
from models.db_models import (
  Context,
  ContextBase,
  Errors,
  MessageRole,
  PlanBase,
  Plans,
  ProjectBase,
  ProjectUpdate,
  PromptTitle,
  TaskBase,
  TaskUpdate,
  Tasks, TeamBase,
  TeamRoles,
  TeamUpdate,
  Teams,
  UserBase, Users, Projects,
  ReminderBase, ReminderUpdate, Reminders
)

""" Util """
async def is_present_by_id(s: SessionDep, table: type, id: int) -> bool:
	return s.exec(select(table).where(table.id == id)).first() is not None

async def is_admin(s: SessionDep, user_id: int, project_id: int) -> bool:
	user = (s.exec(
			select(Teams)
   		.where(and_(Teams.user_id == user_id, Teams.project_id == project_id)))
			.first())
	if user:
		return user.role == TeamRoles.ADMIN
	return False


class SortBy(StrEnum):
	LATEST = 'latest'
	NONE = 'none'
	OLDER = 'older'


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
	query = select(Users).where(col(Users.id).in_(ids))
	users = s.exec(query).all()
	return users

""" CREATE """
async def create_user(s: SessionDep, user: UserBase) -> int:
	user = Users(**user.model_dump())
	s.add(user)
	s.commit()
	s.refresh(user)
	return user.id

async def create_users(s: SessionDep, users: Union[List[UserBase], Sequence[UserBase]]) -> Sequence[int]:
	ids: List[int] = []
	parsed_users: List[Users] = []

	for user in users:
			user_obj = Users(**user.model_dump())
			parsed_users.append(user_obj)
	s.add_all(parsed_users)
	s.commit()
	for user in parsed_users:
		s.refresh(user)
		ids.append(user.id)
	return ids

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

async def get_projects_by_owner_id(s: SessionDep, owner_id: int) -> Optional[Sequence[Projects]]:
	return s.exec(select(Projects).where(Projects.owner_id == owner_id)).all()

# async def get_projects_by_id_where_user_is_admin(s: SessionDep, id: int) -> Optional[Projects]:
# 	return s.exec(select(Projects).where(Projects.id == id)).first()

# async def get_project_by_id(s: SessionDep, id: int) -> Optional[Projects]:
# 	return s.exec(select(Projects).where(Projects.id == id)).first()

async def get_project_by_id(s: SessionDep, id: int) -> Optional[Projects]:
	return s.exec(select(Projects).where(Projects.id == id)).first()

async def get_projects_by_user_id(s: SessionDep, id: int) -> Sequence[Projects]:
	q = select(Teams).where(Teams.user_id == id)
	teams = s.exec(q).all()

	_ids = [ ]
	for team in teams:
		_ids.append(team.project_id)

	q = select(Projects)
	projects = s.exec(q.where(col(Projects.id).in_(_ids))).all()

	return projects


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

async def delete_projects_by_owner_id(s: SessionDep, owner_id: int) -> Sequence[int]:
		proj_ids: List[int]
		query = select(Projects).where(Projects.owner_id == owner_id)
		projects = s.exec(query).all()
		proj_ids = [ proj.id for proj in projects ]
		s.delete(projects)
		s.commit()
		return proj_ids

""" UPDATE """
async def update_project_by_id(s: SessionDep, project_id: int, update: ProjectUpdate) -> int:
	query = select(Projects).where(Projects.id == project_id)
	project = s.exec(query).one()

	if update.title is not None:
		project.title = update.title
	if update.description is not None:
		project.description = update.description
	if update.repo_link is not None:
		project.repo_link = update.repo_link
	if update.chat_link is not None:
		project.chat_link = update.chat_link

	s.commit()
	s.refresh(project)
	return project.id


#*
#*	Tasks table
#*
""" GET """
async def get_all_tasks(s: SessionDep) -> Sequence[Tasks]:
	return s.exec(select(Tasks)).all()

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
	_tasks = [ Tasks(**_task.model_dump()) for _task in tasks ]
	_ids: List[int] = [ ]
	s.add_all(_tasks)
	s.commit()

	for task in _tasks:
		s.refresh(task)
		_ids.append(task.id)
	return tuple(_ids)

""" UPDATE """
async def update_task_by_id(s: SessionDep, task_id: int, upd: TaskUpdate) -> int:
	q = select(Tasks).where(Tasks.id == task_id)
	task = s.exec(q).first()

	if task:
		if upd.title: task.title = upd.title
		if upd.description: task.description = upd.description
		if upd.deadline: task.deadline = upd.deadline
		if upd.priority: task.priority = upd.priority
		if upd.status: task.status = upd.status
		if upd.user_id: task.user_id = upd.user_id
		task.changed_at = datetime.now(timezone.utc)
	else:
		return -1

	s.commit()
	s.refresh(task)
	return task.id

""" DELETE """
async def delete_task_by_id(s: SessionDep, task_id: int) -> int:
	q = select(Tasks).where(Tasks.id == task_id)
	task = s.exec(q).one()
	s.delete(task)
	s.commit()
	return task_id


#*
#*	Teams table
#*
""" GET """
async def get_all_teams(s: SessionDep) -> Sequence[Teams]:
	return s.exec(select(Teams)).all()

async def get_team_by_project_id(s: SessionDep, project_id: int) -> Sequence[Teams]:
	return s.exec(select(Teams).where(Teams.project_id == project_id)).all()

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
	s: SessionDep, upd: TeamUpdate,
	user_id: Optional[int] = None, project_id: Optional[int] = None,
	team_id: Optional[int] = None
  ) -> int:
	q = select(Teams)
	if user_id is not None:
		q = q.where(and_(Teams.user_id == user_id, Teams.project_id == project_id))
	if team_id is not None:
		q = q.where(Teams.id == team_id)

	team = s.exec(q).one()
	team.role = upd.role

	s.commit()
	s.refresh(team)
	return team.id

""" DELETE """
async def delete_team_by_(
  s: SessionDep,
  user_id: Optional[int] = None, project_id: Optional[int] = None,
  team_id: Optional[int] = None
  ) -> int:
	ret_id: int = -1
	if user_id is not None:
		q = select(Teams).where(and_(Teams.user_id == user_id, Teams.project_id == project_id))
	if team_id is not None:
		q = select(Teams).where(Teams.id == team_id)
	team = s.exec(q).first()
	if team is not None:
		ret_id = team.id
	s.delete(team)
	s.commit()
	return ret_id


#*
#*  Context table
#*
""" GET """
async def get_context_by_project_id(
	s: SessionDep,
	project_id: int,
	action: PromptTitle,
	context_depth: int
) -> List[dict]:
	""" Gets the latest messages with specified depth """
	query = select(Context)
	_context = [ ]

	""" query based on needed action """
	if action in [PromptTitle.PLAN, PromptTitle.RE_PLAN, PromptTitle.TASK]:
		query = query.where(and_(Context.project_id == project_id, Context.action == 'plan'))
	if action in [PromptTitle.RE_TASK, PromptTitle.DIV_TASK]:
		query = query.where(and_(Context.project_id == project_id, Context.action == 'task'))

	""" gets context """
	contexts = s.exec(query.order_by(desc(Context.changed_at)).limit(context_depth)).all()
	""" building context list """
	for context in contexts:
		_context.append({'role': context.role, 'text': context.message})
	return _context


""" CREATE """
async def create_context(
	s: SessionDep,
	context: ContextBase
) -> int:
	_context = Context(**context.model_dump())
	s.add(_context)
	s.commit()
	s.refresh(_context)
	return _context.project_id

#*
#*	Plan table
#*
""" GET """
async def get_plans_by_project_id(
	s: SessionDep,
	project_id: int,
	sort: Optional[SortBy] = SortBy.LATEST,
	limit: Optional[int] = 3
) -> Sequence[Plans]:
	q = (select(Plans)
			.where(Plans.project_id == project_id))
	if limit:
		q = q.limit(limit)

	match sort:
		case SortBy.LATEST:
			q = q.order_by(desc(Plans.created_at))
		case SortBy.OLDER:
			q = q.order_by(asc(Plans.created_at))

	plans = s.exec(q).all()
	return plans

""" CREATE """
async def create_plan(
	s: SessionDep,
	plan: PlanBase
) -> int:
	plan = Plans(**plan.model_dump())
	s.add(plan)
	s.commit()
	s.refresh(plan)
	return plan.id

#*
#* Reminders table
#*

async def get_all_reminders(s: SessionDep) -> Sequence[Reminders]:
	return s.exec(select(Reminders)).all()

async def get_reminders_by_project_ids(s: SessionDep, project_ids: Union[List[int], Sequence[int]]) -> Sequence[Reminders]:
	query = select(Reminders).where(col(Reminders.project_id).in_(project_ids))
	reminders = s.exec(query).all()
	return reminders

async def create_remider(s: SessionDep, reminder: ReminderBase) -> int:
	reminder = Reminders(**reminder.model_dump())
	s.add(reminder)
	s.commit()
	s.refresh(reminder)
	return reminder.task_id

async def create_remiders(s: SessionDep, reminders: List[ReminderBase]) -> Sequence[int]:
	reminders = [ Reminders(**reminder.model_dump()) for reminder in reminders ]
	s.add_all(reminders)
	s.commit()
	_ids: List[int] = [ ]

	for rem in reminders:
		s.refresh(rem)
		_ids.append(rem.task_id)
	return tuple(_ids)

async def update_reminder_by_task_id(s: SessionDep, task_id: int, upd: ReminderUpdate) -> int:
	q = select(Reminders).where(Reminders.task_id == task_id)
	rem = s.exec(q).one()

	if rem:
		if upd.title: rem.title = upd.title
		if upd.send_time: rem.send_time = upd.send_time
		if upd.user_id: rem.user_id = upd.user_id
	else:
		return -1

	rem.changed_at = datetime.now(timezone.utc)
	s.commit()
	s.refresh(rem)
	return rem.task_id

async def delete_reminder_by_task_id(s: SessionDep, task_id: int) -> int:
	q = select(Reminders).where(Reminders.task_id == task_id)
	reminder = s.exec(q).one()
	s.delete(reminder)
	s.commit()
	return task_id

async def exist_reminder_by_task_id(s: SessionDep, task_id: int) ->bool:
	q = select(Reminders).where(Reminders.task_id == task_id)
	reminder = s.exec(q).first()
	if reminder:
		return True
	else:
		return False
