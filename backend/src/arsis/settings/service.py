import json
from collections.abc import Mapping
from datetime import datetime
from typing import Any

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from arsis.audit.service import record_audit_event
from arsis.auth.schemas import normalize_email
from arsis.core.database import transaction
from arsis.core.errors import ConflictError, ResourceNotFoundError, StaleVersionError
from arsis.core.security import hash_password
from arsis.core.time import utc_now_iso
from arsis.generated.models import AppSetting, User
from arsis.settings.schemas import (
    GeneralSettingsResponse,
    GeneralSettingsUpdateRequest,
    ResponsibleUserCreateRequest,
    ResponsibleUserResponse,
    ResponsibleUserUpdateRequest,
)

_ORGANIZATION_NAME = "organization.name"
_ARCHIVE_URL = "archive.google_drive_url"
_DEFAULT_THEME = "ui.default_theme"
_SETTING_KEYS = (_ORGANIZATION_NAME, _ARCHIVE_URL, _DEFAULT_THEME)


class SettingsService:
    def list_responsible_users(self, session: Session) -> list[ResponsibleUserResponse]:
        users = session.scalars(
            select(User).where(User.archived_at.is_(None)).order_by(User.email)
        ).all()
        return [self._user_response(user) for user in users]

    def create_responsible_user(
        self, session: Session, *, data: ResponsibleUserCreateRequest, actor_id: int
    ) -> ResponsibleUserResponse:
        email = normalize_email(data.email)
        with transaction(session):
            existing = session.scalar(select(User.id).where(func.lower(User.email) == email))
            if existing is not None:
                raise ConflictError(
                    "Esiste già un utente con questa email", code="USER_EMAIL_EXISTS"
                )
            now = utc_now_iso()
            user = User(
                email=email,
                password_hash=hash_password(data.password),
                display_name=data.display_name.strip(),
                is_active=True,
                created_at=now,
                updated_at=now,
                created_by=actor_id,
                updated_by=actor_id,
                version=1,
            )
            session.add(user)
            session.flush()
            record_audit_event(
                session,
                action="user.created",
                entity_type="user",
                entity_id=user.id,
                user_id=actor_id,
            )
            return self._user_response(user)

    def update_responsible_user(
        self,
        session: Session,
        *,
        user_id: int,
        data: ResponsibleUserUpdateRequest,
        actor_id: int,
    ) -> ResponsibleUserResponse:
        with transaction(session):
            user = session.get(User, user_id)
            if user is None or user.archived_at is not None:
                raise ResourceNotFoundError("Utente", user_id)
            if user.version != data.version:
                raise StaleVersionError(expected_version=data.version, current_version=user.version)
            if not data.is_active:
                if user.id == actor_id:
                    raise ConflictError(
                        "Non è possibile disattivare il proprio utente",
                        code="CANNOT_DEACTIVATE_SELF",
                    )
                active_count = session.scalar(
                    select(func.count()).select_from(User).where(
                        User.is_active.is_(True), User.archived_at.is_(None)
                    )
                )
                if active_count is not None and active_count <= 1:
                    raise ConflictError(
                        "Deve rimanere almeno un responsabile attivo",
                        code="LAST_ACTIVE_RESPONSIBLE",
                    )
            if user.is_active != data.is_active:
                user.is_active = data.is_active
                user.updated_at = utc_now_iso()
                user.updated_by = actor_id
                user.version += 1
                record_audit_event(
                    session,
                    action="user.activated" if data.is_active else "user.deactivated",
                    entity_type="user",
                    entity_id=user.id,
                    user_id=actor_id,
                )
            session.flush()
            return self._user_response(user)

    def get_general(self, session: Session) -> GeneralSettingsResponse:
        settings = self._get_settings(session)
        return self._response(settings)

    def update_general(
        self,
        session: Session,
        *,
        data: GeneralSettingsUpdateRequest,
        actor_id: int,
    ) -> GeneralSettingsResponse:
        with transaction(session):
            settings = self._get_settings(session)
            values: Mapping[str, tuple[Any, int]] = {
                _ORGANIZATION_NAME: (data.organization_name, data.organization_name_version),
                _ARCHIVE_URL: (
                    data.archive_google_drive_url,
                    data.archive_google_drive_url_version,
                ),
                _DEFAULT_THEME: (data.default_theme, data.default_theme_version),
            }
            changed_keys: list[str] = []
            for key, (value, expected_version) in values.items():
                setting = settings[key]
                if setting.version != expected_version:
                    raise StaleVersionError(
                        expected_version=expected_version, current_version=setting.version
                    )
                if self._decode(setting) != value:
                    setting.value = json.dumps(value, ensure_ascii=False)
                    setting.version += 1
                    setting.updated_at = utc_now_iso()
                    setting.updated_by = actor_id
                    changed_keys.append(key)
            if changed_keys:
                record_audit_event(
                    session,
                    action="settings.general_updated",
                    entity_type="app_settings",
                    entity_id=None,
                    user_id=actor_id,
                    details={"keys": changed_keys},
                )
            session.flush()
            return self._response(settings)

    def _get_settings(self, session: Session) -> dict[str, AppSetting]:
        rows = {
            setting.key: setting
            for setting in session.query(AppSetting).filter(AppSetting.key.in_(_SETTING_KEYS)).all()
        }
        missing = next((key for key in _SETTING_KEYS if key not in rows), None)
        if missing is not None:
            raise ResourceNotFoundError("Configurazione", missing)
        return rows

    @staticmethod
    def _decode(setting: AppSetting) -> Any:
        try:
            return json.loads(setting.value)
        except json.JSONDecodeError as error:
            raise ValueError(f"Valore non valido per la configurazione {setting.key}") from error

    def _response(self, settings: Mapping[str, AppSetting]) -> GeneralSettingsResponse:
        theme = self._decode(settings[_DEFAULT_THEME])
        if theme not in {"light", "dark"}:
            raise ValueError("Tema predefinito non valido")
        return GeneralSettingsResponse(
            organization_name=str(self._decode(settings[_ORGANIZATION_NAME])),
            organization_name_version=settings[_ORGANIZATION_NAME].version,
            archive_google_drive_url=str(self._decode(settings[_ARCHIVE_URL])),
            archive_google_drive_url_version=settings[_ARCHIVE_URL].version,
            default_theme=theme,
            default_theme_version=settings[_DEFAULT_THEME].version,
        )

    @staticmethod
    def _user_response(user: User) -> ResponsibleUserResponse:
        return ResponsibleUserResponse(
            id=user.id,
            email=user.email,
            display_name=user.display_name,
            is_active=user.is_active,
            last_login_at=(
                datetime.fromisoformat(user.last_login_at.replace("Z", "+00:00"))
                if user.last_login_at
                else None
            ),
            version=user.version,
        )
