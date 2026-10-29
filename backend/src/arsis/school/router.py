"""HTTP endpoints for music-school courses."""

from typing import Annotated, Any

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from arsis.auth.dependencies import CurrentUser
from arsis.core.api_models import (
    ERROR_RESPONSES,
    Page,
    PaginationParams,
    SortDirection,
    build_page,
    parse_sort,
)
from arsis.core.database import get_database_session
from arsis.generated.schemas import (
    CourseCreateDTO,
    CourseUpdateDTO,
    EnrollmentCreateDTO,
    EnrollmentUpdateDTO,
)
from arsis.school.enrollment_service import EnrollmentsService
from arsis.school.schemas import (
    CourseCreateRequest,
    CourseResponse,
    CourseUpdateRequest,
    EnrollmentCreateRequest,
    EnrollmentResponse,
    EnrollmentUpdateRequest,
)
from arsis.school.service import CoursesService

router = APIRouter(prefix="/api/v1/courses", tags=["school"])
enrollments_router = APIRouter(prefix="/api/v1/enrollments", tags=["school"])
_service = CoursesService()
_enrollments_service = EnrollmentsService()
_SORT_FIELDS = {"name", "annual_fee", "status", "created_at", "updated_at"}


def _response(course: Any) -> CourseResponse:
    return CourseResponse.model_validate(course)


def _enrollment_response(enrollment: Any) -> EnrollmentResponse:
    return EnrollmentResponse.model_validate(enrollment)


@router.get("", response_model=Page[CourseResponse], responses=ERROR_RESPONSES)
def list_courses(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    q: Annotated[str | None, Query(max_length=200)] = None,
    sort: str | None = None,
    include_archived: bool = False,
) -> Page[CourseResponse]:
    sort_spec = parse_sort(
        sort,
        allowed_fields=_SORT_FIELDS,
        default_field="name",
        default_direction=SortDirection.ASC,
    )
    courses = list(_service.list_courses(session, search=q, include_archived=include_archived))
    courses.sort(
        key=lambda course: (
            getattr(course, sort_spec.field) is None,
            str(getattr(course, sort_spec.field) or "").casefold(),
            course.id,
        ),
        reverse=sort_spec.direction == "desc",
    )
    return build_page(
        [
            _response(course)
            for course in courses[pagination.offset : pagination.offset + pagination.page_size]
        ],
        total_items=len(courses),
        params=pagination,
    )


@router.post(
    "",
    response_model=CourseResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_course(
    payload: CourseCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> CourseResponse:
    return _response(
        _service.create_course(
            session, data=CourseCreateDTO(**payload.model_dump()), actor_id=current_user.id
        )
    )


@router.get("/{course_id}", response_model=CourseResponse, responses=ERROR_RESPONSES)
def get_course(
    course_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> CourseResponse:
    return _response(_service.get_course(session, course_id))


@router.patch("/{course_id}", response_model=CourseResponse, responses=ERROR_RESPONSES)
def update_course(
    course_id: int,
    payload: CourseUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> CourseResponse:
    values = payload.model_dump(exclude={"version"}, exclude_unset=True)
    return _response(
        _service.update_course(
            session,
            course_id=course_id,
            data=CourseUpdateDTO(**values),
            expected_version=payload.version,
            actor_id=current_user.id,
        )
    )


@router.delete("/{course_id}", response_model=CourseResponse, responses=ERROR_RESPONSES)
def archive_course(
    course_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> CourseResponse:
    return _response(
        _service.archive_course(
            session, course_id=course_id, expected_version=version, actor_id=current_user.id
        )
    )


@enrollments_router.get("", response_model=Page[EnrollmentResponse], responses=ERROR_RESPONSES)
def list_enrollments(
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
    pagination: Annotated[PaginationParams, Depends()],
    q: Annotated[str | None, Query(max_length=200)] = None,
    include_archived: bool = False,
) -> Page[EnrollmentResponse]:
    enrollments = list(
        _enrollments_service.list_enrollments(session, search=q, include_archived=include_archived)
    )
    return build_page(
        [
            _enrollment_response(enrollment)
            for enrollment in enrollments[
                pagination.offset : pagination.offset + pagination.page_size
            ]
        ],
        total_items=len(enrollments),
        params=pagination,
    )


@enrollments_router.post(
    "",
    response_model=EnrollmentResponse,
    status_code=status.HTTP_201_CREATED,
    responses=ERROR_RESPONSES,
)
def create_enrollment(
    payload: EnrollmentCreateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> EnrollmentResponse:
    return _enrollment_response(
        _enrollments_service.create_enrollment(
            session, data=EnrollmentCreateDTO(**payload.model_dump()), actor_id=current_user.id
        )
    )


@enrollments_router.get(
    "/{enrollment_id}", response_model=EnrollmentResponse, responses=ERROR_RESPONSES
)
def get_enrollment(
    enrollment_id: int,
    session: Annotated[Session, Depends(get_database_session)],
    _current_user: CurrentUser,
) -> EnrollmentResponse:
    return _enrollment_response(_enrollments_service.get_enrollment(session, enrollment_id))


@enrollments_router.patch(
    "/{enrollment_id}", response_model=EnrollmentResponse, responses=ERROR_RESPONSES
)
def update_enrollment(
    enrollment_id: int,
    payload: EnrollmentUpdateRequest,
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> EnrollmentResponse:
    values = payload.model_dump(exclude={"version"}, exclude_unset=True)
    return _enrollment_response(
        _enrollments_service.update_enrollment(
            session,
            enrollment_id=enrollment_id,
            data=EnrollmentUpdateDTO(**values),
            expected_version=payload.version,
            actor_id=current_user.id,
        )
    )


@enrollments_router.delete(
    "/{enrollment_id}", response_model=EnrollmentResponse, responses=ERROR_RESPONSES
)
def archive_enrollment(
    enrollment_id: int,
    version: Annotated[int, Query(ge=1)],
    session: Annotated[Session, Depends(get_database_session)],
    current_user: CurrentUser,
) -> EnrollmentResponse:
    return _enrollment_response(
        _enrollments_service.archive_enrollment(
            session,
            enrollment_id=enrollment_id,
            expected_version=version,
            actor_id=current_user.id,
        )
    )
