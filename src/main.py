""" FastAPI imports """
import fastapi as fa
from sqlmodel import Session
""" asyncio imports """
import asyncio
""" uvicorn imports """
import uvicorn
import uvicorn.config
""" Internal imports """
from api import llm, general as gen
from core.db import init_database_and_tables



""" Application starts here """
server: fa.FastAPI = fa.FastAPI()

server.include_router(router=llm.router, prefix="/api")
server.include_router(router=gen.router, prefix="/api")


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
