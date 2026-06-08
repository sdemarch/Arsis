from pydantic import BaseModel, EmailStr
from datetime import date
from typing import Optional
from app.models.persona_mixin import StatoPersona


class AllievBase(BaseModel):
    nome: str
    cognome: str
    email: EmailStr
    tel: Optional[str] = None
    data_nascita: Optional[date] = None
    codice_fiscale: Optional[str] = None
    indirizzo: Optional[str] = None
    stato: StatoPersona = StatoPersona.attivo
    avatar_color: Optional[str] = None


class AllievCreate(AllievBase):
    pass


class AllievUpdate(AllievBase):
    nome: Optional[str] = None
    cognome: Optional[str] = None
    email: Optional[EmailStr] = None


class AllievOut(AllievBase):
    id: int

    model_config = {"from_attributes": True}
