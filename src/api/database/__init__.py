""" FastAPI imports """
from fastapi import APIRouter, Depends, Query, Request
""" Internal imports """
from .users import users_router
from .projects import projects_router
from .tasks import tasks_router
from .teams import teams_router
from .reports import reports_router
from .reminders import reminders_router


""" APIRouter added to upper router(api/__init__.py) """
router = APIRouter()

router.include_router(users_router)
router.include_router(projects_router)
router.include_router(tasks_router)
router.include_router(teams_router)
router.include_router(reports_router)
router.include_router(reminders_router)
