from fastapi import APIRouter, HTTPException
from database import get_connection
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter()

class NNA(BaseModel):
    # ── Datos básicos ──
    nombre: str = Field(..., max_length=50)
    primer_apellido: str = Field(..., max_length=50)
    segundo_apellido: Optional[str] = Field(None, max_length=50)
    fecha_nacimiento: Optional[str] = None
    edad: Optional[int] = Field(None, ge=0, le=99)
    sexo: Optional[str] = None
    nacionalidad: Optional[str] = Field(None, max_length=50)
    curp: Optional[str] = Field(None, min_length=18, max_length=18)
    rfc: Optional[str] = Field(None, min_length=13, max_length=13)
    estado_civil: Optional[str] = None
    lugar_nac_pais: Optional[str] = Field(None, max_length=50)
    lugar_nac_entidad: Optional[str] = Field(None, max_length=100)
    lugar_nac_municipio: Optional[str] = Field(None, max_length=100)
    lugar_nac_comunidad: Optional[str] = Field(None, max_length=100)

    # ── Domicilio ──
    calle: Optional[str] = Field(None, max_length=150)
    numero_exterior: Optional[str] = Field(None, max_length=20)
    numero_interior: Optional[str] = Field(None, max_length=20)
    colonia: Optional[str] = Field(None, max_length=100)
    codigo_postal: Optional[str] = Field(None, max_length=5)
    localidad: Optional[str] = Field(None, max_length=100)
    delegacion_municipio: Optional[str] = Field(None, max_length=100)
    entidad_federativa: Optional[str] = Field(None, max_length=100)
    telefono: Optional[str] = Field(None, max_length=10)

    # ── Tipo de víctima y Hechos ──
    tipo_victima: Optional[str] = None
    nombre_victima_directa: Optional[str] = Field(None, max_length=100)
    relacion_victima: Optional[str] = Field(None, max_length=50)
    lugar_hechos_calle: Optional[str] = Field(None, max_length=150)
    lugar_hechos_colonia: Optional[str] = Field(None, max_length=100)
    lugar_hechos_municipio: Optional[str] = Field(None, max_length=100)
    lugar_hechos_entidad: Optional[str] = Field(None, max_length=100)
    fecha_hechos: Optional[str] = None
    relato_hechos: Optional[str] = Field(None, max_length=2000)

    # ── Daños e Investigación ──
    dano_fisico: Optional[bool] = False
    dano_psicologico: Optional[bool] = False
    dano_patrimonial: Optional[bool] = False
    dano_sexual: Optional[bool] = False
    denuncio_mp: Optional[bool] = False
    fecha_denuncia_mp: Optional[str] = None
    competencia_mp: Optional[str] = None
    entidad_mp: Optional[str] = Field(None, max_length=100)
    delito_mp: Optional[str] = Field(None, max_length=100)
    agencia_mp: Optional[str] = Field(None, max_length=100)
    numero_averiguacion: Optional[str] = Field(None, max_length=50)
    estado_investigacion: Optional[str] = Field(None, max_length=100)

    # ── Red de Apoyo (Tutor) ──
    nombre_tutor: Optional[str] = Field(None, max_length=100)
    telefono_tutor: Optional[str] = Field(None, max_length=10)
    correo_tutor: Optional[str] = Field(None, max_length=100)
    id_parentesco: Optional[int] = None

    contacto_emergencia_1: Optional[str] = Field(None, max_length=100)
    telefono_emergencia_1: Optional[str] = Field(None, max_length=10)
    contacto_emergencia_2: Optional[str] = Field(None, max_length=100)
    telefono_emergencia_2: Optional[str] = Field(None, max_length=10)

    tipo_violencia: Optional[str] = None
    tiene_discapacidad: Optional[bool] = False
    tipo_discapacidad: Optional[str] = None
    grado_dependencia: Optional[str] = None
    habla_espanol: Optional[bool] = True
    requiere_traductor: Optional[bool] = False
    idioma_lengua: Optional[str] = Field(None, max_length=50)
    pertenece_indigena: Optional[bool] = False
    comunidad_indigena: Optional[str] = Field(None, max_length=100)

    tipo_solicitante: Optional[str] = None
    nombre_solicitante: Optional[str] = Field(None, max_length=100)
    parentesco_solicitante: Optional[str] = Field(None, max_length=50)

    # ── Catálogos (Aseguramos que siempre lleguen como listas válidas) ──
    ids_enfermedades: List[int] = []
    ids_enfermedades_tutor: List[int] = []
    ids_variantes_lengua: List[int] = []

