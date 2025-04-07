""" SQLModel imports """
from fastapi import Depends
from sqlmodel import Session, create_engine, SQLModel
""" typing imports """
from typing import Annotated, Optional
""" ABC imports """
from collections.abc import Generator
""" Internal imports """
from models.db_models import *
from .config import SERVER, PORT, PASSWORD, DB, USER


database_url = f"postgresql+psycopg2://{USER}:{PASSWORD}@{SERVER}:{PORT}/{DB}"

engine = create_engine(database_url, echo=True)

async def init_database_and_tables() -> None:
  #SQLModel.metadata.drop_all(engine)
  SQLModel.metadata.create_all(engine)


def get_db() -> Generator[Session, None, None]:
  with Session(engine) as session:
    yield session

SessionDep = Annotated[ Session, Depends(get_db) ]
