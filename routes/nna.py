from fastapi import APIRouter, HTTPException
from database import get_connection
from pydantic import BaseModel, Field
from typing import Optional, List

router = APIRouter()

class EnfermedadControlada(BaseModel):
    id_enfermedad: int
    esta_controlada: bool

class NNA(BaseModel):
    nombre: str = Field(..., max_length=100)
    primer_apellido: str = Field(..., max_length=60)
    segundo_apellido: Optional[str] = Field(None, max_length=60)
    fecha_nacimiento: Optional[str] = None
    edad: Optional[int] = Field(None, ge=0, le=99)
    sexo: Optional[str] = None
    nacionalidad: Optional[str] = None
    curp: Optional[str] = None
    estado_civil: Optional[str] = None
    lugar_nac_pais: Optional[str] = None
    lugar_nac_entidad: Optional[str] = None
    lugar_nac_municipio: Optional[str] = None
    lugar_nac_comunidad: Optional[str] = None

    calle: Optional[str] = None
    numero_exterior: Optional[str] = None
    numero_interior: Optional[str] = None
    colonia: Optional[str] = None
    codigo_postal: Optional[str] = None

    tipo_victima: Optional[str] = None
    nombre_victima_directa: Optional[str] = None
    relacion_victima: Optional[str] = None
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

    nombre_tutor: Optional[str] = None
    telefono_tutor: Optional[str] = None
    correo_tutor: Optional[str] = None
    id_parentesco: Optional[int] = None

    tipo_violencia: Optional[str] = None

    tiene_discapacidad: Optional[bool] = False
    tipo_discapacidad: Optional[str] = None
    grado_dependencia: Optional[str] = None

    habla_espanol: Optional[bool] = True
    requiere_traductor: Optional[bool] = False
    idioma_lengua: Optional[str] = None
    pertenece_indigena: Optional[bool] = False
    comunidad_indigena: Optional[str] = None

    tipo_solicitante: Optional[str] = None
    nombre_solicitante: Optional[str] = None
    parentesco_solicitante: Optional[str] = None

    ids_enfermedades: List[int] = []
    ids_enfermedades_tutor: List[int] = []
    enfermedades_nna: List[EnfermedadControlada] = []
    enfermedades_tutor: List[EnfermedadControlada] = []
    ids_variantes_lengua: List[int] = []


def _id(cur, sql, val):
    if val is None or val == "":
        return None
    cur.execute(sql, (val,))
    r = cur.fetchone()
    return r[0] if r else None

def id_sexo(cur, v):        return _id(cur, "SELECT id_sexo FROM cat_sexo WHERE LOWER(nombre)=LOWER(%s)", v)
def id_nac(cur, v):         return _id(cur, "SELECT id_nacionalidad FROM cat_nacionalidad WHERE LOWER(nombre)=LOWER(%s)", v)
def id_ecivil(cur, v):      return _id(cur, "SELECT id_estado_civil FROM cat_estado_civil WHERE LOWER(nombre)=LOWER(%s)", v)
def id_entidad(cur, v):     return _id(cur, "SELECT id_entidad FROM cat_entidad WHERE LOWER(nombre)=LOWER(%s)", v)
def id_tvic(cur, v):        return _id(cur, "SELECT id_tipo_victima FROM cat_tipo_victima WHERE LOWER(nombre)=LOWER(%s)", v)
def id_tdisc(cur, v):       return _id(cur, "SELECT id_tipo_discapacidad FROM cat_tipo_discapacidad WHERE LOWER(nombre)=LOWER(%s)", v)
def id_grado(cur, v):       return _id(cur, "SELECT id_grado_dependencia FROM cat_grado_dependencia WHERE LOWER(nombre)=LOWER(%s)", v)
def id_tviol(cur, v):       return _id(cur, "SELECT id_tipo_violencia FROM cat_tipo_violencia WHERE LOWER(nombre)=LOWER(%s)", v)
def id_tsol(cur, v):
    if not v:
        return None
    cur.execute("SELECT id_tipo_solicitante FROM cat_tipo_solicitante WHERE LOWER(nombre)=LOWER(%s) OR LOWER(clave)=LOWER(%s)", (v, v))
    r = cur.fetchone()
    return r[0] if r else None