@router.get("/api/nna")
def obtener_nna():
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM nna ORDER BY 1 DESC")
        columnas = [desc[0] for desc in cursor.description]
        expedientes = [dict(zip(columnas, fila)) for fila in cursor.fetchall()]
        cursor.close()
        conexion.close()
        return expedientes
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/api/nna")
def crear_nna(nna: NNA):
    conexion = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        
        # 1. Procesar al Tutor (División inteligente de nombre para evitar errores NOT NULL)
        id_tutor_insertado = None
        if nna.nombre_tutor:
            partes = nna.nombre_tutor.strip().split()
            tutor_nom = partes[0] if len(partes) > 0 else "N/A"
            tutor_ap1 = partes[1] if len(partes) > 1 else "N/A"
            tutor_ap2 = " ".join(partes[2:]) if len(partes) > 2 else ""

            cursor.execute("""
                INSERT INTO tutores (nombre, primer_apellido, segundo_apellido, telefono, correo, id_parentesco) 
                VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
            """, (tutor_nom, tutor_ap1, tutor_ap2, nna.telefono_tutor, nna.correo_tutor, nna.id_parentesco))
            id_tutor_insertado = cursor.fetchone()[0]
            
            if nna.ids_enfermedades_tutor:
                for id_enf in nna.ids_enfermedades_tutor:
                    cursor.execute("INSERT INTO padece_tutor (id_tutor, id_enfermedad, esta_controlada) VALUES (%s, %s, false)", (id_tutor_insertado, id_enf))

        # 2. Insertar al NNA
        cursor.execute("""
            INSERT INTO nna (nombre, primer_apellido, segundo_apellido, edad, curp, id_tutor) 
            VALUES (%s, %s, %s, %s, %s, %s) RETURNING id
        """, (nna.nombre, nna.primer_apellido, nna.segundo_apellido, nna.edad, nna.curp, id_tutor_insertado))
        id_nna_insertado = cursor.fetchone()[0]

        # 3. Vincular Catálogos del NNA
        if nna.ids_enfermedades:
            for id_enf in nna.ids_enfermedades:
                cursor.execute("INSERT INTO padece_nna (id_nna, id_enfermedad, esta_controlada) VALUES (%s, %s, false)", (id_nna_insertado, id_enf))
                
        if nna.ids_variantes_lengua:
            for id_var in nna.ids_variantes_lengua:
                cursor.execute("INSERT INTO habla_nna (id_nna, id_lengua) VALUES (%s, %s)", (id_nna_insertado, id_var))

        conexion.commit()
        return {"mensaje": "Expediente guardado exitosamente", "id_nna": id_nna_insertado}
        
    except Exception as e:
        if conexion:
            conexion.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conexion:
            cursor.close()
            conexion.close()

# ── Rutas de Catálogos para los menús desplegables ──
@router.get("/api/parentescos")
def obtener_parentescos():
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre FROM parentescos ORDER BY nombre ASC")
    resultados = [dict(zip([d[0] for d in cursor.description], fila)) for fila in cursor.fetchall()]
    cursor.close()
    conexion.close()
    return resultados

@router.get("/api/enfermedades")
def obtener_enfermedades():
    conexion = get_connection()
    cursor = conexion.cursor()
    # ESTA ES LA LÍNEA QUE CAMBIA: Ahora apunta a catalogo_enfermedades
    cursor.execute("SELECT id, nombre FROM catalogo_enfermedades ORDER BY nombre ASC")
    resultados = [dict(zip([d[0] for d in cursor.description], fila)) for fila in cursor.fetchall()]
    cursor.close()
    conexion.close()
    return resultados
    
# ── RUTAS DE LOS NUEVOS CATÁLOGOS ──

@router.get("/api/lenguas")
def obtener_lenguas():
    conexion = get_connection()
    cursor = conexion.cursor()
    # Traemos las variantes del INALI
    cursor.execute("SELECT id, variante as nombre FROM catalogo_lenguas ORDER BY variante ASC")
    resultados = [dict(zip([d[0] for d in cursor.description], fila)) for fila in cursor.fetchall()]
    cursor.close()
    conexion.close()
    return resultados

@router.get("/api/sepomex/{cp}")
def buscar_cp(cp: str):
    conexion = get_connection()
    cursor = conexion.cursor()
    # Buscamos todas las colonias de ese CP
    cursor.execute("""
        SELECT id, asentamiento as colonia, municipio, entidad_federativa 
        FROM catalogo_sepomex 
        WHERE codigo_postal = %s
    """, (cp,))
    resultados = [dict(zip([d[0] for d in cursor.description], fila)) for fila in cursor.fetchall()]
    cursor.close()
    conexion.close()
    
    if not resultados:
        raise HTTPException(status_code=404, detail="Código Postal no encontrado en SEPOMEX")
    
    # Devolvemos la entidad, municipio y la lista de colonias posibles
    return {
        "entidad": resultados[0]["entidad_federativa"],
        "municipio": resultados[0]["municipio"],
        "colonias": [{"id": r["id"], "nombre": r["colonia"]} for r in resultados]
    }
    
