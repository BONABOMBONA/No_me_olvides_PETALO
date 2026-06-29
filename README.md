<div align="center">

<img src="img/no_me_olvides.png" alt="No Me Olvides" width="120"/>

# 🌸 No Me Olvides

### Sistema de Gestión de Expedientes Fundación Infantil

*Manteniendo viva la memoria y el futuro de cada niña, niño y adolecente*

Desarrollado por **Pétalo** · Bases de Datos · ESCOM-IPN · 2026

</div>

---

## Sobre Pétalo

**Pétalo** es la agencia de consultoría en datos responsable de este proyecto.

**Misión**
En Pétalo convertimos información dispersa en sistemas de datos confiables y fáciles de usar. Nos comprometemos con la integridad, privacidad y disponibilidad de cada registro, ayudando a las organizaciones —especialmente a las de impacto social— a gestionar su información con seguridad y eficiencia.

**Visión**
Ser el aliado de confianza en gestión de datos para organizaciones que generan impacto social, destacando por nuestra excelencia técnica y un compromiso firme con la seguridad y la protección de la información sensible.

**Servicios:** diseño de bases de datos · análisis de datos · estrategia tecnológica · migración de información.

**Equipo**

| Integrante | Rol |
|---|---|
| Edgar Alessandro García Hernández | Backend y base de datos |
| Dana Paola Soria López | Frontend y base de datos |
| Lesly Velázquez Rivero | Catálogos y base de datos|

---

## PETALO

El nombre nace de la flor *No me olvides* (Myosotis), que representa el amor eterno y la memoria fiel. En el contexto de la fundación, conecta con el recuerdo de la madre ausente y el compromiso de no olvidar ni abandonar a los niños que quedaron atrás: el sistema asegura que cada historia y cada necesidad queden registradas.

### Problemática
Actualmente los registros de la fundación están en papel o digitalizados sin estructura, y sin un buscador eficiente. Esto genera retrasos críticos que afectan directamente la atención a los beneficiarios.

### Objetivo
Centralizar y resguardar la información de los niños, niñas y adolescentes atendidos por la fundación en una base de datos segura y bien estructurada, que reemplace los registros en papel, reduzca los tiempos de búsqueda y asegure que la atención llegue a tiempo a cada beneficiario.

---

## Funcionalidades

- **Gestión de expedientes (CRUD):** alta, consulta, actualización y baja de los NNA atendidos, con validación de datos.
- **Control de estatus por beneficiario:** cada caso transita por `Sin proceso` → `En proceso` → `Concluido`, con registro de fechas para medir tiempos de respuesta.
- **Búsqueda inteligente multicriterio:** localización por apellidos, tipo de proceso o estatus, con despliegue inmediato del expediente completo.
- **Roles y control de acceso:** distintas vistas y permisos según el tipo de usuario (dirección, equipo multidisciplinario, donante).
- **Registro por invitación:** alta de personal mediante token con expiración.

---

## Beneficios

- **Eficiencia operativa:** reducción drástica en los tiempos de búsqueda y recuperación de expedientes.
- **Gestión integral:** altas, bajas y modificaciones con validación de datos.
- **Minimización de retrasos:** elimina la incertidumbre de los archivos físicos para que la ayuda llegue a tiempo.
- **Integridad de datos:** información resguardada contra pérdidas físicas o deterioro.

---

## Tecnologías

| Capa | Tecnología |
|---|---|
| Base de datos | PostgreSQL |
| Lenguaje de consultas | SQL |
| Backend / acceso a datos | Python · FastAPI |
| Frontend | HTML · CSS · JavaScript (vanilla) |
| Autenticación | JWT |
| Administración de BD | pgAdmin |
| Migración de datos | Archivos CSV |

---

## 🗂️ Estructura del repositorio

```
No_me_olvides_PETALO/
├── Database/                  Base de datos
│   ├── schema.sql             Modelo físico normalizado a 3FN (35 tablas)
│   ├── *.csv                  Catálogos (lenguas INALI, SEPOMEX, etc.)
│   └── docs/                  Diccionario de datos, normalización y diagrama
├── Frontend/                  Pantallas HTML/CSS/JS
├── routes/                    Endpoints de la API (FastAPI)
├── main.py                    Punto de entrada del backend
├── database.py                Conexión a PostgreSQL
├── importar_*.py              Scripts de carga de catálogos
└── img/                       Recursos gráficos
```

