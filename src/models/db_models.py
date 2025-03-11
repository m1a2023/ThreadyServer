""" SQLModel imports """
from sqlmodel import Field, Relationship, SQLModel
""" typing imports """
from typing import Optional, List
""" datetime imports """
from datetime import datetime, timezone

""" Tables start here """

""" Users table """
class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=255)
    created_at: Optional[datetime] = Field(default=datetime.now(timezone.utc))  
    projects: List["Projects"] = Relationship(
        back_populates="user", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


""" Projects table """
class ProjectBase(SQLModel):
    title: str = Field(index=True)
    description: Optional[str] = Field(default=None, max_length=1024)
    repo_link: Optional[str] = Field(default=None, max_length=256)
    owner_id: int = Field(foreign_key="users.id")

class ProjectUpdate(SQLModel):
    new_title: Optional[str] = Field(index=True, max_length=64)
    new_description: Optional[str] = Field(default=None, max_length=1024)
    changed_at: Optional[datetime] = Field(default=datetime.now(timezone.utc))  

class Projects(ProjectBase, table=True):
    id: int = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default=datetime.now(timezone.utc))  
    changed_at: Optional[datetime] = Field(default=None)  
    user: Users = Relationship(
        back_populates="projects", 
        sa_relationship_kwargs={"lazy": "joined"}
    )

""" Tasks table """
class TaskBase(SQLModel):
    pass 

