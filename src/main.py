""" FastAPI imports """
import fastapi as fa
from sqlmodel import Session

from services.general_service import create_project
from models.db_models import ProjectBase
""" asyncio imports """
import asyncio
""" uvicorn imports """
import uvicorn
import uvicorn.config
""" Internal imports """
import api
from core.db import init_database_and_tables, engine


""" Application starts here """
server: fa.FastAPI = fa.FastAPI()

server.include_router(router=api.router)


""" Main function """
async def main() -> None:
	""" Server starts here """
	server_config = uvicorn.Config(server, host="localhost", port=9000)
	server_ = uvicorn.Server(config=server_config)
	""" Database connection here """
	await init_database_and_tables()
	""" Server listening """
	await server_.serve()


if __name__ == "__main__":
    asyncio.run(main())
