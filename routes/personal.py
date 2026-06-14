from pydantic import BaseModel
from typing import Optional


class Personal(BaseModel):
    nombre: str
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    rfc: Optional[str] = None
    curp: Optional[str] = None
    sexo: Optional[str] = None
    edad: Optional[int] = None
    direccion: Optional[str] = None
    correo: str
    contrasena: str
    tipo: Optional[str] = None          # empleado | voluntario
    rol: Optional[str] = None           # director | coordinador | psicologo | ...
    estado: Optional[str] = "pendiente" # activo | inactivo | pendiente | restringido


class ActualizarPersonal(BaseModel):
    nombre: Optional[str] = None
    primer_apellido: Optional[str] = None
    segundo_apellido: Optional[str] = None
    rfc: Optional[str] = None
    curp: Optional[str] = None
    sexo: Optional[str] = None
    edad: Optional[int] = None
    direccion: Optional[str] = None
    tipo: Optional[str] = None


class CambiarRol(BaseModel):
    rol: str     # director | coordinador | psicologo | doctor | abogado | ...
    estado: str  # activo | inactivo | pendiente | restringido
