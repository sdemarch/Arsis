import enum
from datetime import datetime, date
from decimal import Decimal
from sqlalchemy import String, Integer, ForeignKey, DECIMAL, Date, TIMESTAMP, Enum as SAEnum, func
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base


class TipoRiga(str, enum.Enum):
    allievo    = "allievo"
    insegnante = "insegnante"
    generico   = "generico"


class StatoPagamento(str, enum.Enum):
    pagato       = "pagato"
    in_scadenza  = "in scadenza"
    scaduto      = "scaduto"
    futuro       = "futuro"


class ContoType(str, enum.Enum):
    banca = "banca"
    cassa = "cassa"


class RigaPagamento(Base):
    __tablename__ = "righe_pagamento"

    id:             Mapped[int]           = mapped_column(primary_key=True, autoincrement=True)
    tipo:           Mapped[TipoRiga]      = mapped_column(SAEnum(TipoRiga), nullable=False)
    soggetto_id:    Mapped[int | None]    = mapped_column(Integer, nullable=True)
    corso_id:       Mapped[int | None]    = mapped_column(Integer, ForeignKey("corsi.id"), nullable=True)
    rata_id:        Mapped[int | None]    = mapped_column(Integer, ForeignKey("rate.id"), nullable=True)
    descrizione:    Mapped[str]           = mapped_column(String(200), nullable=False)
    categoria:      Mapped[str | None]    = mapped_column(String(100))
    scadenza:       Mapped[date]          = mapped_column(Date, nullable=False)
    importo_totale: Mapped[Decimal]       = mapped_column(DECIMAL(10, 2), nullable=False)
    stato:          Mapped[StatoPagamento] = mapped_column(SAEnum(StatoPagamento), nullable=False)
    conto:          Mapped[ContoType]     = mapped_column(SAEnum(ContoType), default=ContoType.banca)
    created_at:     Mapped[datetime]      = mapped_column(TIMESTAMP, server_default=func.now())

    versamenti = relationship("Versamento", back_populates="riga", lazy="selectin",
                              order_by="Versamento.data")
    allievo    = relationship("Allievo", foreign_keys=[soggetto_id],
                              primaryjoin="and_(RigaPagamento.soggetto_id == Allievo.id, RigaPagamento.tipo == 'allievo')",
                              lazy="selectin", viewonly=True)
    insegnante = relationship("Insegnante", foreign_keys=[soggetto_id],
                              primaryjoin="and_(RigaPagamento.soggetto_id == Insegnante.id, RigaPagamento.tipo == 'insegnante')",
                              lazy="selectin", viewonly=True)
