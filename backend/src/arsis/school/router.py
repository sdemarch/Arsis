from typing import Annotated
from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.orm import Session
from arsis.auth.dependencies import CurrentUser
from arsis.core.database import get_database_session, transaction
from arsis.generated.models import Course, PersonRole
from arsis.school.schemas import CourseCreateRequest, CourseResponse, CourseUpdateRequest

router = APIRouter(prefix='/api/v1/courses', tags=['school'])

def _teacher(session: Session, person_id: int) -> None:
    role = session.scalar(select(PersonRole.id).where(PersonRole.person_id == person_id, PersonRole.role_type == 'teacher', PersonRole.status == 'active', PersonRole.archived_at.is_(None)))
    if role is None: raise ValueError('L’insegnante selezionato non ha un ruolo attivo')

@router.get('', response_model=list[CourseResponse])
def list_courses(session: Annotated[Session, Depends(get_database_session)], _user: CurrentUser) -> list[Course]:
    return list(session.scalars(select(Course).where(Course.archived_at.is_(None)).order_by(Course.name)))

@router.post('', response_model=CourseResponse)
def create_course(payload: CourseCreateRequest, session: Annotated[Session, Depends(get_database_session)], user: CurrentUser) -> Course:
    _teacher(session, payload.teacher_person_id)
    with transaction(session):
        course = Course(**payload.model_dump(), status=payload.status or 'active', created_by=user.id, updated_by=user.id)
        session.add(course); session.flush()
    return course

@router.patch('/{course_id}', response_model=CourseResponse)
def update_course(course_id: int, payload: CourseUpdateRequest, session: Annotated[Session, Depends(get_database_session)], user: CurrentUser) -> Course:
    course = session.get(Course, course_id)
    if course is None or course.archived_at: raise ValueError('Corso non trovato')
    _teacher(session, payload.teacher_person_id)
    with transaction(session):
        for key, value in payload.model_dump(exclude={'version'}).items(): setattr(course, key, value)
        course.updated_by = user.id; course.version += 1; session.flush()
    return course