---

## Base de datos

El modelo está normalizado hasta la **Tercera Forma Normal (3FN)** y consta de **35 tablas** (catálogos, expediente y tablas de asociación), derivadas del Formato Único de Declaración (FUD) de la CEAVEM y de los catálogos del proyecto (lenguas INALI, discapacidad, SEPOMEX).

La documentación completa está en `Database/docs/`:
- **Diccionario de datos** — cada tabla con sus atributos, tipos, claves y descripción.
- **Proceso de normalización** — descomposición 1FN → 2FN → 3FN tabla por tabla.
- **Diagrama relacional** — modelo final con todas las relaciones.

---

## Requisitos previos

- Python 3.12+
- PostgreSQL 16+
- Git

---

## Instalación (primera vez)

Estos pasos solo se hacen **una vez**, al instalar el proyecto en una máquina nueva.

### 1. Crear el usuario y la base de datos en PostgreSQL

```bash
sudo -u postgres psql -c "CREATE USER petalo WITH PASSWORD '1234';"
sudo -u postgres psql -c "CREATE DATABASE no_me_olvides OWNER petalo;"
```

### 2. Clonar el repositorio

```bash
git clone https://github.com/BONABOMBONA/No_me_olvides_PETALO.git
cd No_me_olvides_PETALO
```

### 3. Cargar el esquema de la base de datos

```bash
psql -U petalo -d no_me_olvides -f Database/schema.sql
```

Esto crea las 35 tablas y carga los catálogos de lenguas (INALI) y discapacidad.

### 4. Crear el archivo de variables de entorno

```bash
cp env.example .env
nano .env
```

Llena el archivo con tus datos y guárdalo (en `nano`: `Ctrl+O`, Enter, `Ctrl+X`):

```
DB_HOST=localhost
DB_NAME=no_me_olvides
DB_USER=petalo
DB_PASS=1234
JWT_SECRET=una_clave_secreta
LINK_EXPIRA_HORAS=48
```

### 5. Crear el entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r Database/requirements.txt
```

### 6. Cargar el catálogo SEPOMEX (códigos postales)

```bash
python3 importar_sepomex.py
```

Esto importa las 32 entidades, 2,478 municipios y 158,480 asentamientos a la base de datos.

---

## ¿Cómo correr el programa?

El sistema tiene dos partes que deben estar corriendo **al mismo tiempo**: el backend (la API) y el frontend (las pantallas). Se necesitan dos terminales abiertas.

### 1. Abre una terminal y levanta el backend

```bash
source venv/bin/activate
uvicorn main:app --reload --port 4000
```

La API queda corriendo en `http://127.0.0.1:4000`. **Deja esta terminal abierta** (si la cierras, se apaga el sistema).

### 2. Abre otra terminal y levanta el frontend

```bash
cd Frontend
python3 -m http.server 5500
```

### 3. Abre el navegador

Entra a `http://localhost:5500` y se mostrará la pantalla de inicio de sesión.

> El frontend se sirve con `http.server` (no se abre el `index.html` con doble clic), para que el navegador permita la conexión con la API.

---

## Costos

| Concepto | Detalle | Monto |
|---|---|---|
| Desarrollo | 1,320 h (3 personas × 4 meses) × $120/h | $158,400 |
| Gastos operativos | Internet, electricidad y reuniones (4 meses) | $4,000 |
| Software y licencias | Herramientas open source | $0 |
| **Total** | | **$162,400 MXN** |

---

## Plan de trabajo

| Fase | Etapa | Descripción |
|---|---|---|
| 1 | Diagnóstico | Análisis de requerimientos y de la información existente |
| 2 | Desarrollo | Diseño de la base de datos e implementación del sistema |
| 3 | Validación | Revisión del modelo y pruebas con el equipo |
| 4 | Pruebas y entrega | Pruebas finales, ajustes y entrega del sistema |

Duración total: **4 meses**.

---

## Contacto

**Pétalo** · agpetalo@gmail.com · +52 55 1234 5678
Av. Innovación Social 404, Torre 2, CDMX

---

<div align="center">
<i>Proyecto académico · Bases de Datos · ESCOM — Instituto Politécnico Nacional · 2026</i>
</div>
