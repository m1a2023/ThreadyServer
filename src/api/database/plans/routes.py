""" FastAPI imports """
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
""" SQLModel imports"""
from sqlmodel import desc, select
""" SQLAlchemy imports """
from sqlalchemy.orm.exc import UnmappedInstanceError
from sqlalchemy.exc import SQLAlchemyError
""" typing imports """
from typing import Any, Dict, List, Optional, Union
""" Internal imports """
from core.db import SessionDep, get_db
from services import general_service as gen
from models.db_models import Plans


""" APIRouter added to upper router(db/__init__.py) """
router = APIRouter(prefix="/plans", tags=["/plans"])

@router.get('/project/{project_id}', dependencies=[Depends(get_db)])
async def get_last_project_by_id(s: SessionDep, project_id: int) -> Optional[Plans]:
	q = select(Plans).where(Plans.project_id == project_id).order_by(desc(Plans.created_at)).limit(1)
	plan = s.exec(q).first()
	return plan if plan else None

	