""" FastAPI imports """
import fastapi as fa
""" asyncio imports """
import asyncio
""" uvicorn imports """
import uvicorn
import uvicorn.config
""" SQLModel imports """
from sqlmodel import SQLModel, Session
""" Internal imports """
from api.llm import router as router_api_llm
from core.db import create_db_and_tables


""" Application starts here """
server: fa.FastAPI = fa.FastAPI()

server.include_router(router=router_api_llm)

""" Main function """
async def main() -> None:
    """ Server starts here """
    server_config = uvicorn.Config(server, host="localhost", port=9000)
    server_ = uvicorn.Server(config=server_config)
   
    """ Database connection here """
    await create_db_and_tables()

    """ Server listening """
    await server_.serve()


if __name__ == "__main__":
    asyncio.run(main())
