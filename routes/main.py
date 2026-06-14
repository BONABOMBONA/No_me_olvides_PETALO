from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import auth, usuarios, nna, invitaciones

app = FastAPI(title="No Me Olvides", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(nna.router)
app.include_router(invitaciones.router)

@app.get("/")
def root():
    return {"mensaje": "Sistema No Me Olvides activo"}
