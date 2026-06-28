"""
Importa el catálogo SEPOMEX (códigos postales) a las tablas normalizadas
cat_entidad -> cat_municipio -> cat_asentamiento.

Fuente: Database/catalogo_sepomex.csv
Uso:    python importar_sepomex.py
"""
import csv
from psycopg2.extras import execute_values
from database import get_connection

ARCHIVO_CSV = "Database/catalogo_sepomex.csv"


def importar_sepomex():
    conexion = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        print("Limpiando tablas de domicilio (entidad, municipio, asentamiento)...")
        cursor.execute("TRUNCATE TABLE cat_asentamiento, cat_municipio, cat_entidad "
                       "RESTART IDENTITY CASCADE;")

        print(f"Leyendo {ARCHIVO_CSV}...")
        entidades = {}            # nombre -> id
        municipios = {}           # (entidad, municipio) -> id
        asentamientos = []        # (id_municipio, cp, nombre)

        with open(ARCHIVO_CSV, mode="r", encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                ent = fila["entidad_federativa"].strip()
                mun = fila["municipio"].strip()
                cp = fila["codigo_postal"].strip()
                asen = fila["asentamiento"].strip()
                entidades.setdefault(ent, None)
                municipios.setdefault((ent, mun), None)

        # 1) Entidades
        print(f"Insertando {len(entidades)} entidades...")
        for nombre in entidades:
            cursor.execute("INSERT INTO cat_entidad (nombre) VALUES (%s) RETURNING id_entidad;",
                           (nombre,))
            entidades[nombre] = cursor.fetchone()[0]

        # 2) Municipios
        print(f"Insertando {len(municipios)} municipios...")
        for (ent, mun) in municipios:
            cursor.execute(
                "INSERT INTO cat_municipio (id_entidad, nombre) VALUES (%s, %s) RETURNING id_municipio;",
                (entidades[ent], mun))
            municipios[(ent, mun)] = cursor.fetchone()[0]

        # 3) Asentamientos (en bloque, por velocidad)
        print("Preparando asentamientos...")
        with open(ARCHIVO_CSV, mode="r", encoding="utf-8") as f:
            for fila in csv.DictReader(f):
                ent = fila["entidad_federativa"].strip()
                mun = fila["municipio"].strip()
                id_mun = municipios[(ent, mun)]
                asentamientos.append((id_mun, fila["codigo_postal"].strip(),
                                      fila["asentamiento"].strip()))

        print(f"Insertando {len(asentamientos)} asentamientos...")
        execute_values(cursor,
                       "INSERT INTO cat_asentamiento (id_municipio, codigo_postal, nombre) VALUES %s",
                       asentamientos, page_size=1000)

        conexion.commit()
        print(f"\n¡Éxito! {len(entidades)} entidades, {len(municipios)} municipios "
              f"y {len(asentamientos)} asentamientos importados.")

    except Exception as e:
        print(f"\nOcurrió un error al importar: {e}")
        if conexion:
            conexion.rollback()
    finally:
        if conexion:
            cursor.close()
            conexion.close()


if __name__ == "__main__":
    importar_sepomex()
