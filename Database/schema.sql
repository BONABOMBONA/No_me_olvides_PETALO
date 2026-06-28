-- ============================================================================
--  Proyecto: No Me Olvides  ·  Equipo Pétalo
--  Sistema de gestión de expedientes de NNA víctimas de feminicidio/orfandad
--  Base de Datos · ESCOM-IPN · Prof. Ulises Vélez Saldaña
--
--  Modelo físico normalizado a 3FN.
--  Derivado del Formato Único de Declaración (FUD) de la CEAVEM (8 hojas)
--  y de los catálogos del proyecto (contacto, lengua INALI, discapacidad).
--  SGBD: PostgreSQL 16
-- ============================================================================

-- Orden de borrado inverso al de creación para respetar las FK
DROP TABLE IF EXISTS nna_violencia, nna_dano, nna_lengua, nna_discapacidad,
    contacto, tutor, vulnerabilidad, organismo_ddhh, proceso_judicial,
    investigacion_ministerial, hechos_victimizantes, identificacion,
    domicilio, solicitante, nna, invitaciones, personal,
    cat_asentamiento, cat_municipio, cat_entidad,
    cat_nivel_competencia_oral, cat_modo_adquisicion_lengua, cat_lengua,
    cat_familia_linguistica, cat_tipo_discapacidad, cat_grado_dependencia,
    cat_tipo_violencia, cat_tipo_dano, cat_tipo_contacto,
    cat_tipo_documento_id, cat_tipo_victima, cat_tipo_solicitante,
    cat_nacionalidad, cat_estado_civil, cat_sexo
    CASCADE;

-- ============================================================================
--  BLOQUE 1 · CATÁLOGOS SIMPLES (tablas de referencia, dominios cerrados)
-- ============================================================================

CREATE TABLE cat_sexo (
    id_sexo     SERIAL PRIMARY KEY,
    nombre      VARCHAR(20) NOT NULL UNIQUE          -- Hombre, Mujer, Otro
);

CREATE TABLE cat_estado_civil (
    id_estado_civil SERIAL PRIMARY KEY,
    nombre          VARCHAR(30) NOT NULL UNIQUE
);

