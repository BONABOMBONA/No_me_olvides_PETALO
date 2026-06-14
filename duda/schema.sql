-- ============================================================
-- No Me Olvides — Fundación Infantil
-- Schema COMPLETO v2 — Incluye catálogo de discapacidades
-- Basado en FUD CEAVEM y LGDNNA
-- ============================================================

-- ── PERSONAL ─────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS personal (
    id                  SERIAL PRIMARY KEY,
    nombre              VARCHAR(100) NOT NULL,
    primer_apellido     VARCHAR(60)  NOT NULL,
    segundo_apellido    VARCHAR(60),
    rfc                 VARCHAR(13)  UNIQUE,
    curp                VARCHAR(18)  UNIQUE,
    sexo                VARCHAR(20),
    edad                INTEGER,
    direccion           TEXT,
    correo              VARCHAR(120) UNIQUE NOT NULL,
    contrasena          VARCHAR(255) NOT NULL,
    tipo                VARCHAR(20)  CHECK (tipo IN ('empleado', 'voluntario')),
    rol                 VARCHAR(40)  CHECK (rol IN (
                            'director', 'coordinador', 'psicologo',
                            'doctor', 'abogado', 'trabajador_social',
                            'analista', 'equipo_multidisciplinario', 'donante'
                        )),
    estado              VARCHAR(20)  DEFAULT 'pendiente'
                                     CHECK (estado IN ('activo', 'inactivo', 'pendiente', 'restringido')),
    activo              BOOLEAN      DEFAULT FALSE,
    fecha_registro      TIMESTAMP    DEFAULT NOW()
);

-- ── INVITACIONES ─────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS invitaciones (
    id              SERIAL PRIMARY KEY,
    token           VARCHAR(100) UNIQUE NOT NULL,
    creado_por      INTEGER REFERENCES personal(id),
    fecha_creacion  TIMESTAMP DEFAULT NOW(),
    fecha_expira    TIMESTAMP NOT NULL,
    usado           BOOLEAN   DEFAULT FALSE
);

-- ── CATÁLOGO DE DISCAPACIDADES (Petalo) ──────────────────────
CREATE TABLE IF NOT EXISTS catalogo_discapacidades (
    id_discapacidad     SERIAL PRIMARY KEY,
    tipo                VARCHAR(20) NOT NULL CHECK (tipo IN ('Física','Mental','Intelectual','Visual','Auditiva','Múltiple')),
    descripcion         VARCHAR(200) NOT NULL,
    grado_dependencia   VARCHAR(20) NOT NULL CHECK (grado_dependencia IN ('Moderada','Severa','Gran dependencia')),
    es_permanente       BOOLEAN DEFAULT TRUE
);

