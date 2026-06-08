from pydantic import BaseModel, EmailStr
from datetime import date
from decimal import Decimal
from typing import Optional
from app.models.persona_mixin import StatoPersona


class InsegnanteBase(BaseModel):
    nome: str
    cognome: str
    email: EmailStr
    tel: Optional[str] = None
    data_nascita: Optional[date] = None
    codice_fiscale: Optional[str] = None
    indirizzo: Optional[str] = None
    stato: StatoPersona = StatoPersona.attivo
    avatar_color: Optional[str] = None
    stipendio: Decimal


class InsegnanteCreate(InsegnanteBase):
    pass


class InsegnanteUpdate(InsegnanteBase):
    nome: Optional[str] = None
    cognome: Optional[str] = None
    email: Optional[EmailStr] = None
    stipendio: Optional[Decimal] = None


class InsegnanteOut(InsegnanteBase):
    id: int

    model_config = {"from_attributes": True}
