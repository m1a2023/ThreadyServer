""" FastAPI imports """
from wsgiref import headers
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
from pydantic import Json
from sqlmodel import and_, desc, select
""" httpx import """
import httpx
""" typing imports """
from typing import Any, Dict, List, Optional, Union
""" Internal imports """
from core import db
from core.db import SessionDep
from models.llm_models import CompletionOptions, Message
from models.db_models import Context, ContextBase, MessageRole, PromptTitle, Prompts

async def send_request(
	url: str,
	request: Dict,
	headers: Dict[str, str],
	action: PromptTitle
) -> JSONResponse:
	async with httpx.AsyncClient() as client:
		response = await client.post(url=url, headers=headers, json=request)
		response.raise_for_status()
		return response.json()

async def general_request(
	s: SessionDep,
	url: str,
	request: Dict,
	headers: Dict[str, str],
	action: PromptTitle,
	project_id: int,
	context_depth: int
	) -> JSONResponse:
	_prompt: str = ""
	
	""" Select needed action to exec """
	query = select(Prompts)
	sys_prompt_query = s.exec(query.where(Prompts.title == 'system')).first()
	prompt_query = s.exec(query.where(Prompts.title == action)).first()
	
	""" Get context if present """
	context = get_context(s, project_id, action, context_depth)
	base_msgs = request['messages']

	if sys_prompt_query:
		system_prompt = { 'role': 'system', 'text': sys_prompt_query.prompt }
		base_msgs.insert(0, system_prompt)
		print('\n\nStart')
		print(system_prompt)
	if prompt_query:
		_prompt = prompt_query.prompt
		print(_prompt)
		print('End\n\n')
  
	for msg in base_msgs:
		if msg['role'] == 'user':
			msg['text'] = f"{_prompt}\n\n{msg['text']}"
			print(msg['text'])
			# ! USE A FUNCTION 
			s.add(
				Context(**ContextBase(
					project_id=project_id, role=MessageRole.USER, 
					action=action, message=msg['text']
				).model_dump())
			)
			s.commit()
	context.extend(base_msgs)
	request['messages'] = context
	print('\nREQUEST\n')
	print(request)
	print('\n\n')
	print('\nHEADERS\n')
	print(headers)
	print('\n\n')
	""" Sending post request to external api """
	async with httpx.AsyncClient(timeout=30) as client:
		response = await client.post(url=url, headers=headers, json=request)
		response.raise_for_status()
		print(response)
		s.add(
			Context(**ContextBase(
				project_id=project_id, role=MessageRole.ASSISTANT, 
				action=action, message=response.text
				).model_dump())
		)
		s.commit()
		return response.json()
  
def get_context(
	s: SessionDep,	
	project_id: int,
	action: PromptTitle,
	context_depth: int
	):
	_context = [ ]
	""" Get context """
	query = select(Context).where(and_(Context.project_id == project_id, Context.action == action))
	contexts = s.exec(query.order_by(desc(Context.changed_at)).limit(context_depth)).all()
	for context in contexts:
		_context.append({'role': context.role, 'text': context.message})
	return _context