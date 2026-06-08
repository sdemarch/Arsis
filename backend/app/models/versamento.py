import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, DECIMAL, Date, TIMESTAMP, Enum as SAEnum, func, Text
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base


class MetodoPagamento(str, enum.Enum):
    bonifico      = "bonifico"
    contanti      = "contanti"
    pos           = "pos"
    domiciliazione = "domiciliazione"
    assegno       = "assegno"


class Versamento(Base):
    __tablename__ = "versamenti"

    id:         Mapped[int]              = mapped_column(primary_key=True, autoincrement=True)
    riga_id:    Mapped[int]              = mapped_column(Integer, ForeignKey("righe_pagamento.id"), nullable=False)
    data:       Mapped[date]             = mapped_column(Date, nullable=False)
    importo:    Mapped[Decimal]          = mapped_column(DECIMAL(10, 2), nullable=False)
    metodo:     Mapped[MetodoPagamento]  = mapped_column(SAEnum(MetodoPagamento), nullable=False)
    note:       Mapped[str | None]       = mapped_column(Text)
    created_at: Mapped[datetime]         = mapped_column(TIMESTAMP, server_default=func.now())

    riga = relationship("RigaPagamento", back_populates="versamenti")