-- ── NNA ───────────────────────────────────────────────────────
CREATE TABLE IF NOT EXISTS nna (
    id                      SERIAL PRIMARY KEY,

    -- SECCIÓN I: Datos de la víctima (hoja 1 FUD)
    nombre                  VARCHAR(100) NOT NULL,
    primer_apellido         VARCHAR(60)  NOT NULL,
    segundo_apellido        VARCHAR(60),
    fecha_nacimiento        DATE,
    sexo                    VARCHAR(20),
    nacionalidad            VARCHAR(60),
    curp                    VARCHAR(18)  UNIQUE,
    lugar_nac_pais          VARCHAR(60),
    lugar_nac_entidad       VARCHAR(60),
    lugar_nac_municipio     VARCHAR(80),
    lugar_nac_comunidad     VARCHAR(80),
    estado_civil            VARCHAR(30),

    -- DOMICILIO
    calle                   VARCHAR(120),
    numero_exterior         VARCHAR(20),
    numero_interior         VARCHAR(20),
    colonia                 VARCHAR(80),
    codigo_postal           VARCHAR(10),
    localidad               VARCHAR(80),
    delegacion_municipio    VARCHAR(80),
    entidad_federativa      VARCHAR(60),
    telefono                VARCHAR(20),

    -- SECCIÓN II: Tipo de víctima (hoja 2 FUD)
    tipo_victima            VARCHAR(20)  CHECK (tipo_victima IN ('directa', 'indirecta', 'ofendido')),
    nombre_victima_directa  VARCHAR(200),
    relacion_victima        VARCHAR(100),

    -- RELATO DE HECHOS
    lugar_hechos_calle      VARCHAR(120),
    lugar_hechos_colonia    VARCHAR(80),
    lugar_hechos_municipio  VARCHAR(80),
    lugar_hechos_entidad    VARCHAR(60),
    fecha_hechos            DATE,
    relato_hechos           TEXT,

    -- DAÑO (hoja 3 FUD)
    dano_fisico             BOOLEAN DEFAULT FALSE,
    dano_psicologico        BOOLEAN DEFAULT FALSE,
    dano_patrimonial        BOOLEAN DEFAULT FALSE,
    dano_sexual             BOOLEAN DEFAULT FALSE,

    -- INVESTIGACIÓN MINISTERIAL
    denuncio_mp             BOOLEAN DEFAULT FALSE,
    fecha_denuncia_mp       DATE,
    competencia_mp          VARCHAR(20),
    entidad_mp              VARCHAR(60),
    delito_mp               VARCHAR(200),
    agencia_mp              VARCHAR(100),
    numero_averiguacion     VARCHAR(60),
    estado_investigacion    VARCHAR(80),

    -- PROCESO JUDICIAL
    tiene_proceso_judicial  BOOLEAN DEFAULT FALSE,
    fecha_inicio_judicial   DATE,
    competencia_judicial    VARCHAR(20),
    entidad_judicial        VARCHAR(60),
    delito_judicial         VARCHAR(200),
    numero_juzgado          VARCHAR(40),
    numero_proceso          VARCHAR(40),
    estado_proceso          VARCHAR(80),

    -- VULNERABILIDAD (hoja 8 FUD)
    es_menor                BOOLEAN DEFAULT TRUE,

    -- Datos del tutor
    tutor_nombre            VARCHAR(100),
    tutor_primer_apellido   VARCHAR(60),
    tutor_segundo_apellido  VARCHAR(60),
    tutor_parentesco        VARCHAR(80),
    tutor_telefono          VARCHAR(20),
    tutor_correo            VARCHAR(120),

    -- Discapacidad (catálogo Petalo)
    tiene_discapacidad      BOOLEAN DEFAULT FALSE,
    tipo_discapacidad       VARCHAR(20) CHECK (tipo_discapacidad IN ('Física','Mental','Intelectual','Visual','Auditiva','Múltiple')),
    grado_dependencia       VARCHAR(20) CHECK (grado_dependencia IN ('Moderada','Severa','Gran dependencia')),

    -- Idioma / comunidad
    habla_espanol           BOOLEAN DEFAULT TRUE,
    requiere_traductor      BOOLEAN DEFAULT FALSE,
    idioma_lengua           VARCHAR(80),
    pertenece_indigena      BOOLEAN DEFAULT FALSE,
    comunidad_indigena      VARCHAR(100),
    es_migrante             BOOLEAN DEFAULT FALSE,
    pais_origen             VARCHAR(60),

    -- Tipo de violencia contra las mujeres (hoja 8 FUD)
    violencia_psicologica   BOOLEAN DEFAULT FALSE,
    violencia_fisica        BOOLEAN DEFAULT FALSE,
    violencia_economica     BOOLEAN DEFAULT FALSE,
    violencia_patrimonial   BOOLEAN DEFAULT FALSE,
    violencia_sexual        BOOLEAN DEFAULT FALSE,
    violencia_obstetrica    BOOLEAN DEFAULT FALSE,
    violencia_feminicida    BOOLEAN DEFAULT FALSE,

    -- Tipo de violencia (campo general)
    tipo_violencia          VARCHAR(50),

    -- Solicitante
    tipo_solicitante        VARCHAR(40),
    nombre_solicitante      VARCHAR(200),
    parentesco_solicitante  VARCHAR(80),

    -- Control
    estatus                 VARCHAR(20) DEFAULT 'sin_proceso'
                                         CHECK (estatus IN ('sin_proceso','en_proceso','concluido')),
    registrado_por          INTEGER REFERENCES personal(id),
    fecha_ingreso           TIMESTAMP DEFAULT NOW(),
    fecha_inicio_proceso    TIMESTAMP,
    fecha_cierre            TIMESTAMP,
    ultima_actualizacion    TIMESTAMP
);

