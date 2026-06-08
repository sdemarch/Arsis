from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional, List
from app.models.corso import TipoCorso, StatoCorso
from app.models.piano_rate import RateMode


class RataIn(BaseModel):
    descrizione: str
    scadenza: date
    importo: Decimal
    ordine: int = 0


class PianoRateIn(BaseModel):
    mode: RateMode
    quota_annuale: Decimal
    rate: List[RataIn]


class CorsoBase(BaseModel):
    nome: str
    tipo: TipoCorso
    insegnante_id: Optional[int] = None
    giorno: Optional[str] = None
    orario: Optional[str] = None
    aula: Optional[str] = None
    stato: StatoCorso = StatoCorso.attivo
    color_index: int = 0


class CorsoCreate(CorsoBase):
    piano: PianoRateIn


class CorsoUpdate(CorsoBase):
    nome: Optional[str] = None
    tipo: Optional[TipoCorso] = None


class RataOut(RataIn):
    id: int
    model_config = {"from_attributes": True}


class PianoRateOut(BaseModel):
    id: int
    mode: RateMode
    quota_annuale: Decimal
    rate: List[RataOut]
    model_config = {"from_attributes": True}


class CorsoOut(CorsoBase):
    id: int
    piano: Optional[PianoRateOut] = None
    model_config = {"from_attributes": True}
