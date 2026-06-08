"""Business logic per pagamenti: calcolo saldi, generazione rate, aggiornamento stato."""
from datetime import date
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models import RigaPagamento, Versamento, PianoRate, CorsoAllievo
from app.models.riga_pagamento import TipoRiga, StatoPagamento, ContoType


def calcola_stato(importo_totale: Decimal, versato: Decimal, scadenza: date) -> StatoPagamento:
    if versato >= importo_totale:
        return StatoPagamento.pagato
    oggi = date.today()
    if scadenza < oggi:
        return StatoPagamento.scaduto
    if scadenza <= oggi + timedelta(days=30):
        return StatoPagamento.in_scadenza
    return StatoPagamento.futuro


async def genera_righe_per_allievo(
    db: AsyncSession,
    allievo_id: int,
    corso_id: int,
    piano: PianoRate,
    conto: ContoType = ContoType.banca,
) -> list[RigaPagamento]:
    """Crea RigaPagamento per ogni rata del piano per un allievo."""
    from datetime import timedelta
    righe = []
    for rata in piano.rate:
        stato = calcola_stato(rata.importo, Decimal("0"), rata.scadenza)
        riga = RigaPagamento(
            tipo=TipoRiga.allievo,
            soggetto_id=allievo_id,
            corso_id=corso_id,
            rata_id=rata.id,
            descrizione=rata.descrizione,
            scadenza=rata.scadenza,
            importo_totale=rata.importo,
            stato=stato,
            conto=conto,
        )
        db.add(riga)
        righe.append(riga)
    await db.flush()
    return righe


async def aggiorna_stato_riga(db: AsyncSession, riga_id: int) -> RigaPagamento:
    """Ricalcola lo stato di una riga dopo un versamento."""
    riga = await db.get(RigaPagamento, riga_id)
    versato = (await db.execute(
        select(func.coalesce(func.sum(Versamento.importo), 0))
        .where(Versamento.riga_id == riga_id)
    )).scalar()
    riga.stato = calcola_stato(riga.importo_totale, Decimal(str(versato)), riga.scadenza)
    await db.flush()
    return riga
