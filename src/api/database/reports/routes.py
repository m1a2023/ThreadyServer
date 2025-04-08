""" FastAPI imports """
from fastapi import APIRouter, Body, Depends, HTTPException, Query, Request
""" SQLModel imports"""
from sqlmodel import select
""" SQLAlchemy imports """
from sqlalchemy.exc import SQLAlchemyError
""" typing imports """
from typing import Any, Dict, List, Optional, Union
""" Internal imports """
from core.db import SessionDep, get_db
from services import report_service as rep
from models.db_models import TeamBase, TeamUpdate, Teams,Tasks


""" APIRouter added to upper router(db/__init__.py) """
router = APIRouter(prefix="/reports", tags=["/reports"])

@router.get("/developer/{user_d}", response_model=Dict)
async def get_developer_report(user_d: int, project_id: int, s: SessionDep):
    try:
        report = await rep.get_developer_report(s, user_d, project_id)
        if report is None:
            raise HTTPException(status_code=404,detail=f"Erorr creating report by user_d {user_d}")
        return report
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erorr creating report by user_d {user_d}")

@router.get("/project/{project_id}", response_model=Dict)
async def get_project_report(project_id: int, s: SessionDep):
    try:
        report = await rep.get_project_report(s, project_id)
        if report is None:
            raise HTTPException(status_code=404,detail=f"Erorr creating report by project_id {project_id}")
        return report
    except SQLAlchemyError as e:
        raise HTTPException(status_code=500, detail=f"Erorr creating report by project_id {project_id}")
