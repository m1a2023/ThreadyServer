""" SQLModel imports """
from sqlmodel import Field, Relationship, SQLModel
""" typing imports """
from typing import Optional, List
""" datetime imports """
from datetime import datetime, timezone
""" enum imports """
from enum import StrEnum


""" Tables start here """

""" Users table """
class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))  
    projects: List["Projects"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    tasks: List["Tasks"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    team: List["Teams"] = Relationship(back_populates="user", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

""" Projects table """
class ProjectBase(SQLModel):
    title: str = Field(index=True, max_length=128)
    description: Optional[str] = Field(default=None, max_length=1024)
    repo_link: Optional[str] = Field(default=None, max_length=256)
    owner_id: int = Field(foreign_key="users.id")

class ProjectUpdate(SQLModel):
    new_title: Optional[str] = Field(default=None, max_length=128)
    new_description: Optional[str] = Field(default=None, max_length=1024)
    changed_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))  

class Projects(ProjectBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))  
    changed_at: Optional[datetime] = Field(default=None)  
    user: Users = Relationship(back_populates="projects", sa_relationship_kwargs={"lazy": "joined"})
    tasks: List["Tasks"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
    team: List["Teams"] = Relationship(back_populates="project", sa_relationship_kwargs={"cascade": "all, delete-orphan"})

""" Tasks table """
class TaskPriority(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class TaskStatus(StrEnum):
    TODO = "todo"
    IN_PROGRESS = "in progress"
    DONE = "done"

class TaskBase(SQLModel):
    title: str = Field(index=True, max_length=64)
    description: Optional[str] = Field(default=None, max_length=1024)
    deadline: Optional[datetime] = Field(default=None)
    priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
    status: Optional[TaskStatus] = Field(default=TaskStatus.TODO)
    project_id: int = Field(foreign_key="projects.id")

class TaskUpdate(SQLModel):
    new_title: Optional[str] = Field(default=None, max_length=64)
    new_description: Optional[str] = Field(default=None, max_length=1024)
    new_deadline: Optional[datetime] = Field(default=None)
    new_priority: Optional[TaskPriority] = Field(default=TaskPriority.MEDIUM)
    new_status: Optional[TaskStatus] = Field(default=TaskStatus.TODO)
    changed_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))

class Tasks(TaskBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    changed_at: Optional[datetime] = Field(default=None)
    user: Users = Relationship(back_populates="tasks", sa_relationship_kwargs={"lazy": "joined"})
    project: Projects = Relationship(back_populates="tasks", sa_relationship_kwargs={"lazy": "joined"})
    

""" Teams tables """
class TeamRoles(StrEnum):
    ADMIN = "admin" 
    USER = "user"

class TeamBase(SQLModel):
    user_id: int = Field(foreign_key="users.id")
    role: Optional[TeamRoles] = Field(default=TeamRoles.ADMIN)
    project_id: int = Field(index=True, foreign_key="projects.id")   

class TeamUpdate(SQLModel):
    new_user_id: int = Field(default=None)
    new_project_id: int = Field(default=None)
    new_role: Optional[TeamRoles] = Field(default=TeamRoles.USER)

class Teams(TeamBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(timezone.utc))
    user: Users = Relationship(back_populates="team")
    project: Projects = Relationship(back_populates="team")