"""Attendance register and Excel import for school lessons."""

from collections.abc import Iterable, Sequence
from copy import copy
from io import BytesIO

from openpyxl import Workbook, load_workbook  # type: ignore[import-untyped]
from openpyxl.worksheet.datavalidation import DataValidation  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.core.database import transaction
from arsis.core.errors import ImportValidationError, ResourceNotFoundError
from arsis.core.time import utc_now_iso
from arsis.generated.models import Lesson, LessonAttendance, Person
from arsis.school.attendance_repository import AttendanceRepository

AttendanceRow = tuple[int, str | None]
_ALLOWED_ATTENDANCE = {"present", "absent"}
_ATTENDANCE_ALIASES = {"presente": "present", "assente": "absent"}
_REQUIRED_HEADERS = {"student_person_id", "attendance"}
_MAX_IMPORT_BYTES = 5 * 1024 * 1024


class AttendanceService:
    def __init__(self, repository: AttendanceRepository | None = None) -> None:
        self._repository = repository or AttendanceRepository()

    def list_attendance(self, session: Session, *, lesson_id: int) -> Sequence[dict[str, object]]:
        lesson = self._get_lesson(session, lesson_id)
        return [
            self._serialize_row(person, record)
            for _, person, record in self._repository.list_roster(session, lesson=lesson)
        ]

    def save_attendance(
        self, session: Session, *, lesson_id: int, rows: Iterable[AttendanceRow], actor_id: int
    ) -> int:
        with transaction(session):
            normalized = self._validate_rows(session, lesson_id=lesson_id, rows=rows)
            records = self._repository.get_records_by_student(session, lesson_id=lesson_id)
            for student_id, attendance in normalized:
                record = records.get(student_id)
                if record is None:
                    if attendance is None:
                        continue
                    session.add(
                        LessonAttendance(
                            lesson_id=lesson_id,
                            student_person_id=student_id,
                            attendance=attendance,
                            recorded_at=utc_now_iso(),
                            recorded_by=actor_id,
                            created_by=actor_id,
                            updated_by=actor_id,
                        )
                    )
                    continue
                record.attendance = attendance
                record.recorded_at = utc_now_iso() if attendance is not None else None
                record.recorded_by = actor_id if attendance is not None else None
                record.updated_by = actor_id
                record.version += 1
            record_audit_event(
                session,
                action="lesson_attendance.recorded",
                entity_type="lesson",
                entity_id=lesson_id,
                user_id=actor_id,
                details={"rows": len(normalized)},
            )
        return len(normalized)

    def import_excel(
        self, session: Session, *, lesson_id: int, content: bytes, actor_id: int
    ) -> int:
        if len(content) > _MAX_IMPORT_BYTES:
            raise ImportValidationError("Il file Excel supera la dimensione massima di 5 MB")
        return self.save_attendance(
            session,
            lesson_id=lesson_id,
            rows=self._parse_excel(content),
            actor_id=actor_id,
        )

    def build_template(self, session: Session, *, lesson_id: int) -> bytes:
        rows = self.list_attendance(session, lesson_id=lesson_id)
        workbook = Workbook()
        worksheet = workbook.active
        worksheet.title = "Presenze"
        worksheet.append(["student_person_id", "student_name", "attendance"])
        for row in rows:
            worksheet.append([row["student_person_id"], row["student_name"], row["attendance"]])
        worksheet.freeze_panes = "A2"
        worksheet.auto_filter.ref = f"A1:C{max(len(rows) + 1, 2)}"
        for cell in worksheet[1]:
            font = copy(cell.font)
            font.bold = True
            cell.font = font
        worksheet.column_dimensions["A"].width = 20
        worksheet.column_dimensions["B"].width = 32
        worksheet.column_dimensions["C"].width = 18
        validation = DataValidation(type="list", formula1='"present,absent"', allow_blank=True)
        worksheet.add_data_validation(validation)
        validation.add(f"C2:C{max(len(rows) + 1, 2)}")
        output = BytesIO()
        workbook.save(output)
        return output.getvalue()

    def _validate_rows(
        self, session: Session, *, lesson_id: int, rows: Iterable[AttendanceRow]
    ) -> list[AttendanceRow]:
        lesson = self._get_lesson(session, lesson_id)
        roster_ids = {
            enrollment.student_person_id
            for enrollment, _, _ in self._repository.list_roster(session, lesson=lesson)
        }
        normalized: list[AttendanceRow] = []
        seen: set[int] = set()
        for student_id, attendance in rows:
            if student_id in seen:
                raise ImportValidationError(
                    "Lo stesso allievo è presente più volte nel registro",
                    details={"student_person_id": student_id},
                )
            if student_id not in roster_ids:
                raise ImportValidationError(
                    "L'allievo non risulta iscritto al corso alla data della lezione",
                    details={"student_person_id": student_id},
                )
            if attendance is not None and attendance not in _ALLOWED_ATTENDANCE:
                raise ImportValidationError(
                    "Lo stato presenza deve essere present, absent oppure vuoto",
                    details={"student_person_id": student_id, "attendance": attendance},
                )
            seen.add(student_id)
            normalized.append((student_id, attendance))
        if not normalized:
            raise ImportValidationError("Il file non contiene righe di presenza")
        return normalized

    def _parse_excel(self, content: bytes) -> list[AttendanceRow]:
        try:
            workbook = load_workbook(BytesIO(content), read_only=True, data_only=True)
            worksheet = workbook.active
            values = worksheet.iter_rows(values_only=True)
            headers = next(values, None)
        except Exception as exc:
            raise ImportValidationError("Il file Excel non è leggibile") from exc
        if headers is None:
            raise ImportValidationError("Il file Excel non contiene intestazioni")
        normalized_headers = [
            str(value).strip().lower() if value is not None else "" for value in headers
        ]
        if not _REQUIRED_HEADERS.issubset(normalized_headers):
            raise ImportValidationError(
                "Il file deve contenere le colonne student_person_id e attendance",
                details={"headers": normalized_headers},
            )
        id_column = normalized_headers.index("student_person_id")
        attendance_column = normalized_headers.index("attendance")
        imported: list[AttendanceRow] = []
        for row_number, values_row in enumerate(values, start=2):
            student_value = values_row[id_column] if id_column < len(values_row) else None
            attendance_value = (
                values_row[attendance_column] if attendance_column < len(values_row) else None
            )
            if student_value is None and attendance_value is None:
                continue
            if student_value is None:
                raise ImportValidationError(
                    "student_person_id deve essere un numero intero",
                    details={"row": row_number},
                )
            try:
                student_id = int(student_value)
            except (TypeError, ValueError) as exc:
                raise ImportValidationError(
                    "student_person_id deve essere un numero intero",
                    details={"row": row_number},
                ) from exc
            raw_attendance = (
                "" if attendance_value is None else str(attendance_value).strip().lower()
            )
            attendance = _ATTENDANCE_ALIASES.get(raw_attendance, raw_attendance) or None
            imported.append((student_id, attendance))
        return imported

    def _get_lesson(self, session: Session, lesson_id: int) -> Lesson:
        lesson = self._repository.get_lesson(session, lesson_id)
        if lesson is None:
            raise ResourceNotFoundError("Lezione", lesson_id)
        return lesson

    @staticmethod
    def _serialize_row(person: Person, record: LessonAttendance | None) -> dict[str, object]:
        return {
            "student_person_id": person.id,
            "student_name": f"{person.first_name} {person.last_name}",
            "attendance": record.attendance if record else None,
            "recorded_at": record.recorded_at if record else None,
            "version": record.version if record else None,
        }
