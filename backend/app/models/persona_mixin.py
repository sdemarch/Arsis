"""Mixin condiviso tra Allievo e Insegnante."""
import enum
from sqlalchemy import String, Date, Enum as SAEnum
from sqlalchemy.orm import mapped_column, MappedColumn
from datetime import date


class StatoPersona(str, enum.Enum):
    attivo = "attivo"
    sospeso = "sospeso"


class PersonaMixin:
    nome:           MappedColumn[str]  = mapped_column(String(100), nullable=False)
    cognome:        MappedColumn[str]  = mapped_column(String(100), nullable=False)
    email:          MappedColumn[str]  = mapped_column(String(150), unique=True, nullable=False)
    tel:            MappedColumn[str | None] = mapped_column(String(20))
    data_nascita:   MappedColumn[date | None] = mapped_column(Date)
    codice_fiscale: MappedColumn[str | None] = mapped_column(String(16), unique=True)
    indirizzo:      MappedColumn[str | None] = mapped_column(String(300))
    stato:          MappedColumn[StatoPersona] = mapped_column(
        SAEnum(StatoPersona), default=StatoPersona.attivo, nullable=False
    )
    avatar_color:   MappedColumn[str | None] = mapped_column(String(20))
