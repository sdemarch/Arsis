import enum
from decimal import Decimal
from datetime import date
from sqlalchemy import String, Integer, ForeignKey, DECIMAL, Date, Enum as SAEnum
from sqlalchemy.orm import mapped_column, Mapped, relationship
from app.database import Base


class RateMode(str, enum.Enum):
    tre_rate  = "3rate"
    quattro_rate = "4rate"
    custom    = "custom"


class PianoRate(Base):
    __tablename__ = "piani_rate"

    id:            Mapped[int]       = mapped_column(primary_key=True, autoincrement=True)
    corso_id:      Mapped[int]       = mapped_column(Integer, ForeignKey("corsi.id"), unique=True)
    mode:          Mapped[RateMode]  = mapped_column(SAEnum(RateMode), nullable=False)
    quota_annuale: Mapped[Decimal]   = mapped_column(DECIMAL(10, 2), nullable=False)

    corso = relationship("Corso", back_populates="piano")
    rate  = relationship("Rata", back_populates="piano", order_by="Rata.ordine", lazy="selectin")


class Rata(Base):
    __tablename__ = "rate"

    id:          Mapped[int]     = mapped_column(primary_key=True, autoincrement=True)
    piano_id:    Mapped[int]     = mapped_column(Integer, ForeignKey("piani_rate.id"))
    descrizione: Mapped[str]     = mapped_column(String(100), nullable=False)
    scadenza:    Mapped[date]    = mapped_column(Date, nullable=False)
    importo:     Mapped[Decimal] = mapped_column(DECIMAL(10, 2), nullable=False)
    ordine:      Mapped[int]     = mapped_column(default=0)

    piano = relationship("PianoRate", back_populates="rate")
