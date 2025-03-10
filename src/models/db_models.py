from sqlmodel import Field, Relationship, SQLModel
from typing import Optional, List


""" Users table """
class Users(SQLModel, table=True):
    id: int = Field(default=None, primary_key=True)
    name: str = Field(default=None, max_length=255)
    projects: List["Projects"] = Relationship(
        back_populates="user", 
        sa_relationship_kwargs={"cascade": "all, delete-orphan"}
    )


# TODO: check correctness
""" Projects table """
class ProjectBase(SQLModel):
    title: str
    description: Optional[str] = Field(default=None, max_length=1024)
    owner_id: int = Field(foreign_key="users.id")

class ProjectUpdate(SQLModel):
    title: Optional[str] = Field(default=None, max_length=64)
    description: Optional[str] = Field(default=None, max_length=1024)

class Projects(ProjectBase, table=True):
    id: int = Field(default=None, primary_key=True)
    user: Users = Relationship(
        back_populates="projects", 
        sa_relationship_kwargs={"lazy": "joined"}
    )


# TODO: 
""" Tasts table """
class TaskBase(SQLModel):
    """ TODO: """
    pass