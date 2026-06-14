from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional
from database import get_connection
from routes.auth import verificar_token, solo_director

router = APIRouter()

# ── Modelos ──────────────────────────────────────────────────
class Usuario(BaseModel):
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
    tipo: Optional[str] = None
    rol: Optional[str] = None
    estado: Optional[str] = "pendiente"

class ActualizarUsuario(BaseModel):
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
    rol: str
    estado: str

# ── Rutas ────────────────────────────────────────────────────

@router.get("/api/usuarios")
def listar_usuarios(usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, nombre, primer_apellido, segundo_apellido,
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
        SELECT id, nombre, primer_apellido, correo, fecha_registro
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
    cur.execute("SELECT * FROM personal WHERE id = %s", (id,))
    row = cur.fetchone()
    cur.close()
    conn.close()
    if not row:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    cols = [desc[0] for desc in cur.description] if cur.description else []
    return dict(zip(cols, row))


@router.post("/api/usuarios")
def crear_usuario(data: Usuario, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    try:
        cur.execute("""
            INSERT INTO personal
                (nombre, primer_apellido, segundo_apellido, rfc, curp,
                 sexo, edad, direccion, correo, contrasena, tipo, rol, estado, activo)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
            RETURNING id
        """, (
            data.nombre, data.primer_apellido, data.segundo_apellido,
            data.rfc, data.curp, data.sexo, data.edad, data.direccion,
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
    cur.execute(f"UPDATE personal SET {sets} WHERE id = %s", valores)
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
        WHERE id = %s
    """, (data.rol, data.estado, True if data.estado == "activo" else False, id))
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": f"Rol actualizado a {data.rol}"}


@router.put("/api/usuarios/{id}/restringir")
def restringir_usuario(id: int, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        UPDATE personal SET estado = 'restringido', activo = false WHERE id = %s
    """, (id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Acceso revocado"}


@router.delete("/api/usuarios/{id}")
def eliminar_usuario(id: int, usuario=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("DELETE FROM personal WHERE id = %s", (id,))
    conn.commit()
    cur.close()
    conn.close()
    return {"mensaje": "Usuario eliminado"}
