from fastapi import APIRouter
from database import get_connection

router = APIRouter()

from pydantic import BaseModel
from typing import Optional


class NNA(BaseModel):
    nombre: str
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    fecha_nacimiento: Optional[str] = None
    sexo: Optional[str] = None
    nacionalidad: Optional[str] = None
    curp: Optional[str] = None
    lugar_nac_pais: Optional[str] = None
    lugar_nac_entidad: Optional[str] = None
    lugar_nac_municipio: Optional[str] = None
    lugar_nac_comunidad: Optional[str] = None
    estado_civil: Optional[str] = None

    calle: Optional[str] = None
    numero_exterior: Optional[str] = None
    numero_interior: Optional[str] = None
    colonia: Optional[str] = None
    codigo_postal: Optional[str] = None
    localidad: Optional[str] = None
    delegacion_municipio: Optional[str] = None
    entidad_federativa: Optional[str] = None
    telefono: Optional[str] = None

    tipo_victima: Optional[str] = None
    nombre_victima_directa: Optional[str] = None
    relacion_victima: Optional[str] = None

    lugar_hechos_calle: Optional[str] = None
    lugar_hechos_colonia: Optional[str] = None
    lugar_hechos_municipio: Optional[str] = None
    lugar_hechos_entidad: Optional[str] = None
    fecha_hechos: Optional[str] = None
    relato_hechos: Optional[str] = None

    dano_fisico: Optional[bool] = False
    dano_psicologico: Optional[bool] = False
    dano_patrimonial: Optional[bool] = False
    dano_sexual: Optional[bool] = False

    denuncio_mp: Optional[bool] = False
    fecha_denuncia_mp: Optional[str] = None
    competencia_mp: Optional[str] = None
    entidad_mp: Optional[str] = None
    delito_mp: Optional[str] = None
    agencia_mp: Optional[str] = None
    numero_averiguacion: Optional[str] = None
    estado_investigacion: Optional[str] = None

    tiene_proceso_judicial: Optional[bool] = False
    fecha_inicio_judicial: Optional[str] = None
    competencia_judicial: Optional[str] = None
    entidad_judicial: Optional[str] = None
    delito_judicial: Optional[str] = None
    numero_juzgado: Optional[str] = None
    numero_proceso: Optional[str] = None
    estado_proceso: Optional[str] = None

    es_menor: Optional[bool] = True
    tutor_nombre: Optional[str] = None
    tutor_primer_apellido: Optional[str] = None
    tutor_segundo_apellido: Optional[str] = None
    tutor_parentesco: Optional[str] = None
    tutor_telefono: Optional[str] = None
    tutor_correo: Optional[str] = None

    tiene_discapacidad: Optional[bool] = False
    tipo_discapacidad: Optional[str] = None   
    grado_dependencia: Optional[str] = None  

    habla_espanol: Optional[bool] = True
    requiere_traductor: Optional[bool] = False
    idioma_lengua: Optional[str] = None
    pertenece_indigena: Optional[bool] = False
    comunidad_indigena: Optional[str] = None
    es_migrante: Optional[bool] = False
    pais_origen: Optional[str] = None

    violencia_psicologica: Optional[bool] = False
    violencia_fisica: Optional[bool] = False
    violencia_economica: Optional[bool] = False
    violencia_patrimonial: Optional[bool] = False
    violencia_sexual: Optional[bool] = False
    violencia_obstetrica: Optional[bool] = False
    violencia_feminicida: Optional[bool] = False
    tipo_violencia: Optional[str] = None

    tipo_solicitante: Optional[str] = None
    nombre_solicitante: Optional[str] = None
    parentesco_solicitante: Optional[str] = None


class CambiarEstatus(BaseModel):
    estatus: str


@router.get("/api/nna")
async def obtener_nna():
    return []

@router.get("/")
async def obtener_nna_raiz():
    return []
    
@router.get("/api/discapacidades")
def obtener_catalogo_discapacidades():
    medio_conexion = get_connection()
    medio = medio_conexion.cursor()
    
    medio.execute("SELECT id_discapacidad, tipo, descripcion, grado_dependencia FROM catalogo_discapacidades")
    
    columnas = [desc[0] for desc in medio.description]
    arreglo_ordenado = [dict(zip(columnas, fila)) for fila in medio.fetchall()]
    
    medio.close()
    medio_conexion.close()
    
    return arreglo_ordenado
