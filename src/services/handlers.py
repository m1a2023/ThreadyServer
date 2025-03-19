""" FastAPI imports """
from fastapi import HTTPException
from fastapi.responses import JSONResponse
""" SqlAlchemy imports """
from sqlalchemy.exc import NoResultFound
""" Internal imports """
from ..main import server

@server.exception_handler(NoResultFound)
async def no_result_handler(req, exc):
  return JSONResponse(
		status_code=404,
		content={"detail": "Requested resource not found"}
	)
  
