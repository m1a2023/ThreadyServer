""" FastAPI imports """
import traceback
from fastapi import APIRouter, Body, Depends, Query, Request
from fastapi.responses import JSONResponse, StreamingResponse
""" httpx import """
import httpx
""" typing imports """
from typing import Optional, Union
""" Internal imports """
from services import llm_service
from models.llm_models import BaseRequest, CompletionOptions, Message, OptionsRequest, ProblemRequest 
from models.db_models import PromptTitle
from core.db import SessionDep, get_db


""" APIRouter added to general  """
router = APIRouter(prefix="/ygpt")

@router.get("/")
async def send_api_request_to_llm(
  url_path: str, 
  json: Optional[dict] = None, 
  stream: Optional[bool] = False,
  timeout: Optional[int] = 30 
):
  """ Send unblocking error json """
  if not json: return { "error": "Body json prompt is required." }

  if stream:
    """ Get json stream response """ 
    async def _iterate_over_JSONs():
      async with httpx.AsyncClient() as client: 
        async with client.stream('POST', url=url_path, json=json, timeout=timeout) as response:
          async for chunk in response.aiter_text():
            yield chunk
    return StreamingResponse(_iterate_over_JSONs(), status_code=200, media_type='application/json')
  
  else: 
    """ Get only one json response """
    async with httpx.AsyncClient() as client:
      response = await client.post(url=url_path, json=json, timeout=timeout)
      result = response.json()
      return result

@router.post("/", dependencies=[Depends(get_db)])
async def send_request(
	s: SessionDep,
	url: str = Query(...),
	action: PromptTitle = Query(...),
	project_id: int = Query(...),
	context_depth: int = Query(...),
	timeout: int = Query(...),
	json: BaseRequest | ProblemRequest | OptionsRequest = Body(...)
) -> JSONResponse:
	request = { 
		'modelUri': json.model_uri,
		'completionOptions': CompletionOptions().model_dump()
	}
	if isinstance(json, OptionsRequest):
		request['completionOptions'] = json.options
	
	headers = { 
		'Authorization': 'Bearer ' + json.iam_token,
		'Content-Type' : 'application/json'
	}
 
	if isinstance(json, ProblemRequest):
		request.update({
			'problem': json.problem
		})
  
	try:
		response =  await llm_service.general_request(
			s=s, url=url, 
			request=request, 
			headers=headers, 
			action=action, 
			project_id=project_id, 
			context_depth=context_depth,
			timeout=timeout
		)
		return response
	except Exception as e:
		traceback_details = traceback.format_exc()
		print(traceback_details)
		return JSONResponse(content={ 'error' : f'{str(e)}'}, status_code=404)