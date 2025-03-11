""" FastAPI imports """
import fastapi as fa
""" asyncio imports """
import asyncio
""" uvicorn imports """
import uvicorn
import uvicorn.config
""" SQLModel imports """
"""TODO: delete """
from sqlmodel import SQLModel, Session, select
from models.db_models import *
""" Internal imports """
from api.llm import router as router_api_llm
from core.db import init_database_and_tables, engine


""" Application starts here """
server: fa.FastAPI = fa.FastAPI()

server.include_router(router=router_api_llm)

""" Main function """
async def main() -> None:
    """ Server starts here """
    server_config = uvicorn.Config(server, host="localhost", port=9000)
    server_ = uvicorn.Server(config=server_config)
   
    """ Database connection here """
    await init_database_and_tables()

    """
        Testing DB
    """
    # user =  Users(id=0, name="demo-name")
    # proj =  Projects(title="demo", description="demo_desc", owner_id=0)
    # with Session(engine) as session:
    #     session.add(user)
    #     session.add(proj)
    #     session.commit()

    #     st = select(Projects)
    #     res = session.exec(st)
    #     print(res.all())

    """ Server listening """
    await server_.serve()


if __name__ == "__main__":
    asyncio.run(main())
