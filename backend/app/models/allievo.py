from datetime import datetime
from sqlalchemy import TIMESTAMP, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base
from .persona_mixin import PersonaMixin


class Allievo(PersonaMixin, Base):
    __tablename__ = "allievi"

    id:         Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    created_at: Mapped[datetime] = mapped_column(TIMESTAMP, server_default=func.now())

    corsi     = relationship("Corso", secondary="corso_allievi", back_populates="allievi_rel", lazy="selectin")
    pagamenti = relationship("RigaPagamento", back_populates="allievo", lazy="selectin",
                             primaryjoin="Allievo.id == foreign(RigaPagamento.soggetto_id)")
