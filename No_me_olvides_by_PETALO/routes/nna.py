from fastapi import APIRouter, HTTPException, Depends
from database import get_connection
from pydantic import BaseModel, Field
from typing import Optional, List
from routes.auth import verificar_token

router = APIRouter()

def _verificar_password(usuario, password):
    if not password:
        raise HTTPException(status_code=400, detail="Debes ingresar tu contraseña")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM personal WHERE id_personal=%s AND contrasena=%s",
                (usuario.get("id"), password))
    ok = cur.fetchone()
    cur.close()
    conn.close()
    if not ok:
        raise HTTPException(status_code=401, detail="Contraseña incorrecta")

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
    primer_apellido_tutor: Optional[str] = None
    segundo_apellido_tutor: Optional[str] = None
    fecha_nacimiento_tutor: Optional[str] = None
    telefono_tutor: Optional[str] = None
    telefono: Optional[str] = None
    correo_tutor: Optional[str] = None
    id_parentesco: Optional[int] = None

    tipo_violencia: Optional[str] = None

    tiene_discapacidad: Optional[bool] = False
    tipo_discapacidad: Optional[str] = None
    grado_dependencia: Optional[str] = None
    origen_discapacidad: Optional[str] = None
    temporalidad: Optional[str] = None
    ayudas_tecnicas: Optional[str] = None
    diagnostico_especifico: Optional[str] = None

    localidad: Optional[str] = None
    lugar_hechos_calle: Optional[str] = None
    lugar_hechos_colonia: Optional[str] = None
    lugar_hechos_municipio: Optional[str] = None
    lugar_hechos_entidad: Optional[str] = None

    tutor_tiene_discapacidad: Optional[bool] = False
    tutor_tipo_discapacidad: Optional[str] = None
    tutor_grado_dependencia: Optional[str] = None
    tutor_origen_discapacidad: Optional[str] = None
    tutor_temporalidad: Optional[str] = None
    tutor_ayudas_tecnicas: Optional[str] = None
    tutor_diagnostico_especifico: Optional[str] = None
    tutor_habla_espanol: Optional[bool] = True
    tutor_requiere_traductor: Optional[bool] = False
    tutor_pertenece_indigena: Optional[bool] = False
    tutor_habla_lengua_indigena: Optional[bool] = False
    tutor_comunidad_indigena: Optional[str] = None
    ids_variantes_lengua_tutor: List[int] = []

    contacto_emergencia_1: Optional[str] = None
    telefono_emergencia_1: Optional[str] = None
    contacto_emergencia_2: Optional[str] = None
    telefono_emergencia_2: Optional[str] = None

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


# ---------- helpers de catálogo (devuelven id o None) ----------
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
            SELECT n.id_nna, n.id_nna AS id, n.nombre, n.primer_apellido, n.segundo_apellido,
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


class CambioEstatus(BaseModel):
    estatus: str
    password: Optional[str] = None

@router.put("/api/nna/{id}/estatus")
def cambiar_estatus(id: int, data: CambioEstatus, usuario=Depends(verificar_token)):
    if data.estatus not in ("en_proceso", "concluido"):
        raise HTTPException(status_code=400, detail="Estatus no válido")
    _verificar_password(usuario, data.password)
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("UPDATE nna SET estatus=%s WHERE id_nna=%s RETURNING id_nna", (data.estatus, id))
    actualizado = cursor.fetchone()
    conexion.commit()
    cursor.close()
    conexion.close()
    if not actualizado:
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    return {"mensaje": "Estatus actualizado", "estatus": data.estatus}


class EliminarNNA(BaseModel):
    password: Optional[str] = None

@router.delete("/api/nna/{id}")
def eliminar_nna(id: int, data: EliminarNNA, usuario=Depends(verificar_token)):
    _verificar_password(usuario, data.password)
    conexion = get_connection()
    cursor = conexion.cursor()
    cursor.execute("SELECT id_nna FROM nna WHERE id_nna=%s", (id,))
    if not cursor.fetchone():
        cursor.close(); conexion.close()
        raise HTTPException(status_code=404, detail="Expediente no encontrado")
    _borrar_relacionados(cursor, id)
    cursor.execute("DELETE FROM nna WHERE id_nna=%s", (id,))
    conexion.commit()
    cursor.close()
    conexion.close()
    return {"mensaje": "Expediente eliminado"}


