from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.database import get_db
from app.models import Allievo
from app.models.persona_mixin import StatoPersona
from app.schemas.allievo import AllievCreate, AllievUpdate, AllievOut

router = APIRouter()


@router.get("", response_model=List[AllievOut])
async def list_allievi(
    stato: Optional[StatoPersona] = None,
    corso_id: Optional[int] = None,
    q: Optional[str] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Allievo)
    if stato:
        stmt = stmt.where(Allievo.stato == stato)
    if q:
        stmt = stmt.where(
            (Allievo.nome.ilike(f"%{q}%")) | (Allievo.cognome.ilike(f"%{q}%"))
        )
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=AllievOut, status_code=201)
async def create_allievo(data: AllievCreate, db: AsyncSession = Depends(get_db)):
    allievo = Allievo(**data.model_dump())
    db.add(allievo)
    await db.commit()
    await db.refresh(allievo)
    return allievo


@router.get("/{id}", response_model=AllievOut)
async def get_allievo(id: int, db: AsyncSession = Depends(get_db)):
    a = await db.get(Allievo, id)
    if not a:
        raise HTTPException(404, "Allievo non trovato")
    return a


@router.put("/{id}", response_model=AllievOut)
async def update_allievo(id: int, data: AllievUpdate, db: AsyncSession = Depends(get_db)):
    a = await db.get(Allievo, id)
    if not a:
        raise HTTPException(404, "Allievo non trovato")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(a, k, v)
    await db.commit()
    await db.refresh(a)
    return a


@router.delete("/{id}", status_code=204)
async def delete_allievo(id: int, db: AsyncSession = Depends(get_db)):
    """Soft delete: setta stato = sospeso."""
    a = await db.get(Allievo, id)
    if not a:
        raise HTTPException(404, "Allievo non trovato")
    a.stato = StatoPersona.sospeso
    await db.commit()
