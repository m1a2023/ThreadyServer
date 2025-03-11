""" SQLModel imports """
from sqlmodel import create_engine, SQLModel
""" typing imports """
from typing import Optional
""" Internal imports """
from models.db_models import *
from .config import SERVER, PORT, PASSWORD, DB, USER 


database_url = f"postgresql+psycopg2://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB}"

engine = create_engine(database_url, echo=True)

async def init_database_and_tables() -> None:
  SQLModel.metadata.create_all(engine)