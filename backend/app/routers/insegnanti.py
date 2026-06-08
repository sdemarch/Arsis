from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import Optional, List
from app.database import get_db
from app.models import Insegnante
from app.models.persona_mixin import StatoPersona
from app.schemas.insegnante import InsegnanteCreate, InsegnanteUpdate, InsegnanteOut

router = APIRouter()


@router.get("", response_model=List[InsegnanteOut])
async def list_insegnanti(
    stato: Optional[StatoPersona] = None,
    db: AsyncSession = Depends(get_db),
):
    stmt = select(Insegnante)
    if stato:
        stmt = stmt.where(Insegnante.stato == stato)
    result = await db.execute(stmt)
    return result.scalars().all()


@router.post("", response_model=InsegnanteOut, status_code=201)
async def create_insegnante(data: InsegnanteCreate, db: AsyncSession = Depends(get_db)):
    ins = Insegnante(**data.model_dump())
    db.add(ins)
    await db.commit()
    await db.refresh(ins)
    return ins


@router.get("/{id}", response_model=InsegnanteOut)
async def get_insegnante(id: int, db: AsyncSession = Depends(get_db)):
    ins = await db.get(Insegnante, id)
    if not ins:
        raise HTTPException(404, "Insegnante non trovato")
    return ins


@router.put("/{id}", response_model=InsegnanteOut)
async def update_insegnante(id: int, data: InsegnanteUpdate, db: AsyncSession = Depends(get_db)):
    ins = await db.get(Insegnante, id)
    if not ins:
        raise HTTPException(404, "Insegnante non trovato")
    for k, v in data.model_dump(exclude_unset=True).items():
        setattr(ins, k, v)
    await db.commit()
    await db.refresh(ins)
    return ins


@router.delete("/{id}", status_code=204)
async def delete_insegnante(id: int, db: AsyncSession = Depends(get_db)):
    ins = await db.get(Insegnante, id)
    if not ins:
        raise HTTPException(404, "Insegnante non trovato")
    ins.stato = StatoPersona.sospeso
    await db.commit()
