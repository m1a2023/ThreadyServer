""" SQLModel imports """
from sqlmodel import Session, select
""" typing imports """
from typing import List, Optional, Sequence, Union
""" datetime imports """
from datetime import datetime, timezone
""" Internal imports """
from core import db
from src.models.db_models import ProjectUpdate, Users, Projects

""" Util """
async def is_present_by_id(table: type, id: int) -> bool:
  with Session(db.engine) as session:
    return session.exec(select(table).where(table.id == id)).first() is not None

#*
#*  Users table
#*

""" GET """
async def get_all_users() -> Sequence[Users]:
  with Session(db.engine) as session:
    return session.exec(select(Users)).all()

async def get_user_by_id(id: int) -> Optional[Users]:
  with Session(db.engine) as session:
    return session.exec(select(Users).where(Users.id == id)).first()

async def get_users_by_ids(ids: Union[List[int], Sequence[int]]) -> Sequence[Optional[Users]]:
  users: List[Optional[Users]] = [ ]

  for id in ids:
    user = await get_user_by_id(id)
    users.append(user)

  return tuple(users)


""" CREATE """
async def create_user(user: Users) -> bool:
  with Session(db.engine) as session:
    session.add(user)
    session.commit()

  return await is_present_by_id(table=Users, id=user.id)

async def create_users(users: Union[List[Users], Sequence[Users]]) -> bool:
  with Session(db.engine) as session:
    session.add_all(users)
    session.commit()

    for user in users:
      if not is_present_by_id(table=Users, id=user.id):
        return False
    return True

""" DELETE """
async def delete_user_by_id(id: int) -> bool:
  with Session(db.engine) as session:
    """ Deleting user """
    query = select(Users).where(Users.id == id)
    user = session.exec(query).first()
    session.delete(user)
    session.commit()

    """ Checking deletion correctness"""
    return await is_present_by_id(table=Users, id=id)


#*
#*  Projects table
#*

""" GET """
async def get_all_projects() -> Sequence[Projects]:
  with Session(db.engine) as session:
    return session.exec(select(Projects)).all()

async def get_all_projects_by_user(user: Users) -> Sequence[Projects]:
  with Session(db.engine) as session:
    return session.exec(select(Projects).where(Projects.owner_id == user.id)).all()

async def get_all_projects_owner_id(owner_id: int) -> Sequence[Projects]:
  with Session(db.engine) as session:
    return session.exec(select(Projects).where(Projects.owner_id == owner_id)).all()

async def get_project_by_id(id: int) -> Projects:
  with Session(db.engine) as session:
    return session.exec(select(Projects).where(Projects.id == id)).one()

""" CREATE """
async def create_project(project: Projects) -> bool:
  with Session(db.engine) as session:
    session.add(project)
    session.commit()

    return await is_present_by_id(table=Projects, id=project.id)

""" DELETE """
async def delete_project_by_id(project_id: int) -> bool:
  with Session(db.engine) as session:
    """ Deleting project """
    query = select(Projects).where(Projects.id == project_id)
    project = session.exec(query).first()
    session.delete(project)
    session.commit()

    return await is_present_by_id(table=Projects, id=project_id)

async def delete_projects_by_user(user: Users) -> bool:
  with Session(db.engine) as session:
    query = select(Projects).where(Projects.owner_id == user.id)
    projects = session.exec(query).all()

    if projects is None:
      return False

    session.delete(projects)
    session.commit()

    return session.exec(select(Projects).where(Projects.owner_id == user.id)).first() is not None

""" UPDATE """
async def update_project_by_id(update: ProjectUpdate, project_id: int) -> bool:
  with Session(db.engine) as session:
     query = select(Projects).where(Projects.id == project_id)
     project = session.exec(query).first()

     if project is None:
       return False

     if update.new_title is not None:
       project.title = update.new_title
     if update.new_description is not None:
       project.description = update.new_description

     project.changed_at = datetime.now(timezone.utc)

     session.commit()
     session.refresh(project) 
     return True
  

#*
#*	Tasks table
#* 
#TODO