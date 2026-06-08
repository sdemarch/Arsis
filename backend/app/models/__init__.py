from .insegnante import Insegnante
from .allievo import Allievo
from .corso import Corso, CorsoAllievo
from .piano_rate import PianoRate, Rata
from .riga_pagamento import RigaPagamento, TipoRiga, StatoPagamento, ContoType
from .versamento import Versamento, MetodoPagamento

__all__ = [
    "Insegnante", "Allievo", "Corso", "CorsoAllievo",
    "PianoRate", "Rata", "RigaPagamento", "Versamento",
    "TipoRiga", "StatoPagamento", "ContoType", "MetodoPagamento",
]
