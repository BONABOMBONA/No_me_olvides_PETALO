from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_connection
from routes.auth import verificar_token, solo_director

router = APIRouter()

class Usuario(BaseModel):
    nombre: str
    primer_apellido: str
    segundo_apellido: Optional[str] = None
    rfc: Optional[str] = None
    curp: Optional[str] = None
    sexo: Optional[str] = None
    correo: str
    contrasena: str
    tipo: Optional[str] = None
    rol: Optional[str] = None
    estado: Optional[str] = "pendiente"

class ActualizarUsuario(BaseModel):
    nombre: Optional[str] = None
    primer_apellido: Optional[str] = None
    segundo_apellido: Optional[str] = None
    rfc: Optional[str] = None
    curp: Optional[str] = None
    tipo: Optional[str] = None
    rol: Optional[str] = None

class CambiarRol(BaseModel):
    rol: str
    estado: str

def id_sexo_por_nombre(cur, sexo):
    if not sexo:
        return None
    cur.execute("SELECT id_sexo FROM cat_sexo WHERE LOWER(nombre)=LOWER(%s)", (sexo,))
    r = cur.fetchone()
    return r[0] if r else None

@router.get("/api/usuarios")
def listar_usuarios(usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_personal, nombre, primer_apellido, segundo_apellido,
               rfc, correo, rol, estado, tipo, fecha_registro
        FROM personal
        ORDER BY fecha_registro DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    cols = ["id","nombre","primer_apellido","segundo_apellido",
            "rfc","correo","rol","estado","tipo","fecha_registro"]
    return [dict(zip(cols, r)) for r in rows]


@router.get("/api/usuarios/pendientes")
def listar_pendientes(usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id_personal, nombre, primer_apellido, correo, fecha_registro
        FROM personal
        WHERE estado = 'pendiente'
        ORDER BY fecha_registro DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    cols = ["id","nombre","primer_apellido","correo","fecha_registro"]
    return [dict(zip(cols, r)) for r in rows]


@router.get("/api/usuarios/{id}")
def ver_usuario(id: int, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT * FROM personal WHERE id_personal = %s", (id,))
    row = cur.fetchone()
    cols = [desc[0] for desc in cur.description] if cur.description else []
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return dict(zip(cols, row))


@router.post("/api/usuarios")
def crear_usuario(data: Usuario, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO personal
                (nombre, primer_apellido, segundo_apellido, rfc, curp,
                 id_sexo, correo, contrasena, tipo, rol, estado, activo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id_personal
        """, (
            data.nombre, data.primer_apellido, data.segundo_apellido,
            data.rfc, data.curp, id_sexo_por_nombre(cur, data.sexo),
            data.correo, data.contrasena, data.tipo, data.rol,
            data.estado, True if data.estado == "activo" else False
        ))
        nuevo_id = cur.fetchone()[0]
        conn.commit()
        return {"mensaje": "Usuario creado", "id": nuevo_id}
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.put("/api/usuarios/{id}")
def editar_usuario(id: int, data: ActualizarUsuario, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    campos = {k: v for k, v in data.dict().items() if v is not None}
    if not campos:
        raise HTTPException(status_code=400, detail="No hay campos para actualizar")
    sets = ", ".join([f"{k} = %s" for k in campos])
    valores = list(campos.values()) + [id]
    cur.execute(f"UPDATE personal SET {sets} WHERE id_personal = %s", valores)
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Usuario actualizado"}


@router.put("/api/usuarios/{id}/rol")
def cambiar_rol(id: int, data: CambiarRol, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE personal
        SET rol = %s, estado = %s, activo = %s
        WHERE id_personal = %s
    """, (data.rol, data.estado, True if data.estado == "activo" else False, id))
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": f"Rol actualizado a {data.rol}"}


@router.put("/api/usuarios/{id}/restringir")
def restringir_usuario(id: int, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE personal SET estado = 'restringido', activo = false WHERE id_personal = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Acceso revocado"}


@router.delete("/api/usuarios/{id}")
def eliminar_usuario(id: int, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM personal WHERE id_personal = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Usuario eliminado"}


@router.put("/api/usuarios/{id}/activar")
def activar_usuario(id: int, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("UPDATE personal SET estado = 'activo', activo = true WHERE id_personal = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Usuario activado correctamente"}

class RecuperarPassword(BaseModel):
    password: Optional[str] = None

@router.post("/api/usuarios/{id}/recuperar-password")
def recuperar_password(id: int, data: RecuperarPassword, usuario=Depends(verificar_token)):
    if usuario.get("rol") != "director":
        raise HTTPException(status_code=403, detail="Solo el director puede recuperar contraseñas")
    if not data.password:
        raise HTTPException(status_code=400, detail="Debes ingresar tu contraseña de director")
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM personal WHERE id_personal=%s AND contrasena=%s", (usuario.get("id"), data.password))
    if not cur.fetchone():
        cur.close(); conn.close()
        raise HTTPException(status_code=401, detail="Tu contraseña de director es incorrecta")
    cur.execute("SELECT nombre, primer_apellido, contrasena FROM personal WHERE id_personal=%s", (id,))
    fila = cur.fetchone()
    cur.close()
    conn.close()
    if not fila:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return {"nombre": f"{fila[0]} {fila[1] or ''}".strip(), "contrasena": fila[2]}