CREATE TABLE cat_nacionalidad (
    id_nacionalidad SERIAL PRIMARY KEY,
    nombre          VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE cat_tipo_solicitante (
    id_tipo_solicitante SERIAL PRIMARY KEY,
    clave               CHAR(1) NOT NULL UNIQUE,     -- A,B,C,D del FUD
    nombre              VARCHAR(80) NOT NULL
);

CREATE TABLE cat_tipo_victima (
    id_tipo_victima SERIAL PRIMARY KEY,
    nombre          VARCHAR(20) NOT NULL UNIQUE      -- Directa, Indirecta, Ofendido
);

CREATE TABLE cat_tipo_documento_id (
    id_tipo_documento SERIAL PRIMARY KEY,
    nombre            VARCHAR(80) NOT NULL UNIQUE
);

CREATE TABLE cat_tipo_contacto (
    id_tipo_contacto SERIAL PRIMARY KEY,
    nombre           VARCHAR(40)  NOT NULL UNIQUE,
    descripcion      VARCHAR(200)
);

CREATE TABLE cat_tipo_dano (
    id_tipo_dano SERIAL PRIMARY KEY,
    nombre       VARCHAR(20) NOT NULL UNIQUE         -- Físico, Psicológico, Sexual, Patrimonial, Otro
);

CREATE TABLE cat_tipo_violencia (
    id_tipo_violencia SERIAL PRIMARY KEY,
    nombre            VARCHAR(20) NOT NULL UNIQUE
);

CREATE TABLE cat_grado_dependencia (
    id_grado_dependencia SERIAL PRIMARY KEY,
    nombre               VARCHAR(20) NOT NULL UNIQUE -- Moderada, Severa, Gran dependencia
);

CREATE TABLE cat_tipo_discapacidad (
    id_tipo_discapacidad SERIAL PRIMARY KEY,
    nombre               VARCHAR(40) NOT NULL UNIQUE,
    descripcion          VARCHAR(200)
);

-- ============================================================================
--  BLOQUE 2 · CATÁLOGOS DE LENGUA (INALI)  ·  jerarquía familia → variante
-- ============================================================================

CREATE TABLE cat_familia_linguistica (
    id_familia SERIAL PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE cat_lengua (
    id_lengua        SERIAL PRIMARY KEY,
    id_familia       INTEGER NOT NULL REFERENCES cat_familia_linguistica(id_familia),
    agrupacion       VARCHAR(80)  NOT NULL,          -- agrupación lingüística
    variante         VARCHAR(80),                    -- variante lingüística
    autodenominacion VARCHAR(80),
    estado_region    VARCHAR(120)
);

CREATE TABLE cat_modo_adquisicion_lengua (
    id_modo_adquisicion SERIAL PRIMARY KEY,
    categoria           VARCHAR(40)  NOT NULL UNIQUE,-- L1, L2, extranjera, herencia, señas
    como_se_adquiere    VARCHAR(120),
    contexto            VARCHAR(160)
);

CREATE TABLE cat_nivel_competencia_oral (
    id_nivel    SERIAL PRIMARY KEY,
    nivel       VARCHAR(40)  NOT NULL UNIQUE,        -- Básico, Intermedio bajo/alto, Avanzado
    significado VARCHAR(300)
);

-- ============================================================================
--  BLOQUE 3 · CATÁLOGO DE DOMICILIO (SEPOMEX)  ·  entidad → municipio → asentamiento
-- ============================================================================

CREATE TABLE cat_entidad (
    id_entidad SERIAL PRIMARY KEY,
    nombre     VARCHAR(60) NOT NULL UNIQUE
);

CREATE TABLE cat_municipio (
    id_municipio SERIAL PRIMARY KEY,
    id_entidad   INTEGER NOT NULL REFERENCES cat_entidad(id_entidad),
    nombre       VARCHAR(80) NOT NULL,
    UNIQUE (id_entidad, nombre)
);

CREATE TABLE cat_asentamiento (
    id_asentamiento SERIAL PRIMARY KEY,
    id_municipio    INTEGER NOT NULL REFERENCES cat_municipio(id_municipio),
    codigo_postal   CHAR(5) NOT NULL,
    nombre          VARCHAR(120) NOT NULL
);

-- ============================================================================
--  BLOQUE 4 · USUARIOS DEL SISTEMA (personal e invitaciones de registro)
-- ============================================================================

CREATE TABLE personal (
    id_personal      SERIAL PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    primer_apellido  VARCHAR(60)  NOT NULL,
    segundo_apellido VARCHAR(60),
    rfc              VARCHAR(13)  UNIQUE,
    curp             VARCHAR(18)  UNIQUE,
    id_sexo          INTEGER REFERENCES cat_sexo(id_sexo),
    correo           VARCHAR(120) NOT NULL UNIQUE,
    contrasena       VARCHAR(255) NOT NULL,
    tipo             VARCHAR(20)  CHECK (tipo IN ('empleado','voluntario')),
    rol              VARCHAR(40)  CHECK (rol IN ('director','coordinador','psicologo',
                          'doctor','abogado','trabajador_social','analista',
                          'equipo_multidisciplinario','donante')),
    estado           VARCHAR(20)  DEFAULT 'pendiente'
                          CHECK (estado IN ('activo','inactivo','pendiente','restringido')),
    activo           BOOLEAN      DEFAULT FALSE,
    fecha_registro   TIMESTAMP    DEFAULT NOW()
);

CREATE TABLE invitaciones (
    id_invitacion  SERIAL PRIMARY KEY,
    token          VARCHAR(100) NOT NULL UNIQUE,
    creado_por     INTEGER REFERENCES personal(id_personal),
    fecha_creacion TIMESTAMP DEFAULT NOW(),
    fecha_expira   TIMESTAMP NOT NULL,
    usado          BOOLEAN   DEFAULT FALSE
);

-- ============================================================================
--  BLOQUE 5 · EXPEDIENTE  ·  entidades fuertes del FUD
-- ============================================================================

-- Hoja 1, sección II — datos personales del NNA (víctima)
CREATE TABLE nna (
    id_nna           SERIAL PRIMARY KEY,
    nombre           VARCHAR(100) NOT NULL,
    primer_apellido  VARCHAR(60)  NOT NULL,
    segundo_apellido VARCHAR(60),
    fecha_nacimiento DATE,
    id_sexo          INTEGER REFERENCES cat_sexo(id_sexo),
    id_nacionalidad  INTEGER REFERENCES cat_nacionalidad(id_nacionalidad),
    curp             VARCHAR(18) UNIQUE,
    id_estado_civil  INTEGER REFERENCES cat_estado_civil(id_estado_civil),
    lugar_nac_pais     VARCHAR(60),
    id_entidad_nac     INTEGER REFERENCES cat_entidad(id_entidad),
    lugar_nac_municipio VARCHAR(80),
    lugar_nac_comunidad VARCHAR(80),
    estatus          VARCHAR(20) DEFAULT 'sin_proceso'
                          CHECK (estatus IN ('sin_proceso','en_proceso','concluido')),
    registrado_por   INTEGER REFERENCES personal(id_personal),
    fecha_ingreso    TIMESTAMP DEFAULT NOW()
);

-- Hoja 1, sección I — quien realiza la solicitud
CREATE TABLE solicitante (
    id_solicitante      SERIAL PRIMARY KEY,
    id_nna              INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    id_tipo_solicitante INTEGER NOT NULL REFERENCES cat_tipo_solicitante(id_tipo_solicitante),
    nombre              VARCHAR(100),
    primer_apellido     VARCHAR(60),
    segundo_apellido    VARCHAR(60),
    parentesco          VARCHAR(80),     -- si B: parentesco/relación afectiva
    cargo               VARCHAR(80),     -- si C: cargo
    dependencia         VARCHAR(120),    -- si C: dependencia o institución
    telefono_movil      VARCHAR(20),
    fecha_solicitud     DATE,
    lugar_solicitud     VARCHAR(120)
);

-- Domicilio (del NNA y/o del lugar de hechos) — normaliza vía SEPOMEX
CREATE TABLE domicilio (
    id_domicilio    SERIAL PRIMARY KEY,
    id_nna          INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    tipo            VARCHAR(20) NOT NULL CHECK (tipo IN ('residencia','hechos')),
    id_asentamiento INTEGER REFERENCES cat_asentamiento(id_asentamiento),
    calle           VARCHAR(120),
    numero_exterior VARCHAR(20),
    numero_interior VARCHAR(20),
    referencias     VARCHAR(200)
);

-- Hoja 2, sección III — identificación de la víctima
CREATE TABLE identificacion (
    id_identificacion SERIAL PRIMARY KEY,
    id_nna            INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    presenta          BOOLEAN DEFAULT FALSE,
    id_tipo_documento INTEGER REFERENCES cat_tipo_documento_id(id_tipo_documento),
    numero_documento  VARCHAR(60)
);

-- Hoja 2, sección IV y V — tipo de víctima, lugar, fecha y relato de los hechos
CREATE TABLE hechos_victimizantes (
    id_hechos              SERIAL PRIMARY KEY,
    id_nna                 INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    id_tipo_victima        INTEGER REFERENCES cat_tipo_victima(id_tipo_victima),
    nombre_victima_directa VARCHAR(200),  -- si es indirecta/ofendido
    relacion_victima       VARCHAR(100),
    fecha_hechos           DATE,
    relato                 TEXT
);

-- Hoja 3, sección VII — investigación ante el Ministerio Público
CREATE TABLE investigacion_ministerial (
    id_investigacion SERIAL PRIMARY KEY,
    id_nna           INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    denuncio_mp      BOOLEAN DEFAULT FALSE,
    fecha            DATE,
    competencia      VARCHAR(20) CHECK (competencia IN ('Federal','Local')),
    id_entidad       INTEGER REFERENCES cat_entidad(id_entidad),
    agencia_mp       VARCHAR(120),
    tipo_registro    VARCHAR(10) CHECK (tipo_registro IN ('AP','CI','NC')),
    numero_registro  VARCHAR(60),
    delito           VARCHAR(200),
    estado_investigacion VARCHAR(120)
);

-- Hoja 3 — proceso judicial
CREATE TABLE proceso_judicial (
    id_proceso     SERIAL PRIMARY KEY,
    id_nna         INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    tiene_proceso  BOOLEAN DEFAULT FALSE,
    fecha_inicio   DATE,
    competencia    VARCHAR(20) CHECK (competencia IN ('Federal','Local')),
    id_entidad     INTEGER REFERENCES cat_entidad(id_entidad),
    delito         VARCHAR(200),
    numero_juzgado VARCHAR(40),
    numero_proceso VARCHAR(40),
    estado_proceso VARCHAR(120)
);

-- Hoja 3 — procedimientos ante organismos de derechos humanos
CREATE TABLE organismo_ddhh (
    id_organismo    SERIAL PRIMARY KEY,
    id_nna          INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    presento_queja  BOOLEAN DEFAULT FALSE,
    fecha           DATE,
    competencia     VARCHAR(20) CHECK (competencia IN ('Federal','Local','Internacional')),
    organismo       VARCHAR(160),
    violacion_ddhh  VARCHAR(200),
    autoridad_responsable VARCHAR(160),
    tipo_resolucion VARCHAR(40),
    folio           VARCHAR(60),
    estado_actual   VARCHAR(120)
);

-- Hoja 8 — condiciones de vulnerabilidad de la víctima
CREATE TABLE vulnerabilidad (
    id_vulnerabilidad   SERIAL PRIMARY KEY,
    id_nna              INTEGER NOT NULL UNIQUE REFERENCES nna(id_nna) ON DELETE CASCADE,
    es_nna              BOOLEAN DEFAULT TRUE,
    es_adulto_mayor     BOOLEAN DEFAULT FALSE,
    situacion_calle     BOOLEAN DEFAULT FALSE,
    tiene_discapacidad  BOOLEAN DEFAULT FALSE,
    es_migrante         BOOLEAN DEFAULT FALSE,
    pais_origen         VARCHAR(60),
    pais_destino        VARCHAR(60),
    habla_espanol       BOOLEAN DEFAULT TRUE,
    requiere_traductor  BOOLEAN DEFAULT FALSE,
    es_indigena         BOOLEAN DEFAULT FALSE,
    comunidad_indigena  VARCHAR(120),
    es_refugiado        BOOLEAN DEFAULT FALSE,
    es_asilado          BOOLEAN DEFAULT FALSE,
    es_defensor_ddhh    BOOLEAN DEFAULT FALSE,
    es_periodista       BOOLEAN DEFAULT FALSE,
    fue_desplazado      BOOLEAN DEFAULT FALSE,
    id_entidad_salida   INTEGER REFERENCES cat_entidad(id_entidad),
    id_entidad_receptora INTEGER REFERENCES cat_entidad(id_entidad),
    motivo_hecho        VARCHAR(120)  -- religión, orientación sexual, género, raza, etc.
);

-- Hoja 8 — tutor/a del NNA
CREATE TABLE tutor (
    id_tutor         SERIAL PRIMARY KEY,
    id_nna           INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    nombre           VARCHAR(100),
    primer_apellido  VARCHAR(60),
    segundo_apellido VARCHAR(60),
    parentesco       VARCHAR(80)
);

-- Datos de contacto (multivaluado): del NNA o de su tutor/a
CREATE TABLE contacto (
    id_contacto      SERIAL PRIMARY KEY,
    id_nna           INTEGER REFERENCES nna(id_nna) ON DELETE CASCADE,
    id_tutor         INTEGER REFERENCES tutor(id_tutor) ON DELETE CASCADE,
    id_tipo_contacto INTEGER NOT NULL REFERENCES cat_tipo_contacto(id_tipo_contacto),
    valor            VARCHAR(160) NOT NULL,
    CHECK (id_nna IS NOT NULL OR id_tutor IS NOT NULL)
);

-- ============================================================================
--  BLOQUE 6 · TABLAS DE ASOCIACIÓN (N:M)  ·  lo que estaba aplanado en "nna"
-- ============================================================================

CREATE TABLE nna_discapacidad (
    id_nna               INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    id_tipo_discapacidad INTEGER NOT NULL REFERENCES cat_tipo_discapacidad(id_tipo_discapacidad),
    id_grado_dependencia INTEGER REFERENCES cat_grado_dependencia(id_grado_dependencia),
    observaciones        TEXT,
    PRIMARY KEY (id_nna, id_tipo_discapacidad)
);

CREATE TABLE nna_lengua (
    id_nna              INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    id_lengua           INTEGER NOT NULL REFERENCES cat_lengua(id_lengua),
    id_modo_adquisicion INTEGER REFERENCES cat_modo_adquisicion_lengua(id_modo_adquisicion),
    id_nivel            INTEGER REFERENCES cat_nivel_competencia_oral(id_nivel),
    PRIMARY KEY (id_nna, id_lengua)
);

CREATE TABLE nna_dano (
    id_nna       INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    id_tipo_dano INTEGER NOT NULL REFERENCES cat_tipo_dano(id_tipo_dano),
    PRIMARY KEY (id_nna, id_tipo_dano)
);

CREATE TABLE nna_violencia (
    id_nna            INTEGER NOT NULL REFERENCES nna(id_nna) ON DELETE CASCADE,
    id_tipo_violencia INTEGER NOT NULL REFERENCES cat_tipo_violencia(id_tipo_violencia),
    PRIMARY KEY (id_nna, id_tipo_violencia)
);

-- ============================================================================
--  BLOQUE 7 · DATOS SEMILLA DE CATÁLOGOS
-- ============================================================================

INSERT INTO cat_sexo (nombre) VALUES ('Hombre'),('Mujer'),('Otro');
INSERT INTO cat_estado_civil (nombre) VALUES ('Soltero/a'),('Casado/a'),('Divorciado/a'),('Viudo/a'),('Unión libre'),('Concubinato'),('Separado/a'),('Otro');
INSERT INTO cat_nacionalidad (nombre) VALUES ('Mexicana'),('Extranjera');
INSERT INTO cat_tipo_solicitante (clave,nombre) VALUES ('A','Víctima u ofendido'),('B','Familiar o persona de confianza'),('C','Servidor/a público/a o autoridad'),('D','Representante legal');
INSERT INTO cat_tipo_victima (nombre) VALUES ('Directa'),('Indirecta'),('Ofendido');
INSERT INTO cat_tipo_documento_id (nombre) VALUES ('Credencial de Elector'),('Pasaporte'),('Cédula profesional'),('Cartilla del Servicio Militar'),('Certificado o constancia de estudios'),('Credencial IMSS'),('Credencial ISSSTE'),('Tarjeta de residencia temporal'),('Tarjeta de residencia permanente'),('Constancia de residencia'),('Otro documento oficial');
INSERT INTO cat_tipo_contacto (nombre,descripcion) VALUES ('Teléfono fijo','Número de teléfono fijo de casa, trabajo o de algún familiar. 10 dígitos.'),('Celular','Número de celular del tutor o de algún otro familiar. 10 dígitos.'),('Correo','Correo al que se pueda enviar documentación, generalmente de un adulto.'),('Instagram','Cuenta de Instagram para establecer comunicación.'),('Facebook','Cuenta de Facebook para establecer comunicación.'),('LinkedIn','Cuenta de LinkedIn para establecer comunicación.'),('Telegram','Cuenta de Telegram para establecer comunicación.');
INSERT INTO cat_tipo_dano (nombre) VALUES ('Físico'),('Psicológico'),('Sexual'),('Patrimonial'),('Otro');
INSERT INTO cat_tipo_violencia (nombre) VALUES ('Psicológica'),('Física'),('Económica'),('Patrimonial'),('Sexual'),('Obstétrica'),('Feminicida'),('Otro');
INSERT INTO cat_grado_dependencia (nombre) VALUES ('Moderada'),('Severa'),('Gran dependencia');
INSERT INTO cat_tipo_discapacidad (nombre,descripcion) VALUES ('Física','Limitaciones de movilidad o motrices.'),('Sensorial','Discapacidad visual o auditiva.'),('Intelectual/Cognitiva','Limitaciones en el funcionamiento intelectual.'),('Psicosocial','Relacionada con la salud mental.'),('Múltiple','Combinación de dos o más tipos de discapacidad.');
INSERT INTO cat_modo_adquisicion_lengua (categoria,como_se_adquiere,contexto) VALUES ('Lengua materna (L1)','Primera infancia, en el hogar','Entorno familiar y comunitario'),('Segunda lengua (L2)','Tras la L1, por necesidad social','País donde el idioma es predominante'),('Lengua extranjera','Aprendizaje formal (escuela, cursos)','País donde el idioma NO es predominante'),('Lengua de herencia','Infancia en el hogar, sin refuerzo social','Hijos de migrantes en país con idioma dominante distinto'),('Lengua de señas','Adquisición visual-gestual','Comunidad sorda');
INSERT INTO cat_nivel_competencia_oral (nivel,significado) VALUES ('Básico oral','Entiende saludos y palabras sueltas, no frases completas.'),('Intermedio bajo','Entiende conversaciones sencillas; se bloquea con estrés o vocabulario legal.'),('Intermedio alto','Se desenvuelve en conversaciones cotidianas con errores; pide repetición a veces.'),('Avanzado / Fluido','Habla con fluidez y entiende discursos complejos.');

INSERT INTO cat_familia_linguistica (nombre) VALUES
('Algic'),
('Cochimí-Yumana'),
('Seri'),
('Yuto-Nahua'),
('Oto-Mangue'),
('Maya'),
('Totonaco-Tepehua'),
('Tarasca'),
('Mixe-Zoque'),
('Chontal de Oaxaca'),
('Huave');

INSERT INTO cat_lengua (id_familia,agrupacion,estado_region) VALUES
(1,'Kickapoo','Coahuila'),
(2,'Cochimí','Baja California'),
(2,'Cucapá','Baja California'),
(2,'Kiliwa','Baja California'),
(2,'Kumiai','Baja California'),
(2,'Paipai','Baja California'),
(3,'Seri','Sonora'),
(4,'Cora','Nayarit'),
(4,'Guarijío','Sonora/Chihuahua'),
(4,'Huichol','Jalisco/Nayarit'),
(4,'Mateo','Chihuahua'),
(4,'Mayo','Sonora/Sinaloa'),
(4,'Náhuatl','Varios estados'),
(4,'Opata','Sonora (extinta)'),
(4,'Pápago','Sonora'),
(4,'Pima','Chihuahua/Sonora'),
(4,'Tarahumara','Chihuahua'),
(4,'Tepehuano del Norte','Chihuahua'),
(4,'Tepehuano del Sur','Durango'),
(4,'Yaqui','Sonora'),
(5,'Amuzgo','Guerrero/Oaxaca'),
(5,'Chatino','Oaxaca'),
(5,'Chichimeca Jonaz','Guanajuato'),
(5,'Chinanteco','Oaxaca'),
(5,'Chocholteco','Oaxaca'),
(5,'Cuicateco','Oaxaca'),
(5,'Ixcateco','Oaxaca'),
(5,'Matlatzinca','Estado de México'),
(5,'Mazahua','Estado de México/Michoacán'),
(5,'Mazateco','Oaxaca/Puebla'),
(5,'Mixteco','Oaxaca/Guerrero/Puebla'),
(5,'Otomí','Hidalgo/México/Querétaro'),
(5,'Pame','San Luis Potosí'),
(5,'Popoloca','Puebla'),
(5,'Tlapaneco (Me''phaa)','Guerrero'),
(5,'Tlahuica','Morelos'),
(5,'Triqui','Oaxaca'),
(5,'Zapoteco','Oaxaca'),
(6,'Akateko','Chiapas'),
(6,'Awakateko','Chiapas'),
(6,'Chuj','Chiapas'),
(6,'Ch''ol','Chiapas/Campeche/Tabasco'),
(6,'Chontal de Tabasco','Tabasco'),
(6,'Ixil','Chiapas'),
(6,'Jacalteko','Chiapas'),
(6,'Kaqchikel','Chiapas'),
(6,'K''iche''','Chiapas'),
(6,'Lacandón','Chiapas'),
(6,'Mam','Chiapas'),
(6,'Maya (Yucateco)','Yucatán/Campeche/Q.Roo'),
(6,'Q''anjob''al','Chiapas'),
(6,'Qato''k','Chiapas'),
(6,'Q''eqchí','Chiapas'),
(6,'Sakapulteko','Chiapas'),
(6,'Sipakapense','Chiapas'),
(6,'Tektiteko','Chiapas'),
(6,'Teko','Chiapas'),
(6,'Tseltal','Chiapas'),
(6,'Tsotsil','Chiapas'),
(6,'Uspanteko','Chiapas'),
(7,'Tepehua','Hidalgo/Veracruz/Puebla'),
(7,'Totonaco','Veracruz/Puebla/Hidalgo'),
(8,'Tarasco (Purépecha)','Michoacán'),
(9,'Ayapaneco','Tabasco'),
(9,'Mixe','Oaxaca'),
(9,'Oluteco','Veracruz'),
(9,'Popoluca','Veracruz'),
(9,'Popoluca de la Sierra','Veracruz'),
(9,'Sayulteco','Veracruz'),
(9,'Texistepequeño','Veracruz'),
(9,'Zoque','Oaxaca/Chiapas/Tabasco'),
(10,'Chontal de Oaxaca','Oaxaca'),
(11,'Huave','Oaxaca');

-- Usuario administrador semilla (contraseña debe re-hashearse con bcrypt en el backend)
INSERT INTO personal (nombre,primer_apellido,correo,contrasena,tipo,rol,estado,activo) VALUES ('Director','Sistema','director@fundacion.org','CAMBIAR_POR_HASH_BCRYPT','empleado','director','activo',TRUE);
