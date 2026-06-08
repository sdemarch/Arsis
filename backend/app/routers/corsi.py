from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.database import get_db
from app.models import Corso, PianoRate, Rata, CorsoAllievo, Allievo
from app.models.corso import StatoCorso, TipoCorso
from app.schemas.corso import CorsoCreate, CorsoUpdate, CorsoOut, PianoRateIn, PianoRateOut

router = APIRouter()


@router.get("", response_model=List[CorsoOut])
async def list_corsi(
    stato: Optional[StatoCorso] = None,
    tipo: Optional[TipoCorso] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Corso)
    if stato:
        stmt = stmt.where(Corso.stato == stato)
    if tipo:
        stmt = stmt.where(Corso.tipo == tipo)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=CorsoOut, status_code=201)
async def create_corso(data: CorsoCreate, db: AsyncSession = Depends(get_db)):
    piano_data = data.piano
    corso_data = data.model_dump(exclude={"piano"})
    corso = Corso(**corso_data)
    db.add(corso)
    await db.flush()  # get corso.id

    piano = PianoRate(
        corso_id=corso.id,
        mode=piano_data.mode,
        quota_annuale=piano_data.quota_annuale,
    )
    db.add(piano)
    await db.flush()

    for r in piano_data.rate:
        db.add(Rata(piano_id=piano.id, **r.model_dump()))

    await db.commit()
    await db.refresh(corso)
    return corso


@router.get("/{id}", response_model=CorsoOut)
async def get_corso(id: int, db: AsyncSession = Depends(get_db)):
    c = await db.get(Corso, id)
    if not c:
        raise HTTPException(404, "Corso non trovato")
    return c


@router.put("/{id}", response_model=CorsoOut)
async def update_corso(id: int, data: CorsoUpdate, db: AsyncSession = Depends(get_db)):
    c = await db.get(Corso, id)
    if not c:
        raise HTTPException(404, "Corso non trovato")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(c, k, v)
    await db.commit()
    await db.refresh(c)
    return c


@router.post("/{id}/allievi", status_code=204)
async def iscrivi_allievo(id: int, allievo_id: int, db: AsyncSession = Depends(get_db)):
    db.add(CorsoAllievo(corso_id=id, allievo_id=allievo_id))
    await db.commit()


@router.delete("/{id}/allievi/{allievo_id}", status_code=204)
async def rimuovi_allievo(id: int, allievo_id: int, db: AsyncSession = Depends(get_db)):
    ca = await db.get(CorsoAllievo, (id, allievo_id))
    if not ca:
        raise HTTPException(404, "Iscrizione non trovata")
    await db.delete(ca)
    await db.commit()


@router.put("/{id}/piano-rate", response_model=PianoRateOut)
async def update_piano_rate(id: int, data: PianoRateIn, db: AsyncSession = Depends(get_db)):
    corso = await db.get(Corso, id)
    if not corso:
        raise HTTPException(404, "Corso non trovato")
    piano = corso.piano
    if not piano:
        raise HTTPException(404, "Piano rate non trovato")
    piano.mode = data.mode
    piano.quota_annuale = data.quota_annuale
    # replace rate
    for r in piano.rate:
        await db.delete(r)
    await db.flush()
    for r in data.rate:
        db.add(Rata(piano_id=piano.id, **r.model_dump()))
    await db.commit()
    await db.refresh(piano)
    return piano
