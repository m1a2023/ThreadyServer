""" SQLModel imports """
from sqlmodel import Field, Session, create_engine, SQLModel
""" typing imports """
from typing import Optional
""" Internal imports """
from models.db_models import *
from .config import SERVER, PORT, PASSWORD, DB, USER 


database_url = f"postgresql+psycopg://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB}"

engine = create_engine(database_url, echo=True)

async def create_db_and_tables():
  SQLModel.metadata.create_all(engine)