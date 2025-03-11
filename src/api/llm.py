""" FastAPI imports """
from fastapi import APIRouter, Request
from fastapi.responses import StreamingResponse
""" httpx import """
import httpx
""" typing imports """
from typing import Optional, Union

""" Simple router added to general  """
router = APIRouter()

@router.get("/api/llm/")
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