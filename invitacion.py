from pydantic import BaseModel
from typing import Optional


class Invitacion(BaseModel):
    token: str
    creado_por: Optional[int] = None   # id del personal que generó el link
    usado: Optional[bool] = False


class GenerarInvitacion(BaseModel):
    horas_expiracion: Optional[int] = 48  # por defecto 48 hrs según el README
