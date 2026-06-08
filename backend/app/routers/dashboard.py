from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from datetime import date, timedelta
from app.database import get_db
from app.models import Allievo, Corso, RigaPagamento, Versamento
from app.models.riga_pagamento import StatoPagamento, TipoRiga
from app.models.persona_mixin import StatoPersona
from app.models.corso import StatoCorso

router = APIRouter()


@router.get("/summary")
async def get_summary(db: AsyncSession = Depends(get_db)):
    allievi_count = (await db.execute(
        select(func.count()).select_from(Allievo).where(Allievo.stato == StatoPersona.attivo)
    )).scalar()

    corsi_count = (await db.execute(
        select(func.count()).select_from(Corso).where(Corso.stato == StatoCorso.attivo)
    )).scalar()

    incasso = (await db.execute(
        select(func.coalesce(func.sum(Versamento.importo), 0))
        .join(RigaPagamento, Versamento.riga_id == RigaPagamento.id)
        .where(RigaPagamento.tipo == TipoRiga.allievo)
    )).scalar()

    scaduto = (await db.execute(
        select(func.coalesce(func.sum(RigaPagamento.importo_totale), 0))
        .where(RigaPagamento.stato == StatoPagamento.scaduto)
    )).scalar()

    return {
        "allievi_attivi": allievi_count,
        "corsi_attivi": corsi_count,
        "incasso_totale": float(incasso),
        "scaduto_totale": float(scaduto),
    }


@router.get("/attivita")
async def get_attivita(limit: int = 20, db: AsyncSession = Depends(get_db)):
    result = await db.execute(
        select(Versamento).order_by(Versamento.created_at.desc()).limit(limit)
    )
    return result.scalars().all()