def _guardar_relacionados(cursor, id_nna, nna):
    if nna.codigo_postal or nna.calle:
        cursor.execute("""
            INSERT INTO domicilio (id_nna, tipo, id_asentamiento, calle, numero_exterior, numero_interior, localidad)
            VALUES (%s,'residencia',%s,%s,%s,%s,%s)
        """, (id_nna, id_asentamiento(cursor, nna.codigo_postal, nna.colonia),
              nna.calle, nna.numero_exterior, nna.numero_interior, nna.localidad))

    if nna.tipo_victima or nna.relato_hechos or nna.fecha_hechos:
        cursor.execute("""
            INSERT INTO hechos_victimizantes (id_nna, id_tipo_victima, nombre_victima_directa,
                                              relacion_victima, fecha_hechos, relato,
                                              lugar_calle, lugar_colonia, lugar_municipio, lugar_entidad)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        """, (id_nna, id_tvic(cursor, nna.tipo_victima), nna.nombre_victima_directa,
              nna.relacion_victima, nna.fecha_hechos or None, nna.relato_hechos,
              nna.lugar_hechos_calle, nna.lugar_hechos_colonia,
              nna.lugar_hechos_municipio, nna.lugar_hechos_entidad))

    danos = {"Físico": nna.dano_fisico, "Psicológico": nna.dano_psicologico,
             "Patrimonial": nna.dano_patrimonial, "Sexual": nna.dano_sexual}
    for nombre_dano, marcado in danos.items():
        if marcado:
            idd = _id(cursor, "SELECT id_tipo_dano FROM cat_tipo_dano WHERE nombre=%s", nombre_dano)
            if idd:
                cursor.execute("INSERT INTO nna_dano (id_nna, id_tipo_dano) VALUES (%s,%s)", (id_nna, idd))

    if nna.denuncio_mp:
        comp = (nna.competencia_mp or "").strip().capitalize()
        if comp not in ("Federal", "Local"):
            comp = None
        cursor.execute("""
            INSERT INTO investigacion_ministerial (id_nna, denuncio_mp, fecha, competencia,
                   id_entidad, agencia_mp, numero_registro, delito, estado_investigacion)
            VALUES (%s,true,%s,%s,%s,%s,%s,%s,%s)
        """, (id_nna, nna.fecha_denuncia_mp or None, comp,
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
                INSERT INTO nna_discapacidad (id_nna, id_tipo_discapacidad, id_grado_dependencia,
                       origen_discapacidad, temporalidad, ayudas_tecnicas, diagnostico_especifico)
                VALUES (%s,%s,%s,%s,%s,%s,%s)
            """, (id_nna, idtd, id_grado(cursor, nna.grado_dependencia),
                  nna.origen_discapacidad, nna.temporalidad, nna.ayudas_tecnicas, nna.diagnostico_especifico))

    for id_var in nna.ids_variantes_lengua:
        cursor.execute("INSERT INTO nna_lengua (id_nna, id_lengua) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                       (id_nna, id_var))

    cursor.execute("""
        INSERT INTO vulnerabilidad (id_nna, tiene_discapacidad, habla_espanol,
               requiere_traductor, es_indigena, comunidad_indigena)
        VALUES (%s,%s,%s,%s,%s,%s)
    """, (id_nna, bool(nna.tiene_discapacidad), bool(nna.habla_espanol),
          bool(nna.requiere_traductor), bool(nna.pertenece_indigena), nna.comunidad_indigena))

    for e in nna.enfermedades_nna:
        cursor.execute("""INSERT INTO nna_enfermedad (id_nna, id_enfermedad, esta_controlada)
                          VALUES (%s,%s,%s) ON CONFLICT DO NOTHING""",
                       (id_nna, e.id_enfermedad, e.esta_controlada))

    if nna.nombre_tutor:
        cursor.execute("""
            INSERT INTO tutor (id_nna, nombre, primer_apellido, segundo_apellido, fecha_nacimiento,
                   tiene_discapacidad, habla_espanol, requiere_traductor, pertenece_indigena,
                   habla_lengua_indigena, comunidad_indigena)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) RETURNING id_tutor
        """, (id_nna, nna.nombre_tutor, nna.primer_apellido_tutor, nna.segundo_apellido_tutor, nna.fecha_nacimiento_tutor or None,
              bool(nna.tutor_tiene_discapacidad),
              bool(nna.tutor_habla_espanol), bool(nna.tutor_requiere_traductor),
              bool(nna.tutor_pertenece_indigena),
              bool(nna.tutor_habla_lengua_indigena), nna.tutor_comunidad_indigena))
        id_tutor = cursor.fetchone()[0]
        if nna.tutor_tiene_discapacidad and nna.tutor_tipo_discapacidad:
            idtd = id_tdisc(cursor, nna.tutor_tipo_discapacidad)
            if idtd:
                cursor.execute("""
                    INSERT INTO tutor_discapacidad (id_tutor, id_tipo_discapacidad, id_grado_dependencia,
                           origen_discapacidad, temporalidad, ayudas_tecnicas, diagnostico_especifico)
                    VALUES (%s,%s,%s,%s,%s,%s,%s)
                """, (id_tutor, idtd, id_grado(cursor, nna.tutor_grado_dependencia),
                      nna.tutor_origen_discapacidad, nna.tutor_temporalidad,
                      nna.tutor_ayudas_tecnicas, nna.tutor_diagnostico_especifico))
        for idl in nna.ids_variantes_lengua_tutor:
            cursor.execute("INSERT INTO tutor_lengua (id_tutor, id_lengua) VALUES (%s,%s) ON CONFLICT DO NOTHING",
                           (id_tutor, idl))
        if nna.telefono_tutor:
            idtc = _id(cursor, "SELECT id_tipo_contacto FROM cat_tipo_contacto WHERE nombre=%s", "Celular")
            cursor.execute("INSERT INTO contacto (id_tutor, id_tipo_contacto, valor) VALUES (%s,%s,%s)",
                           (id_tutor, idtc, nna.telefono_tutor))
        if nna.correo_tutor:
            idtc = _id(cursor, "SELECT id_tipo_contacto FROM cat_tipo_contacto WHERE nombre=%s", "Correo")
            cursor.execute("INSERT INTO contacto (id_tutor, id_tipo_contacto, valor) VALUES (%s,%s,%s)",
                           (id_tutor, idtc, nna.correo_tutor))
        for e in nna.enfermedades_tutor:
            cursor.execute("""INSERT INTO tutor_enfermedad (id_tutor, id_enfermedad, esta_controlada)
                              VALUES (%s,%s,%s) ON CONFLICT DO NOTHING""",
                           (id_tutor, e.id_enfermedad, e.esta_controlada))

    if nna.telefono:
        idtc = _id(cursor, "SELECT id_tipo_contacto FROM cat_tipo_contacto WHERE nombre=%s", "Celular")
        cursor.execute("INSERT INTO contacto (id_nna, id_tipo_contacto, valor) VALUES (%s,%s,%s)",
                       (id_nna, idtc, nna.telefono))

    if nna.contacto_emergencia_1 or nna.telefono_emergencia_1:
        cursor.execute("INSERT INTO contacto_emergencia (id_nna, nombre, telefono) VALUES (%s,%s,%s)",
                       (id_nna, nna.contacto_emergencia_1, nna.telefono_emergencia_1))
    if nna.contacto_emergencia_2 or nna.telefono_emergencia_2:
        cursor.execute("INSERT INTO contacto_emergencia (id_nna, nombre, telefono) VALUES (%s,%s,%s)",
                       (id_nna, nna.contacto_emergencia_2, nna.telefono_emergencia_2))

    if nna.nombre_solicitante or nna.tipo_solicitante:
        ps = (nna.nombre_solicitante or "").strip().split()
        cursor.execute("""
            INSERT INTO solicitante (id_nna, id_tipo_solicitante, nombre, primer_apellido, parentesco)
            VALUES (%s,%s,%s,%s,%s)
        """, (id_nna, id_tsol(cursor, nna.tipo_solicitante),
              ps[0] if ps else None, " ".join(ps[1:]) if len(ps) > 1 else None,
              nna.parentesco_solicitante))


def _borrar_relacionados(cursor, id_nna):
    cursor.execute("DELETE FROM contacto WHERE id_tutor IN (SELECT id_tutor FROM tutor WHERE id_nna=%s)", (id_nna,))
    cursor.execute("DELETE FROM tutor_enfermedad WHERE id_tutor IN (SELECT id_tutor FROM tutor WHERE id_nna=%s)", (id_nna,))
    cursor.execute("DELETE FROM tutor_lengua WHERE id_tutor IN (SELECT id_tutor FROM tutor WHERE id_nna=%s)", (id_nna,))
    cursor.execute("DELETE FROM tutor_discapacidad WHERE id_tutor IN (SELECT id_tutor FROM tutor WHERE id_nna=%s)", (id_nna,))
    cursor.execute("DELETE FROM contacto WHERE id_nna=%s", (id_nna,))
    cursor.execute("DELETE FROM contacto_emergencia WHERE id_nna=%s", (id_nna,))
    for t in ["tutor", "nna_dano", "nna_violencia", "nna_discapacidad", "nna_lengua",
              "nna_enfermedad", "hechos_victimizantes", "investigacion_ministerial",
              "vulnerabilidad", "solicitante", "domicilio"]:
        cursor.execute(f"DELETE FROM {t} WHERE id_nna=%s", (id_nna,))


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
        _guardar_relacionados(cursor, id_nna, nna)
        conexion.commit()
        return {"mensaje": "Expediente guardado exitosamente", "id_nna": id_nna}
    except Exception as e:
        if conexion: conexion.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        if conexion:
            cursor.close()
            conexion.close()


@router.put("/api/nna/{id}")
def editar_nna(id: int, nna: NNA):
    conexion = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()
        cursor.execute("SELECT id_nna FROM nna WHERE id_nna=%s", (id,))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Expediente no encontrado")
        cursor.execute("""
            UPDATE nna SET nombre=%s, primer_apellido=%s, segundo_apellido=%s, fecha_nacimiento=%s,
                   id_sexo=%s, id_nacionalidad=%s, curp=%s, id_estado_civil=%s,
                   lugar_nac_pais=%s, id_entidad_nac=%s, lugar_nac_municipio=%s, lugar_nac_comunidad=%s
            WHERE id_nna=%s
        """, (
            nna.nombre, nna.primer_apellido, nna.segundo_apellido, nna.fecha_nacimiento or None,
            id_sexo(cursor, nna.sexo), id_nac(cursor, nna.nacionalidad),
            nna.curp, id_ecivil(cursor, nna.estado_civil),
            nna.lugar_nac_pais, id_entidad(cursor, nna.lugar_nac_entidad),
            nna.lugar_nac_municipio, nna.lugar_nac_comunidad, id
        ))
        _borrar_relacionados(cursor, id)
        _guardar_relacionados(cursor, id, nna)
        conexion.commit()
        return {"mensaje": "Expediente actualizado exitosamente", "id_nna": id}
    except HTTPException:
        if conexion: conexion.rollback()
        raise
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
        SELECT n.*, n.id_nna AS id, s.nombre AS sexo, na.nombre AS nacionalidad, ec.nombre AS estado_civil
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

    cursor.execute("SELECT id_enfermedad, esta_controlada FROM nna_enfermedad WHERE id_nna=%s", (id,))
    rows_enf = cursor.fetchall()
    data["ids_enfermedades"] = [r[0] for r in rows_enf]
    data["enf_nna_detalle"] = [{"id_enfermedad": r[0], "esta_controlada": r[1]} for r in rows_enf]
    cursor.execute("""SELECT te.id_enfermedad, te.esta_controlada FROM tutor_enfermedad te
                      JOIN tutor t ON te.id_tutor = t.id_tutor WHERE t.id_nna=%s""", (id,))
    rows_enf_t = cursor.fetchall()
    data["ids_enfermedades_tutor"] = [r[0] for r in rows_enf_t]
    data["enf_tutor_detalle"] = [{"id_enfermedad": r[0], "esta_controlada": r[1]} for r in rows_enf_t]

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

    cursor.execute("SELECT nombre, primer_apellido, segundo_apellido, parentesco, fecha_nacimiento, habla_lengua_indigena, comunidad_indigena FROM tutor WHERE id_nna=%s LIMIT 1", (id,))
    t = cursor.fetchone()
    id_tutor_actual = None
    if t:
        data["nombre_tutor"] = t[0]
        data["primer_apellido_tutor"] = t[1]
        data["segundo_apellido_tutor"] = t[2]
        data["fecha_nacimiento_tutor"] = str(t[4]) if t[4] else None
        data["tutor_habla_lengua_indigena"] = t[5]
        data["tutor_comunidad_indigena"] = t[6]
        cursor.execute("SELECT id_tutor FROM tutor WHERE id_nna=%s LIMIT 1", (id,))
        rtut = cursor.fetchone()
        id_tutor_actual = rtut[0] if rtut else None
        if id_tutor_actual:
            cursor.execute("SELECT id_lengua FROM tutor_lengua WHERE id_tutor=%s", (id_tutor_actual,))
            data["ids_variantes_lengua_tutor"] = [r[0] for r in cursor.fetchall()]
        parentescos = ["Madre", "Padre", "Abuelo/a", "Tío/a", "Hermano/a", "Tutor legal", "Otro"]
        data["id_parentesco"] = (parentescos.index(t[3]) + 1) if t[3] in parentescos else None

    cursor.execute("""
        SELECT a.id_asentamiento, a.codigo_postal, d.calle, d.numero_exterior, d.numero_interior,
               a.nombre, m.nombre, e.nombre
        FROM domicilio d
        LEFT JOIN cat_asentamiento a ON d.id_asentamiento = a.id_asentamiento
        LEFT JOIN cat_municipio m ON a.id_municipio = m.id_municipio
        LEFT JOIN cat_entidad e ON m.id_entidad = e.id_entidad
        WHERE d.id_nna=%s AND d.tipo='residencia' LIMIT 1
    """, (id,))
    dom = cursor.fetchone()
    if dom:
        data["id_colonia"] = dom[0]
        data["codigo_postal"] = dom[1]
        data["calle"] = dom[2]
        data["numero_exterior"] = dom[3]
        data["numero_interior"] = dom[4]
        data["colonia_nombre"] = dom[5]
        data["municipio_nombre"] = dom[6]
        data["entidad_nombre"] = dom[7]

    cursor.execute("""
        SELECT tc.nombre, c.valor FROM contacto c
        JOIN cat_tipo_contacto tc ON c.id_tipo_contacto = tc.id_tipo_contacto
        WHERE c.id_nna=%s
    """, (id,))
    for tipo, valor in cursor.fetchall():
        if tipo in ("Celular", "Teléfono fijo"):
            data["telefono"] = valor

    if id_tutor_actual:
        cursor.execute("""
            SELECT tc.nombre, c.valor FROM contacto c
            JOIN cat_tipo_contacto tc ON c.id_tipo_contacto = tc.id_tipo_contacto
            WHERE c.id_tutor=%s
        """, (id_tutor_actual,))
        for tipo, valor in cursor.fetchall():
            if tipo in ("Celular", "Teléfono fijo"):
                data["telefono_tutor"] = valor
            elif tipo == "Correo":
                data["correo_tutor"] = valor

    cursor.execute("""SELECT tv.nombre, h.nombre_victima_directa, h.relacion_victima, h.fecha_hechos, h.relato
                      FROM hechos_victimizantes h
                      LEFT JOIN cat_tipo_victima tv ON h.id_tipo_victima=tv.id_tipo_victima
                      WHERE h.id_nna=%s LIMIT 1""", (id,))
    h = cursor.fetchone()
    if h:
        data["tipo_victima"] = (h[0] or "").lower()
        data["nombre_victima_directa"] = h[1]
        data["relacion_victima"] = h[2]
        data["fecha_hechos"] = h[3]
        data["relato_hechos"] = h[4]

    cursor.execute("""SELECT td.nombre FROM nna_dano nd
                      JOIN cat_tipo_dano td ON nd.id_tipo_dano=td.id_tipo_dano WHERE nd.id_nna=%s""", (id,))
    danos = [r[0] for r in cursor.fetchall()]
    data["dano_fisico"] = "Físico" in danos
    data["dano_psicologico"] = "Psicológico" in danos
    data["dano_patrimonial"] = "Patrimonial" in danos
    data["dano_sexual"] = "Sexual" in danos

    cursor.execute("""SELECT im.denuncio_mp, im.fecha, im.competencia, e.nombre, im.delito,
                             im.agencia_mp, im.numero_registro, im.estado_investigacion
                      FROM investigacion_ministerial im
                      LEFT JOIN cat_entidad e ON im.id_entidad=e.id_entidad
                      WHERE im.id_nna=%s LIMIT 1""", (id,))
    im = cursor.fetchone()
    if im:
        data["denuncio_mp"] = im[0]
        data["fecha_denuncia_mp"] = im[1]
        data["competencia_mp"] = im[2]
        data["entidad_mp"] = im[3]
        data["delito_mp"] = im[4]
        data["agencia_mp"] = im[5]
        data["numero_averiguacion"] = im[6]
        data["estado_investigacion"] = im[7]
    else:
        data["denuncio_mp"] = False

    cursor.execute("""SELECT tvi.nombre FROM nna_violencia nv
                      JOIN cat_tipo_violencia tvi ON nv.id_tipo_violencia=tvi.id_tipo_violencia
                      WHERE nv.id_nna=%s LIMIT 1""", (id,))
    v = cursor.fetchone()
    if v:
        data["tipo_violencia"] = (v[0] or "").lower()

    cursor.execute("""SELECT habla_espanol, requiere_traductor, es_indigena, comunidad_indigena
                      FROM vulnerabilidad WHERE id_nna=%s LIMIT 1""", (id,))
    vu = cursor.fetchone()
    if vu:
        data["habla_espanol"] = vu[0]
        data["requiere_traductor"] = vu[1]
        data["pertenece_indigena"] = vu[2]
        data["comunidad_indigena"] = vu[3]

    cursor.execute("""SELECT ts.nombre, s.nombre, s.primer_apellido, s.parentesco
                      FROM solicitante s
                      LEFT JOIN cat_tipo_solicitante ts ON s.id_tipo_solicitante=ts.id_tipo_solicitante
                      WHERE s.id_nna=%s LIMIT 1""", (id,))
    so = cursor.fetchone()
    if so:
        data["tipo_solicitante"] = so[0]
        data["nombre_solicitante"] = " ".join([x for x in [so[1], so[2]] if x])
        data["parentesco_solicitante"] = so[3]

    if data.get("id_entidad_nac"):
        cursor.execute("SELECT nombre FROM cat_entidad WHERE id_entidad=%s", (data["id_entidad_nac"],))
        ren = cursor.fetchone()
        if ren:
            data["lugar_nac_entidad"] = ren[0]

    cursor.execute("""SELECT origen_discapacidad, temporalidad, ayudas_tecnicas, diagnostico_especifico
                      FROM nna_discapacidad WHERE id_nna=%s LIMIT 1""", (id,))
    de = cursor.fetchone()
    if de:
        data["origen_discapacidad"] = de[0]
        data["temporalidad"] = de[1]
        data["ayudas_tecnicas"] = de[2]
        data["diagnostico_especifico"] = de[3]

    cursor.execute("""SELECT localidad FROM domicilio WHERE id_nna=%s AND tipo='residencia' LIMIT 1""", (id,))
    dl = cursor.fetchone()
    if dl:
        data["localidad"] = dl[0]

    cursor.execute("""SELECT lugar_calle, lugar_colonia, lugar_municipio, lugar_entidad
                      FROM hechos_victimizantes WHERE id_nna=%s LIMIT 1""", (id,))
    lh = cursor.fetchone()
    if lh:
        data["lugar_hechos_calle"] = lh[0]
        data["lugar_hechos_colonia"] = lh[1]
        data["lugar_hechos_municipio"] = lh[2]
        data["lugar_hechos_entidad"] = lh[3]

    cursor.execute("""SELECT tiene_discapacidad, habla_espanol, requiere_traductor, pertenece_indigena
                      FROM tutor WHERE id_nna=%s LIMIT 1""", (id,))
    tt = cursor.fetchone()
    if tt:
        data["tutor_tiene_discapacidad"] = tt[0]
        data["tutor_habla_espanol"] = tt[1]
        data["tutor_requiere_traductor"] = tt[2]
        data["tutor_pertenece_indigena"] = tt[3]
        cursor.execute("""SELECT td.origen_discapacidad, td.temporalidad, td.ayudas_tecnicas,
                                 td.diagnostico_especifico, cd.nombre, cg.nombre
                          FROM tutor_discapacidad td
                          JOIN tutor t ON td.id_tutor = t.id_tutor
                          LEFT JOIN cat_tipo_discapacidad cd ON td.id_tipo_discapacidad = cd.id_tipo_discapacidad
                          LEFT JOIN cat_grado_dependencia cg ON td.id_grado_dependencia = cg.id_grado_dependencia
                          WHERE t.id_nna=%s LIMIT 1""", (id,))
        tdd = cursor.fetchone()
        if tdd:
            data["tutor_origen_discapacidad"] = tdd[0]
            data["tutor_temporalidad"] = tdd[1]
            data["tutor_ayudas_tecnicas"] = tdd[2]
            data["tutor_diagnostico_especifico"] = tdd[3]
            data["tutor_tipo_discapacidad"] = tdd[4]
            data["tutor_grado_dependencia"] = tdd[5]

    cursor.execute("""SELECT nombre, telefono FROM contacto_emergencia WHERE id_nna=%s ORDER BY id_contacto_emergencia""", (id,))
    emergencias = cursor.fetchall()
    if len(emergencias) > 0:
        data["contacto_emergencia_1"] = emergencias[0][0]
        data["telefono_emergencia_1"] = emergencias[0][1]
    if len(emergencias) > 1:
        data["contacto_emergencia_2"] = emergencias[1][0]
        data["telefono_emergencia_2"] = emergencias[1][1]

    cursor.close()
    conexion.close()
    return data


# ---------- catálogos para los formularios ----------
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
    # No es una tabla del modelo; se devuelve una lista fija para los formularios.
    parentescos = ["Madre","Padre","Abuelo/a","Tío/a","Hermano/a","Tutor legal","Otro"]
    return [{"id": i + 1, "nombre": p} for i, p in enumerate(parentescos)]

@router.get("/api/enfermedades")
def obtener_enfermedades():
    conexion = get_connection(); cursor = conexion.cursor()
    cursor.execute("""SELECT id_enfermedad AS id, codigo_cie AS codigo_oms, nombre
                      FROM cat_enfermedad ORDER BY nombre ASC""")
    res = [dict(zip([d[0] for d in cursor.description], f)) for f in cursor.fetchall()]
    cursor.close(); conexion.close()
    return res


@router.get("/api/estadisticas")
def estadisticas():
    conexion = get_connection()
    cursor = conexion.cursor()

    def filas(sql):
        cursor.execute(sql)
        return [{"label": r[0], "value": r[1]} for r in cursor.fetchall()]

    cursor.execute("SELECT count(*) FROM nna")
    total = cursor.fetchone()[0]
    cursor.execute("SELECT estatus, count(*) FROM nna GROUP BY estatus")
    por_estatus = {r[0]: r[1] for r in cursor.fetchall()}

    violencia = filas("""
        SELECT tv.nombre, count(*) FROM nna_violencia nv
        JOIN cat_tipo_violencia tv ON nv.id_tipo_violencia = tv.id_tipo_violencia
        GROUP BY tv.nombre ORDER BY count(*) DESC
    """)
    victima = filas("""
        SELECT tvi.nombre, count(*) FROM hechos_victimizantes h
        JOIN cat_tipo_victima tvi ON h.id_tipo_victima = tvi.id_tipo_victima
        GROUP BY tvi.nombre ORDER BY count(*) DESC
    """)
    danos = filas("""
        SELECT td.nombre, count(*) FROM nna_dano nd
        JOIN cat_tipo_dano td ON nd.id_tipo_dano = td.id_tipo_dano
        GROUP BY td.nombre ORDER BY count(*) DESC
    """)

    cursor.close()
    conexion.close()
    return {
        "total": total,
        "sin_proceso": por_estatus.get("sin_proceso", 0),
        "en_proceso": por_estatus.get("en_proceso", 0),
        "concluido": por_estatus.get("concluido", 0),
        "violencia": violencia,
        "victima": victima,
        "danos": danos,
    }
