import enum
from datetime import datetime
from decimal import Decimal
from sqlalchemy import String, DECIMAL, TIMESTAMP, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base
from .persona_mixin import PersonaMixin, StatoPersona


class Insegnante(PersonaMixin, Base):
    __tablename__ = "insegnanti"

    id:         Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    stipendio:  Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    corsi       = relationship("Corso", back_populates="insegnante_rel", lazy="selectin")
    pagamenti   = relationship("RigaPagamento", back_populates="insegnante", lazy="selectin",
                               primaryjoin="Insegnante.id == foreign(RigaPagamento.soggetto_id)")
