from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from database import get_connection
from routes.auth import solo_director
import secrets
import os
from datetime import datetime, timedelta

router = APIRouter()

HORAS = int(os.getenv("LINK_EXPIRA_HORAS", 48))

# ── Modelo ───────────────────────────────────────────────────
class NuevoUsuario(BaseModel):
    token: str
    nombre: str
    primer_apellido: str
    segundo_apellido: str = None
    rfc: str = None
    curp: str = None
    correo: str
    contrasena: str

# ── Rutas ────────────────────────────────────────────────────

@router.post("/api/invitaciones/generar")
def generar_link(director=Depends(solo_director)):
    token = secrets.token_urlsafe(32)
    expira = datetime.now() + timedelta(hours=HORAS)
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO invitaciones (token, creado_por, fecha_expira)
        VALUES (%s, %s, %s)
    """, (token, director.get("id"), expira))
    conn.commit()
    cur.close()
    conn.close()
    return {
        "token": token,
        "link": f"http://localhost:5173/pages/registro-publico.html?token={token}",
        "expira": str(expira)
    }


@router.get("/api/invitaciones/validar/{token}")
def validar_token(token: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT id, fecha_expira, usado
        FROM invitaciones
        WHERE token = %s
    """, (token,))
    inv = cur.fetchone()
    cur.close()
    conn.close()

    if not inv:
        raise HTTPException(status_code=404, detail="Link no válido")
    if inv[2]:
        raise HTTPException(status_code=400, detail="Este link ya fue usado")
    if datetime.now() > inv[1]:
        raise HTTPException(status_code=400, detail="Este link ha expirado")

    return {"valido": True}


@router.post("/api/registro")
def registrar_con_token(data: NuevoUsuario):
    conn = get_connection()
    cur = conn.cursor()

    # Validar token
    cur.execute("""
        SELECT id, fecha_expira, usado FROM invitaciones WHERE token = %s
    """, (data.token,))
    inv = cur.fetchone()

    if not inv:
        raise HTTPException(status_code=404, detail="Link no válido")
    if inv[2]:
        raise HTTPException(status_code=400, detail="Este link ya fue usado")
    if datetime.now() > inv[1]:
        raise HTTPException(status_code=400, detail="Este link ha expirado")

    # Crear usuario con estado pendiente
    try:
        cur.execute("""
            INSERT INTO personal
                (nombre, primer_apellido, segundo_apellido, rfc, curp,
                 correo, contrasena, estado, activo)
            VALUES (%s, %s, %s, %s, %s, %s, %s, 'pendiente', false)
            RETURNING id
        """, (
            data.nombre, data.primer_apellido, data.segundo_apellido,
            data.rfc, data.curp, data.correo, data.contrasena
        ))
        nuevo_id = cur.fetchone()[0]

        # Marcar token como usado
        cur.execute("UPDATE invitaciones SET usado = true WHERE token = %s", (data.token,))
        conn.commit()

        return {
            "mensaje": "Cuenta creada exitosamente. Acuda a las oficinas para verificar su rol.",
            "id": nuevo_id
        }
    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=400, detail=str(e))
    finally:
        cur.close()
        conn.close()


@router.get("/api/invitaciones")
def listar_invitaciones(director=Depends(solo_director)):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("""
        SELECT i.id, i.token, i.fecha_creacion, i.fecha_expira, i.usado,
               p.nombre as creado_por
        FROM invitaciones i
        LEFT JOIN personal p ON i.creado_por = p.id
        ORDER BY i.fecha_creacion DESC
    """)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    cols = ["id","token","fecha_creacion","fecha_expira","usado","creado_por"]
    return [dict(zip(cols, r)) for r in rows]