#NUEVO AGREGADO    
    
@router.get("/api/nna/{id}")
def ver_nna(id: int):
    conexion = get_connection()
    cursor = conexion.cursor()
    
    # 1. Obtener datos básicos
    cursor.execute("SELECT * FROM nna WHERE id = %s", (id,))
    row = cursor.fetchone()
    if not row:
        cursor.close()
        conexion.close()
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
        
    nna_data = dict(zip([d[0] for d in cursor.description], row))
    
    # 2. Obtener datos del Tutor (si existe)
    if nna_data.get('id_tutor'):
        cursor.execute("SELECT nombre as nombre_tutor, telefono as telefono_tutor, correo as correo_tutor, id_parentesco FROM tutores WHERE id = %s", (nna_data['id_tutor'],))
        tutor_row = cursor.fetchone()
        if tutor_row:
            nna_data.update(dict(zip([d[0] for d in cursor.description], tutor_row)))
            
        # Enfermedades del Tutor
        cursor.execute("SELECT id_enfermedad FROM padece_tutor WHERE id_tutor = %s", (nna_data['id_tutor'],))
        nna_data['ids_enfermedades_tutor'] = [r[0] for r in cursor.fetchall()]

    # 3. Obtener tablas puente del NNA
    cursor.execute("SELECT id_enfermedad FROM padece_nna WHERE id_nna = %s", (id,))
    nna_data['ids_enfermedades'] = [r[0] for r in cursor.fetchall()]
    
    cursor.execute("SELECT id_lengua FROM habla_nna WHERE id_nna = %s", (id,))
    nna_data['ids_variantes_lengua'] = [r[0] for r in cursor.fetchall()]
    
    cursor.close()
    conexion.close()
    return nna_data

@router.put("/api/nna/{id}")
def actualizar_nna(id: int, data: NNA):
    conexion = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        
        # Obtener el id_tutor actual
        cursor.execute("SELECT id_tutor FROM nna WHERE id = %s", (id,))
        id_tutor = cursor.fetchone()[0]
        
        # 1. Actualizar NNA
        cursor.execute("""
            UPDATE nna SET nombre=%s, primer_apellido=%s, segundo_apellido=%s, 
            edad=%s, curp=%s, rfc=%s, codigo_postal=%s, telefono=%s
            WHERE id=%s
        """, (data.nombre, data.primer_apellido, data.segundo_apellido, data.edad, 
              data.curp, data.rfc, data.codigo_postal, data.telefono, id))
              
        # 2. Limpiar y recrear tablas puente (Es la forma más segura de actualizar listas)
        cursor.execute("DELETE FROM padece_nna WHERE id_nna = %s", (id,))
        for id_enf in data.ids_enfermedades:
            cursor.execute("INSERT INTO padece_nna (id_nna, id_enfermedad) VALUES (%s, %s)", (id, id_enf))
            
        cursor.execute("DELETE FROM habla_nna WHERE id_nna = %s", (id,))
        for id_var in data.ids_variantes_lengua:
            cursor.execute("INSERT INTO habla_nna (id_nna, id_lengua) VALUES (%s, %s)", (nna_id, id_var))
            
        # 3. Actualizar Tutor
        if id_tutor and data.nombre_tutor:
            partes = data.nombre_tutor.strip().split()
            cursor.execute("""
                UPDATE tutores SET nombre=%s, primer_apellido=%s, segundo_apellido=%s,
                telefono=%s, correo=%s, id_parentesco=%s WHERE id=%s
            """, (partes[0], partes[1] if len(partes)>1 else 'N/A', " ".join(partes[2:]) if len(partes)>2 else '',
                  data.telefono_tutor, data.correo_tutor, data.id_parentesco, id_tutor))
                  
            cursor.execute("DELETE FROM padece_tutor WHERE id_tutor = %s", (id_tutor,))
            for id_enf in data.ids_enfermedades_tutor:
                cursor.execute("INSERT INTO padece_tutor (id_tutor, id_enfermedad) VALUES (%s, %s)", (id_tutor, id_enf))
                
        conexion.commit()
        return {"mensaje": "Expediente actualizado exitosamente"}
    except Exception as e:
        if conexion: conexion.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conexion:
            cursor.close()
            conexion.close()
