import enum
from datetime import datetime, date
from sqlalchemy import String, Integer, ForeignKey, TIMESTAMP, Date, Enum as SAEnum, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base


class TipoCorso(str, enum.Enum):
    collettivo = "collettivo"
    individuale = "individuale"


class StatoCorso(str, enum.Enum):
    attivo = "attivo"
    sospeso = "sospeso"
    concluso = "concluso"


class Corso(Base):
    __tablename__ = "corsi"

    id:            Mapped[int]        = mapped_column(primary_key=True, autoincrement=True)
    nome:          Mapped[str]        = mapped_column(String(150), nullable=False)
    tipo:          Mapped[TipoCorso]  = mapped_column(SAEnum(TipoCorso), nullable=False)
    insegnante_id: Mapped[int | None] = mapped_column(Integer, ForeignKey("insegnanti.id"), nullable=True)
    giorno:        Mapped[str | None] = mapped_column(String(50))
    orario:        Mapped[str | None] = mapped_column(String(50))
    aula:          Mapped[str | None] = mapped_column(String(100))
    stato:         Mapped[StatoCorso] = mapped_column(SAEnum(StatoCorso), default=StatoCorso.attivo)
    color_index:   Mapped[int]        = mapped_column(default=0)
    created_at:    Mapped[datetime]   = mapped_column(TIMESTAMP, server_default=func.now())

    insegnante_rel = relationship("Insegnante", back_populates="corsi", lazy="selectin")
    allievi_rel    = relationship("Allievo", secondary="corso_allievi", back_populates="corsi", lazy="selectin")
    piano          = relationship("PianoRate", back_populates="corso", uselist=False, lazy="selectin")


class CorsoAllievo(Base):
    __tablename__ = "corso_allievi"

    corso_id:        Mapped[int]        = mapped_column(Integer, ForeignKey("corsi.id"), primary_key=True)
    allievo_id:      Mapped[int]        = mapped_column(Integer, ForeignKey("allievi.id"), primary_key=True)
    data_iscrizione: Mapped[date | None] = mapped_column(Date)
