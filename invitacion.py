from pydantic import BaseModel
from typing import Optional


class Invitacion(BaseModel):
    token: str
    creado_por: Optional[int] = None 
    usado: Optional[bool] = False


class GenerarInvitacion(BaseModel):
    horas_expiracion: Optional[int] = 48 
