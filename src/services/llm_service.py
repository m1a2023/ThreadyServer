""" FastAPI imports """
from fastapi import APIRouter, Request
from fastapi.responses import JSONResponse, StreamingResponse
""" SQLModel imports """
from sqlmodel import and_, desc, select
""" httpx import """
import httpx

import json
import re
""" typing imports """
from typing import Any, Dict, List, Optional, Union
""" Internal imports """
from core.db import SessionDep
from services import general_service as gen
from models.db_models import Context, ContextBase, MessageRole, PlanBase, PromptTitle, Prompts, TaskBase, Tasks
  


async def general_request(
	s: SessionDep,
	url: str, request: Dict, headers: Dict[str, str],
	action: PromptTitle, project_id: int,
	context_depth: int,
	timeout: int) -> JSONResponse:
	
	text: str 
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
  
	if prompt_query:
		text = prompt_query.prompt + '\n\n' + description
		if 'problem' in request.keys():
			text += "\nProblem description: " + request['problem']
		messages['messages'].append({ 'role': 'user', 'text': text })
  
		await gen.create_context(s, ContextBase(
				project_id=project_id, role=MessageRole.USER,
				action=action, message=text)
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
			await _match_action_and_create(s, project_id, action, message)
		return response.json()


async def _match_action_and_create(
	s: SessionDep,
	project_id: int,
	action: PromptTitle,
	text: str) -> None:
  
	if action in [PromptTitle.PLAN, PromptTitle.RE_PLAN]:
		plan = PlanBase(project_id=project_id, text=text)
		await gen.create_plan(s, plan)
  
	if action in [PromptTitle.TASK, PromptTitle.RE_TASK]:
		built = _build_tasks(response=text)
		parsed = _parse_tasks(built, project_id)
		tasks = [ 
			Tasks(**task.model_dump()) for task in parsed
		]
		await gen.create_tasks(s, tasks)
  
	if action in [PromptTitle.DIV_TASK]:
		return 


def _build_tasks(response: str) -> Dict:
	try:
		match = re.search(r'\{[\s\S]*\}', response)
		if not match:
			return { "error": "Couldn't be parsed"}
		clean_json = match.group()
		return json.loads(clean_json)
	except json.JSONDecodeError:
		print("Error: Invalid JSON format.")
		return { "error": "Couldn't be parsed"}

def _parse_tasks(tasks: Dict, project_id: int) -> List[TaskBase]:
	parsed_tasks = []
	print("\n\ntasks: ")
	print(tasks)
	print("\n")
 
	for task in tasks["tasks"]:
		for task_name, task_desc in task.items():
			_task = TaskBase(
				title="task_"+task_name, 
				description=task_desc,
				project_id=project_id
			)
			parsed_tasks.append(_task)
	return parsed_tasks
