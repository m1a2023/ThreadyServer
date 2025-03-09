""" FastAPI imports """
import fastapi as fa
""" asyncio imports """
import asyncio
""" uvicorn imports """
import uvicorn
import uvicorn.config
""" Internal imports """
from api.llm import router as RouterApiLLM 


""" Application starts here """
server: fa.FastAPI = fa.FastAPI()

server.include_router(router=RouterApiLLM)

@server.get("/")
async def root():
    return { "success": "True" }

""" Main function """
async def main() -> None:
    server_config = uvicorn.Config(server, host="localhost", port=9000)
    server_ = uvicorn.Server(config=server_config)
    await server_.serve()

if __name__ == "__main__":
    asyncio.run(main())
