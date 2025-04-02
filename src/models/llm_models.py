from enum import StrEnum
from typing import List, Optional
from pydantic import BaseModel

class CompletionOptions(BaseModel):
	stream: bool = False	
	temperature: float = 0.9
	max_tokens: int = 5000

class Message(BaseModel):
	role: str
	text: str
 
class BaseRequest(BaseModel):
	iam_token: str
	model_uri: str
 
class ProblemRequest(BaseRequest):
	problem: str

class OptionsRequest(BaseRequest):
	options: CompletionOptions