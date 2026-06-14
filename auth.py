from fastapi import APIRouter, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from database import get_connection
from jose import jwt, JWTError
import os

router = APIRouter()
security = HTTPBearer()

SECRET = os.getenv("JWT_SECRET", "nommeolvides2026")

# ── Modelos ──────────────────────────────────────────────────
class LoginData(BaseModel):
    correo: str
    contrasena: str

# ── Helpers ──────────────────────────────────────────────────
def crear_token(datos: dict):
    return jwt.encode(datos, SECRET, algorithm="HS256")

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        payload = jwt.decode(credentials.credentials, SECRET, algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

def solo_director(usuario=Depends(verificar_token)):
    if usuario.get("rol") not in ["director", "coordinador"]:
        raise HTTPException(status_code=403, detail="No tienes permiso")
    return usuario

# ── Rutas ────────────────────────────────────────────────────
@router.post("/api/login")
def login(data: LoginData):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        "SELECT id, nombre, rol, estado FROM personal WHERE correo = %s AND contrasena = %s",
        (data.correo, data.contrasena)
    )
    usuario = cur.fetchone()
    cur.close()
    conn.close()

    if not usuario:
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos")

    id, nombre, rol, estado = usuario

    if estado != "activo":
        raise HTTPException(status_code=403, detail="Tu cuenta aún no está activa. Acude a las oficinas.")

    token = crear_token({"id": id, "nombre": nombre, "rol": rol})
    return {"token": token, "nombre": nombre, "rol": rol}
