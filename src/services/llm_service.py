""" FastAPI imports """
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
""" Pydantic imports """
from pydantic import Json
""" SQLModel imports """
from sqlmodel import and_, desc, select
""" httpx import """
import httpx
""" typing imports """
from typing import Any, Dict, List, Optional, Union
""" Thread imports """
import threading as thread
""" asyncio imports """
import asyncio
""" Internal imports """
from core.db import SessionDep
from services import general_service as gen
from models.db_models import Context, ContextBase, MessageRole, PromptTitle, Prompts

async def general_request(
	s: SessionDep,
	url: str, request: Dict, headers: Dict[str, str],
	action: PromptTitle, project_id: int,
	context_depth: int,
	timeout: int) -> JSONResponse:
	
	_prompt: str 
	description: str
	messages = { 'messages' : [] }
	query = select(Prompts)
	
	""" Get prompts """
	sys_prompt_query = s.exec(query.where(Prompts.title == 'system')).first()
	prompt_query = s.exec(query.where(Prompts.title == action)).first()
	
	""" Get project """
	project = await gen.get_project_by_id(s, id=project_id)
	if project and project.description:
		description = project.description
  
	""" Get context if present """
	context = await gen.get_context_by_project_id(s, project_id, action, context_depth)
	
	if sys_prompt_query:
		system_prompt = { 'role': 'system', 'text': sys_prompt_query.prompt }
		messages['messages'].append(system_prompt)
		# base_msgs.insert(0, system_prompt)
	if prompt_query:
		_prompt = prompt_query.prompt + '\n\n' + description
		messages['messages'].append(
			{ 'role': 'user', 'text': _prompt }
		)
		await gen.create_context(s, ContextBase(
				project_id=project_id, role=MessageRole.USER,
				action=action, message=_prompt)
			)

	context.extend(messages['messages'])
	request['messages'] = context
 
	""" Sending post request to external api """
	async with httpx.AsyncClient(timeout=timeout) as client:
		response = await client.post(url=url, headers=headers, json=request)
		""" Checking response status """
		response.raise_for_status()
		try: 
			message = response.json()["result"]["alternatives"][0]["message"]["text"]
		except Exception as e:
			message = 'Error was interrupt'
		""" Adding assistant context to db """
		if message:
			await gen.create_context(s, ContextBase(
				project_id=project_id, role=MessageRole.ASSISTANT,
				action=action, message=message)
			)
		return response.json()