def id_asentamiento(cur, cp, colonia):
    if not cp:
        return None
    if colonia:
        cur.execute("SELECT id_asentamiento FROM cat_asentamiento WHERE codigo_postal=%s AND LOWER(nombre)=LOWER(%s) LIMIT 1", (cp, colonia))
        r = cur.fetchone()
        if r:
            return r[0]
    cur.execute("SELECT id_asentamiento FROM cat_asentamiento WHERE codigo_postal=%s LIMIT 1", (cp,))
    r = cur.fetchone()
    return r[0] if r else None


@router.get("/api/nna")
def obtener_nna():
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute("""
            SELECT n.id_nna, n.nombre, n.primer_apellido, n.segundo_apellido,
                   n.curp, n.estatus, s.nombre AS sexo, n.fecha_ingreso
            FROM nna n
            LEFT JOIN cat_sexo s ON n.id_sexo = s.id_sexo
            ORDER BY n.id_nna DESC
        """)
        cols = [d[0] for d in cursor.description]
        expedientes = [dict(zip(cols, fila)) for fila in cursor.fetchall()]
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

        cursor.execute("""
            INSERT INTO nna (nombre, primer_apellido, segundo_apellido, fecha_nacimiento,
                             id_sexo, id_nacionalidad, curp, id_estado_civil,
                             lugar_nac_pais, id_entidad_nac, lugar_nac_municipio, lugar_nac_comunidad)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id_nna
        """, (
            nna.nombre, nna.primer_apellido, nna.segundo_apellido,
            nna.fecha_nacimiento or None,
            id_sexo(cursor, nna.sexo), id_nac(cursor, nna.nacionalidad),
            nna.curp, id_ecivil(cursor, nna.estado_civil),
            nna.lugar_nac_pais, id_entidad(cursor, nna.lugar_nac_entidad),
            nna.lugar_nac_municipio, nna.lugar_nac_comunidad
        ))
        id_nna = cursor.fetchone()[0]

        if nna.codigo_postal or nna.calle:
            cursor.execute("""
                INSERT INTO domicilio (id_nna, tipo, id_asentamiento, calle, numero_exterior, numero_interior)
                VALUES (%s,'residencia',%s,%s,%s,%s)
            """, (id_nna, id_asentamiento(cursor, nna.codigo_postal, nna.colonia),
                  nna.calle, nna.numero_exterior, nna.numero_interior))

        if nna.tipo_victima or nna.relato_hechos or nna.fecha_hechos:
            cursor.execute("""
                INSERT INTO hechos_victimizantes (id_nna, id_tipo_victima, nombre_victima_directa,
                                                  relacion_victima, fecha_hechos, relato)
                VALUES (%s,%s,%s,%s,%s,%s)
            """, (id_nna, id_tvic(cursor, nna.tipo_victima), nna.nombre_victima_directa,
                  nna.relacion_victima, nna.fecha_hechos or None, nna.relato_hechos))

        danos = {"Físico": nna.dano_fisico, "Psicológico": nna.dano_psicologico,
                 "Patrimonial": nna.dano_patrimonial, "Sexual": nna.dano_sexual}
        for nombre_dano, marcado in danos.items():
            if marcado:
                idd = _id(cursor, "SELECT id_tipo_dano FROM cat_tipo_dano WHERE nombre=%s", nombre_dano)
                if idd:
                    cursor.execute("INSERT INTO nna_dano (id_nna, id_tipo_dano) VALUES (%s,%s)", (id_nna, idd))

        if nna.denuncio_mp:
            cursor.execute("""
                INSERT INTO investigacion_ministerial (id_nna, denuncio_mp, fecha, competencia,
                       id_entidad, agencia_mp, numero_registro, delito, estado_investigacion)
                VALUES (%s,true,%s,%s,%s,%s,%s,%s,%s)
            """, (id_nna, nna.fecha_denuncia_mp or None, nna.competencia_mp,
                  id_entidad(cursor, nna.entidad_mp), nna.agencia_mp,
                  nna.numero_averiguacion, nna.delito_mp, nna.estado_investigacion))

        if nna.tipo_violencia:
            idv = id_tviol(cursor, nna.tipo_violencia)
            if idv:
                cursor.execute("INSERT INTO nna_violencia (id_nna, id_tipo_violencia) VALUES (%s,%s)", (id_nna, idv))

        if nna.tiene_discapacidad and nna.tipo_discapacidad:
            idtd = id_tdisc(cursor, nna.tipo_discapacidad)
            if idtd:
                cursor.execute("""
                    INSERT INTO nna_discapacidad (id_nna, id_tipo_discapacidad, id_grado_dependencia)
                    VALUES (%s,%s,%s)
                """, (id_nna, idtd, id_grado(cursor, nna.grado_dependencia)))

        for id_var in nna.ids_variantes_lengua:
            cursor.execute("INSERT INTO nna_lengua (id_nna, id_lengua) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                           (id_nna, id_var))

        cursor.execute("""
            INSERT INTO vulnerabilidad (id_nna, tiene_discapacidad, habla_espanol,
                   requiere_traductor, es_indigena, comunidad_indigena)
            VALUES (%s,%s,%s,%s,%s,%s)
        """, (id_nna, bool(nna.tiene_discapacidad), bool(nna.habla_espanol),
              bool(nna.requiere_traductor), bool(nna.pertenece_indigena), nna.comunidad_indigena))

        if nna.nombre_tutor:
            partes = nna.nombre_tutor.strip().split()
            cursor.execute("""
                INSERT INTO tutor (id_nna, nombre, primer_apellido, segundo_apellido)
                VALUES (%s,%s,%s,%s) RETURNING id_tutor
            """, (id_nna, partes[0] if partes else "N/A",
                  partes[1] if len(partes) > 1 else "",
                  " ".join(partes[2:]) if len(partes) > 2 else ""))
            id_tutor = cursor.fetchone()[0]
            if nna.telefono_tutor:
                idtc = _id(cursor, "SELECT id_tipo_contacto FROM cat_tipo_contacto WHERE nombre=%s", "Celular")
                cursor.execute("INSERT INTO contacto (id_tutor, id_tipo_contacto, valor) VALUES (%s,%s,%s)",
                               (id_tutor, idtc, nna.telefono_tutor))
            if nna.correo_tutor:
                idtc = _id(cursor, "SELECT id_tipo_contacto FROM cat_tipo_contacto WHERE nombre=%s", "Correo")
                cursor.execute("INSERT INTO contacto (id_tutor, id_tipo_contacto, valor) VALUES (%s,%s,%s)",
                               (id_tutor, idtc, nna.correo_tutor))

        if nna.nombre_solicitante or nna.tipo_solicitante:
            ps = (nna.nombre_solicitante or "").strip().split()
            cursor.execute("""
                INSERT INTO solicitante (id_nna, id_tipo_solicitante, nombre, primer_apellido, parentesco)
                VALUES (%s,%s,%s,%s,%s)
            """, (id_nna, id_tsol(cursor, nna.tipo_solicitante),
                  ps[0] if ps else None, " ".join(ps[1:]) if len(ps) > 1 else None,
                  nna.parentesco_solicitante))

        conexion.commit()
        return {"mensaje": "Expediente guardado exitosamente", "id_nna": id_nna}
    except Exception as e:
        if conexion: conexion.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conexion:
            cursor.close()
            conexion.close()


@router.get("/api/nna/{id}")
def ver_nna(id: int):
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("""
        SELECT n.*, s.nombre AS sexo, na.nombre AS nacionalidad, ec.nombre AS estado_civil
        FROM nna n
        LEFT JOIN cat_sexo s ON n.id_sexo=s.id_sexo
        LEFT JOIN cat_nacionalidad na ON n.id_nacionalidad=na.id_nacionalidad
        LEFT JOIN cat_estado_civil ec ON n.id_estado_civil=ec.id_estado_civil
        WHERE n.id_nna = %s
    """, (id,))
    row = cursor.fetchone()
    if not row:
        cursor.close(); conexion.close()
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    data = dict(zip([d[0] for d in cursor.description], row))

    cursor.execute("SELECT id_lengua FROM nna_lengua WHERE id_nna=%s", (id,))
    data["ids_variantes_lengua"] = [r[0] for r in cursor.fetchall()]

    cursor.execute("""SELECT td.nombre, gd.nombre FROM nna_discapacidad nd
                      LEFT JOIN cat_tipo_discapacidad td ON nd.id_tipo_discapacidad=td.id_tipo_discapacidad
                      LEFT JOIN cat_grado_dependencia gd ON nd.id_grado_dependencia=gd.id_grado_dependencia
                      WHERE nd.id_nna=%s LIMIT 1""", (id,))
    disc = cursor.fetchone()
    if disc:
        data["tiene_discapacidad"] = True
        data["tipo_discapacidad"] = disc[0]
        data["grado_dependencia"] = disc[1]
    else:
        data["tiene_discapacidad"] = False

    cursor.execute("SELECT nombre, primer_apellido, segundo_apellido FROM tutor WHERE id_nna=%s LIMIT 1", (id,))
    t = cursor.fetchone()
    if t:
        data["nombre_tutor"] = " ".join([x for x in t if x])

    cursor.close()
    conexion.close()
    return data



@router.get("/api/lenguas")
def obtener_lenguas():
    conexion = get_connection(); cursor = conexion.cursor()
    cursor.execute("""SELECT id_lengua AS id,
                      agrupacion || COALESCE(' - ' || variante, '') AS nombre
                      FROM cat_lengua ORDER BY agrupacion ASC""")
    res = [dict(zip([d[0] for d in cursor.description], f)) for f in cursor.fetchall()]
    cursor.close(); conexion.close()
    return res

@router.get("/api/sepomex/{cp}")
def buscar_cp(cp: str):
    conexion = get_connection(); cursor = conexion.cursor()
    cursor.execute("""
        SELECT a.id_asentamiento AS id, a.nombre AS colonia, m.nombre AS municipio, e.nombre AS entidad
        FROM cat_asentamiento a
        JOIN cat_municipio m ON a.id_municipio=m.id_municipio
        JOIN cat_entidad e ON m.id_entidad=e.id_entidad
        WHERE a.codigo_postal = %s
    """, (cp,))
    res = [dict(zip([d[0] for d in cursor.description], f)) for f in cursor.fetchall()]
    cursor.close(); conexion.close()
    if not res:
        raise HTTPException(status_code=404, detail="Código Postal no encontrado en SEPOMEX")
    return {
        "entidad": res[0]["entidad"],
        "municipio": res[0]["municipio"],
        "colonias": [{"id": r["id"], "nombre": r["colonia"]} for r in res]
    }

@router.get("/api/discapacidades")
def obtener_catalogo_discapacidades():
    conexion = get_connection(); cursor = conexion.cursor()
    cursor.execute("SELECT id_tipo_discapacidad AS id_discapacidad, nombre AS tipo, descripcion FROM cat_tipo_discapacidad")
    res = [dict(zip([d[0] for d in cursor.description], f)) for f in cursor.fetchall()]
    cursor.close(); conexion.close()
    return res

@router.get("/api/parentescos")
def obtener_parentescos():
    parentescos = ["Madre","Padre","Abuelo/a","Tío/a","Hermano/a","Tutor legal","Otro"]
    return [{"id": i + 1, "nombre": p} for i, p in enumerate(parentescos)]

@router.get("/api/enfermedades")
def obtener_enfermedades():
    return []