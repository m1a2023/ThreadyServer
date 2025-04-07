""" SQLModel imports """
from sqlalchemy import JSON, BigInteger, Column, ForeignKey
from sqlmodel import Field, Relationship, SQLModel
""" typing imports """
from typing import Optional, List
""" datetime imports """
from datetime import datetime, timezone
""" enum imports """
from enum import Enum, StrEnum


""" Tables start here """

class Errors(StrEnum):
	DOES_NOT_EXIST = 'DOES_NOT_EXIST'
	NO_ACCESS = 'NO_ACCESS'


""" Users table """
class UserBase(SQLModel):
	id: int = Field(default=None, sa_column=Column(BigInteger(), primary_key=True, autoincrement=True))
	name: str = Field(index=True, max_length=255)

class Users(UserBase, table=True):
	created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
	projects: List["Projects"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
	tasks: List["Tasks"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
	team: List["Teams"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


""" Projects table """
class ProjectBase(SQLModel):
	title: str = Field(index=True, max_length=128)
	description: Optional[str] = Field(default=None, max_length=1024)
	chat_link: Optional[str] = Field(default=None, max_length=256)
	repo_link: Optional[str] = Field(default=None, max_length=256)
	owner_id: int = Field(default=None, sa_column=Column(BigInteger(), ForeignKey('users.id')))

class ProjectUpdate(SQLModel):
	title: Optional[str] = Field(default=None, max_length=128)
	description: Optional[str] = Field(default=None, max_length=1024)
	repo_link: Optional[str] = Field(default=None, max_length=256)
	chat_link: Optional[str] = Field(default=None, max_length=256)
	changed_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class Projects(ProjectBase, table=True):
	id: int = Field(default=None, sa_column=Column(BigInteger(), primary_key=True, autoincrement=True))
	created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
	changed_at: Optional[datetime] = Field(default=None)
	user: "Users" = Relationship(back_populates="projects", sa_relationship_kwargs={"lazy": "joined"})
	tasks: List["Tasks"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
	team: List["Teams"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
	context: "Context" = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
	plans: "Plans" = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})


""" Tasks table """
class TaskPriority(StrEnum):
	LOW = "low"
	MEDIUM = "medium"
	HIGH = "high"

class TaskStatus(StrEnum):
	TODO = "todo"
	IN_PROGRESS = "in_progress"
	DONE = "done"

class TaskBase(SQLModel):
	title: str = Field(default=None, max_length=64)
	description: Optional[str] = Field(default=None, max_length=1024)
	deadline: Optional[datetime] = Field(default=None)
	priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
	status: Optional[TaskStatus] = Field(default=TaskStatus.TODO)
	user_id: Optional[int] = Field(default=None, sa_column=Column(BigInteger(), ForeignKey('users.id')))
	project_id: int = Field(default=None, sa_column=Column(BigInteger(), ForeignKey('projects.id')))

class TaskUpdate(SQLModel):
	title: Optional[str] = Field(default=None, max_length=64)
	description: Optional[str] = Field(default=None, max_length=1024)
	deadline: Optional[datetime] = Field(default=None)
	priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
	status: Optional[TaskStatus] = Field(default=TaskStatus.TODO)
	user_id: Optional[int] = Field(default=None, sa_column=Column(BigInteger(), ForeignKey('users.id')))
	changed_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class Tasks(TaskBase, table=True):
	id: int = Field(default=None, sa_column=Column(BigInteger(), primary_key=True, autoincrement=True))
	created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
	changed_at: Optional[datetime] = Field(default=None)
	user: "Users" = Relationship(back_populates="tasks", sa_relationship_kwargs={"lazy": "joined"})
	project: "Projects" = Relationship(back_populates="tasks", sa_relationship_kwargs={"lazy": "joined"})

""" Teams tables """
class TeamRoles(StrEnum):
	ADMIN = "admin"
	USER = "user"

class TeamBase(SQLModel):
	user_id: int = Field(default=None, sa_column=Column(BigInteger(), ForeignKey('users.id')))
	project_id: int = Field(index=True, sa_type=BigInteger, foreign_key="projects.id")
	role: Optional[TeamRoles] = Field(default=TeamRoles.ADMIN)

class TeamUpdate(SQLModel):
	role: TeamRoles = Field(default=TeamRoles.USER)

class Teams(TeamBase, table=True):
	id: int = Field(default=None, sa_column=Column(BigInteger(), primary_key=True, autoincrement=True))
	created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
	user: "Users" = Relationship(back_populates="team")
	project: "Projects" = Relationship(back_populates="team")


""" Context table """
class PromptTitle(StrEnum):
	SYSTEM = 'system'
	PLAN = 'plan'
	RE_PLAN = 're_plan'
	TASK = 'task'
	RE_TASK = 're_task'
	DIV_TASK = 'div_task'

class MessageRole(StrEnum):
	SYSTEM = 'system'
	USER = 'user'
	ASSISTANT = 'assistant'

class ContextBase(SQLModel):
	project_id: int = Field(index=True, sa_type=BigInteger, foreign_key="projects.id")
	role: MessageRole = Field(default=MessageRole.USER)
	action: PromptTitle = Field(default=None)
	message: str = Field(default=None)

class Context(ContextBase, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
	changed_at: Optional[datetime] = Field(default=None)
	project: "Projects" = Relationship(back_populates="context")

""" Prompt table """
class Prompts(SQLModel, table=True):
	id: Optional[int] = Field(default=None, primary_key=True)
	title: PromptTitle = Field(default=None, unique=True)
	prompt: str = Field(default=None)


""" Plan table """
class PlanBase(SQLModel):
	text: str = Field(default=None)
	project_id: int = Field(index=True, sa_type=BigInteger, foreign_key="projects.id")

class Plans(PlanBase, table=True):
	id: int = Field(default=None, primary_key=True)
	created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
	project: "Projects" = Relationship(back_populates='plans')


""" Reminders table """
class ReminderBase(SQLModel):
	task_id: int = Field(index=True, sa_type=BigInteger, foreign_key="tasks.id", primary_key=True)
	user_id: Optional[int] = Field(index=True, sa_type=BigInteger)
	title: str = Field(default=None)
	send_time: Optional[datetime] = Field(default=None)
	project_id: int = Field(index=True, sa_type=BigInteger, foreign_key="projects.id")

class ReminderUpdate(SQLModel):
	title: Optional[str] = Field(default=None)
	send_time: Optional[datetime] = Field(default=None)
	user_id: Optional[int] = Field(index=True, sa_type=BigInteger, foreign_key="users.id")

class Reminders(ReminderBase, table=True):
	created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
	changed_at: Optional[datetime] = Field(default=None)
