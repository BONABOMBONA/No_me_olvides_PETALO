-- ============================================================
-- Catálogo de Discapacidades — No Me Olvides / PETALO Agency
-- Basado en: LGDNNA, FUD CEAVEM, CIF (OMS)
-- ============================================================

-- Tabla principal del catálogo
CREATE TABLE IF NOT EXISTS catalogo_discapacidades (
    id_discapacidad     SERIAL PRIMARY KEY,
    tipo                VARCHAR(20) NOT NULL CHECK (tipo IN ('Física','Mental','Intelectual','Visual','Auditiva','Múltiple')),
    descripcion         VARCHAR(200) NOT NULL,
    grado_dependencia   VARCHAR(20) NOT NULL CHECK (grado_dependencia IN ('Moderada','Severa','Gran dependencia')),
    es_permanente       BOOLEAN DEFAULT TRUE
);

-- Tabla de relación NNA ↔ Discapacidad (un NNA puede tener varias)
CREATE TABLE IF NOT EXISTS nna_discapacidades (
    id              SERIAL PRIMARY KEY,
    id_nna          INTEGER REFERENCES nna(id) ON DELETE CASCADE,
    id_discapacidad INTEGER REFERENCES catalogo_discapacidades(id_discapacidad),
    observaciones   TEXT,
    fecha_registro  TIMESTAMP DEFAULT NOW()
);

-- Insertar datos del catálogo
INSERT INTO catalogo_discapacidades (tipo, descripcion, grado_dependencia, es_permanente) VALUES
('Física',      'Limitación para moverse o caminar',            'Moderada',        true),
('Física',      'Limitación para usar brazos o manos',          'Moderada',        true),
('Física',      'Parálisis parcial',                            'Severa',          true),
('Física',      'Parálisis total',                              'Gran dependencia',true),
('Mental',      'Trastorno de ansiedad',                        'Moderada',        false),
('Mental',      'Trastorno depresivo',                          'Moderada',        false),
('Mental',      'Trastorno bipolar',                            'Severa',          false),
('Mental',      'Esquizofrenia',                                'Severa',          true),
('Mental',      'Trastorno por estrés postraumático (TEPT)',    'Moderada',        false),
('Intelectual', 'Discapacidad intelectual leve',                'Moderada',        true),
('Intelectual', 'Discapacidad intelectual moderada',            'Severa',          true),
('Intelectual', 'Discapacidad intelectual severa',              'Gran dependencia',true),
('Intelectual', 'Síndrome de Down',                             'Severa',          true),
('Intelectual', 'Trastorno del Espectro Autista (TEA)',         'Severa',          true),
('Visual',      'Baja visión',                                  'Moderada',        true),
('Visual',      'Ceguera total',                                'Severa',          true),
('Visual',      'Pérdida visual en un ojo',                     'Moderada',        true),
('Auditiva',    'Hipoacusia leve',                              'Moderada',        true),
('Auditiva',    'Hipoacusia severa',                            'Severa',          true),
('Auditiva',    'Sordera total',                                'Gran dependencia',true),
('Auditiva',    'Sordera en un oído',                           'Moderada',        true),
('Múltiple',    'Discapacidad física y visual',                 'Gran dependencia',true),
('Múltiple',    'Discapacidad física e intelectual',            'Gran dependencia',true),
('Múltiple',    'Discapacidad auditiva e intelectual',          'Gran dependencia',true),
('Múltiple',    'Discapacidad física y mental',                 'Gran dependencia',true);

