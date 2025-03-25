from typing import List, Optional
from pydantic import BaseModel

class CompletionOptions(BaseModel):
	stream: bool = False	
	temperature: float = 0.9
	max_tokens: int = 1000

class Message(BaseModel):
	role: str
	text: str
 
class BaseRequest(BaseModel):
	iam_token: str
	model_uri: str
	# TODO 
	# Developer count
	# Difficulty
	# Message for problem description in RE_PLAN