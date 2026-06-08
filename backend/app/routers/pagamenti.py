from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Optional, List
from decimal import Decimal
from app.database import get_db
from app.models import RigaPagamento, Versamento
from app.models.riga_pagamento import TipoRiga, StatoPagamento, ContoType
from app.schemas.pagamento import RigaCreate, RigaOut, VersamentoCreate, VersamentoOut, SaldiOut

router = APIRouter()


@router.get("", response_model=List[RigaOut])
async def list_righe(
    tipo: Optional[TipoRiga] = None,
    stato: Optional[StatoPagamento] = None,
    conto: Optional[ContoType] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(RigaPagamento)
    if tipo:  stmt = stmt.where(RigaPagamento.tipo == tipo)
    if stato: stmt = stmt.where(RigaPagamento.stato == stato)
    if conto: stmt = stmt.where(RigaPagamento.conto == conto)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=RigaOut, status_code=201)
async def create_riga(data: RigaCreate, db: AsyncSession = Depends(get_db)):
    riga = RigaPagamento(**data.model_dump())
    db.add(riga)
    await db.commit()
    await db.refresh(riga)
    return riga


@router.get("/saldi", response_model=SaldiOut)
async def get_saldi(db: AsyncSession = Depends(get_db)):
    """Calcola saldi aggregati da tutti i versamenti."""
    result = await db.execute(
        select(
            RigaPagamento.tipo,
            RigaPagamento.conto,
            func.sum(Versamento.importo).label("totale"),
        )
        .join(Versamento, Versamento.riga_id == RigaPagamento.id)
        .group_by(RigaPagamento.tipo, RigaPagamento.conto)
    )
    rows = result.all()

    banca_in = banca_out = cassa_in = cassa_out = Decimal("0")
    for tipo, conto, totale in rows:
        if tipo == TipoRiga.allievo:
            if conto == ContoType.banca: banca_in += totale
            else: cassa_in += totale
        elif tipo == TipoRiga.insegnante:
            if conto == ContoType.banca: banca_out += totale
            else: cassa_out += totale

    return SaldiOut(banca_in=banca_in, banca_out=banca_out, cassa_in=cassa_in, cassa_out=cassa_out)


@router.get("/scaduti", response_model=List[RigaOut])
async def get_scaduti(db: AsyncSession = Depends(get_db)):
    stmt = select(RigaPagamento).where(RigaPagamento.stato == StatoPagamento.scaduto)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.get("/{id}", response_model=RigaOut)
async def get_riga(id: int, db: AsyncSession = Depends(get_db)):
    r = await db.get(RigaPagamento, id)
    if not r:
        raise HTTPException(404, "Riga non trovata")
    return r


@router.post("/{id}/versamenti", response_model=VersamentoOut, status_code=201)
async def add_versamento(id: int, data: VersamentoCreate, db: AsyncSession = Depends(get_db)):
    riga = await db.get(RigaPagamento, id)
    if not riga:
        raise HTTPException(404, "Riga non trovata")
    v = Versamento(riga_id=id, **data.model_dump())
    db.add(v)
    await db.commit()
    await db.refresh(v)
    return v
