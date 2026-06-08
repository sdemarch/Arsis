from pydantic import BaseModel
from decimal import Decimal
from datetime import date
from typing import Optional, List
from app.models.riga_pagamento import TipoRiga, StatoPagamento, ContoType
from app.models.versamento import MetodoPagamento


class VersamentoCreate(BaseModel):
    data: date
    importo: Decimal
    metodo: MetodoPagamento
    note: Optional[str] = None


class VersamentoOut(VersamentoCreate):
    id: int
    riga_id: int
    model_config = {"from_attributes": True}


class RigaCreate(BaseModel):
    tipo: TipoRiga
    soggetto_id: Optional[int] = None
    corso_id: Optional[int] = None
    rata_id: Optional[int] = None
    descrizione: str
    categoria: Optional[str] = None
    scadenza: date
    importo_totale: Decimal
    stato: StatoPagamento
    conto: ContoType = ContoType.banca


class RigaOut(RigaCreate):
    id: int
    versamenti: List[VersamentoOut] = []
    model_config = {"from_attributes": True}


class SaldiOut(BaseModel):
    banca_in: Decimal
    banca_out: Decimal
    cassa_in: Decimal
    cassa_out: Decimal
