# Sistema NO ME OLVIDES
Proyecto de la Agencia - Equipo Pétalo 

## Integrantes: 

García Hernández Edgar Alessandro

Soria López Dana Paola

Velázquez Rivero Lesly

## Descripción general

Sistema para el registro y seguimiento de expedientes de Niñas, Niños y Adolescentes (NNA) dentro de una fundación multidisciplinaria. Centraliza los datos demográficos, clínicos, sociales y legales de cada beneficiario y de su tutor o red de apoyo, para que el equipo de la fundación no tenga que ir armando la información a mano entre distintos formatos.

## Características principales

- **Expedientes de NNA:** alta, baja y edición (CRUD) con datos básicos, domicilio, antecedentes de los hechos, situación legal y red de apoyo.
- **Catálogos oficiales integrados:** SEPOMEX, CIE-11 e INALI (ver detalle más abajo).
- **Backend modular:** las rutas están separadas por dominio (`auth`, `usuarios`, `nna`, `invitaciones`) en vez de tener todo amontonado en un solo archivo.

## Stack tecnológico

- Backend: Python con FastAPI
- Base de datos: PostgreSQL
- Frontend: HTML5, CSS3 y JavaScript (sin frameworks), con diseño responsivo
- Validación de datos: Pydantic

## Catálogos y normativas

El módulo de registro de NNA se apoya en catálogos oficiales para no improvisar la captura de datos sensibles:

**Domicilios (SEPOMEX)** — autocompletado y validación de direcciones a partir del código postal, para no depender de que cada persona escriba bien el estado/municipio/colonia. Tablas: `catalogo_sepomex`, `estados`, `municipios`, `colonias`, `domicilios`.

**Enfermedades (CIE-11, OMS)** — diagnósticos estandarizados tanto para el NNA como para el tutor, incluyendo el estatus del padecimiento (controlada / no controlada). Tablas: `catalogo_enfermedades`, `enfermedades`, `padece_nna`, `padece_tutor`.

**Lenguas indígenas (INALI)** — catálogo de variantes lingüísticas organizado por familia, lengua y variante, para poder atender al NNA en su lengua materna cuando aplica. Tablas: `catalogo_lenguas`, `familias_linguisticas`, `lenguas`, `variantes`, `habla_nna`.

**Discapacidades** — tipo de discapacidad y grado de dependencia, usado para definir los ajustes razonables de cada caso (`catalogo_discapacidades`, `nna_discapacidades`).

**Parentescos** — vínculos legales o consanguíneos entre el NNA y su tutor o adulto responsable (`parentescos`).

**Instituciones y apoyos** — directorio de servicios internos y externos (psicología, área legal, etc.) para la ruta de canalización (`instituciones`, `tipos_apoyo`).

Aparte de estos, hay dos referencias que no tienen tabla propia pero sí definieron cómo se armaron los campos del expediente:

- **FUD (Formato Único de Declaración):** de aquí salen varios de los campos estandarizados del registro.
- **LGDNNA (Ley General de los Derechos de Niñas, Niños y Adolescentes):** de aquí se tomaron las variables de vulnerabilidad que se registran en el sistema.

Y las tablas operativas que no son catálogo: `nna`, `tutores`, `personal`, `invitaciones`.

## Estructura del proyecto

- `/routes` — endpoints divididos por dominio (`nna.py`, `auth.py`, etc.)
- `main.py` — punto de entrada de la API y configuración del middleware CORS
- `database.py` — conexión a PostgreSQL
- `schema.sql` — estructura de las tablas (catálogos + tablas operativas)
- `importar_lenguas.py` — carga del catálogo de INALI

## Requisitos previos

- Python 3.9+
- PostgreSQL 13+
- `pip` para instalar dependencias (`fastapi`, `psycopg2`, `python-dotenv`, `python-jose`)

## Instalación y configuración

### 1. Clonar el repositorio

```bash
git clone <URL_DEL_REPOSITORIO>
cd 3etapa
```

### 2. Variables de entorno

Crea un `.env` en la raíz del proyecto:

```env
DB_HOST=localhost
DB_NAME=fundacion_db
DB_USER=usuario
DB_PASS=contraseña
JWT_SECRET=tu_clave_secreta
```

### 3. Crear la base de datos

```bash
sudo -u postgres psql
```

```sql
CREATE DATABASE fundacion_db;
\c fundacion_db
\i schema.sql
```

Con esto quedan las 23 tablas: las operativas (`nna`, `tutores`, `personal`, `invitaciones`) y los 6 catálogos con sus tablas relacionadas.

### 4. Cargar los catálogos

```bash
python importar_lenguas.py
```

### 5. Levantar el servidor

```bash
uvicorn main:app --reload
```

## Notas

El frontend limpia los campos de texto antes de enviarlos a la API, como primera barrera contra XSS. Para enfermedades, la relación entre el padecimiento y el NNA o el tutor se maneja con dos tablas intermedias (`padece_nna`, `padece_tutor`), así no se pierde la integridad referencial aunque el catálogo siga creciendo.