-- ── RELACIÓN NNA ↔ DISCAPACIDADES ────────────────────────────
CREATE TABLE IF NOT EXISTS nna_discapacidades (
    id              SERIAL PRIMARY KEY,
    id_nna          INTEGER REFERENCES nna(id) ON DELETE CASCADE,
    id_discapacidad INTEGER REFERENCES catalogo_discapacidades(id_discapacidad),
    observaciones   TEXT,
    fecha_registro  TIMESTAMP DEFAULT NOW()
);

-- ── DATOS DEL CATÁLOGO ───────────────────────────────────────
INSERT INTO catalogo_discapacidades (tipo, descripcion, grado_dependencia, es_permanente) VALUES
('Física',      'Limitación para moverse o caminar',            'Moderada',         true),
('Física',      'Limitación para usar brazos o manos',          'Moderada',         true),
('Física',      'Parálisis parcial',                            'Severa',           true),
('Física',      'Parálisis total',                              'Gran dependencia', true),
('Mental',      'Trastorno de ansiedad',                        'Moderada',         false),
('Mental',      'Trastorno depresivo',                          'Moderada',         false),
('Mental',      'Trastorno bipolar',                            'Severa',           false),
('Mental',      'Esquizofrenia',                                'Severa',           true),
('Mental',      'Trastorno por estrés postraumático (TEPT)',    'Moderada',         false),
('Intelectual', 'Discapacidad intelectual leve',                'Moderada',         true),
('Intelectual', 'Discapacidad intelectual moderada',            'Severa',           true),
('Intelectual', 'Discapacidad intelectual severa',              'Gran dependencia', true),
('Intelectual', 'Síndrome de Down',                             'Severa',           true),
('Intelectual', 'Trastorno del Espectro Autista (TEA)',         'Severa',           true),
('Visual',      'Baja visión',                                  'Moderada',         true),
('Visual',      'Ceguera total',                                'Severa',           true),
('Visual',      'Pérdida visual en un ojo',                     'Moderada',         true),
('Auditiva',    'Hipoacusia leve',                              'Moderada',         true),
('Auditiva',    'Hipoacusia severa',                            'Severa',           true),
('Auditiva',    'Sordera total',                                'Gran dependencia', true),
('Auditiva',    'Sordera en un oído',                           'Moderada',         true),
('Múltiple',    'Discapacidad física y visual',                 'Gran dependencia', true),
('Múltiple',    'Discapacidad física e intelectual',            'Gran dependencia', true),
('Múltiple',    'Discapacidad auditiva e intelectual',          'Gran dependencia', true),
('Múltiple',    'Discapacidad física y mental',                 'Gran dependencia', true);

-- ── DATOS DE PRUEBA ──────────────────────────────────────────
INSERT INTO personal (nombre, primer_apellido, rfc, curp, correo, contrasena, rol, estado, activo, tipo) VALUES
('Director', 'Sistema', 'SIST800101ABC', 'SIST800101HDFRRL01', 'director@fundacion.org', '1234', 'director', 'activo', true, 'empleado'),
('Coordinador', 'Sistema', 'COOR800101ABC', 'COOR800101HDFRRL01', 'coordinador@fundacion.org', '1234', 'coordinador', 'activo', true, 'empleado'),
('Psicólogo', 'Sistema', 'PSIC800101ABC', 'PSIC800101HDFRRL01', 'psicologo@fundacion.org', '1234', 'psicologo', 'activo', true, 'empleado'),
('Doctor', 'Sistema', 'DOCT800101ABC', 'DOCT800101HDFRRL01', 'doctor@fundacion.org', '1234', 'doctor', 'activo', true, 'empleado'),
('Donante', 'Sistema', 'DONA800101ABC', 'DONA800101HDFRRL01', 'donante@fundacion.org', '1234', 'donante', 'activo', true, 'voluntario')
ON CONFLICT (correo) DO NOTHING;
