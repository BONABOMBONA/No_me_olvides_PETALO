import psycopg2
import os
from dotenv import load_dotenv

# Cargar variables de entorno (DB_HOST, DB_NAME, etc.)
load_dotenv()

def importar_catalogo():
    print("⏳ Conectando a la base de datos...")
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    cur = conn.cursor()

    print("🧹 Limpiando la tabla catalogo_sepomex antigua...")
    cur.execute("TRUNCATE TABLE catalogo_sepomex RESTART IDENTITY CASCADE;")

    print("📖 Leyendo el archivo CPdescarga.txt...")
    # SEPOMEX utiliza codificación ISO-8859-1 (Latin-1)
    with open("CPdescarga.txt", "r", encoding="iso-8859-1") as file:
        lineas = file.readlines()

    registros_insertados = 0
    print("⚙️ Procesando e importando datos, esto puede tardar unos segundos...")
    
    for linea in lineas:
        # Ignorar la primera línea de texto legal, las cabeceras y líneas vacías
        if "Catálogo Nacional" in linea or "d_codigo" in linea or not linea.strip():
            continue
        
        # SEPOMEX separa sus columnas con el símbolo |
        datos = linea.split('|')
        
        # Validar que la línea tenga el formato correcto
        if len(datos) > 4:
            cp = datos[0]               # Código Postal
            asentamiento = datos[1]     # Colonia
            municipio = datos[3]        # Municipio / Alcaldía
            estado = datos[4]           # Entidad Federativa
            
            cur.execute("""
                INSERT INTO catalogo_sepomex (codigo_postal, asentamiento, municipio, entidad_federativa) 
                VALUES (%s, %s, %s, %s)
            """, (cp, asentamiento, municipio, estado))
            registros_insertados += 1

    # Confirmar la transacción
    conn.commit()
    cur.close()
    conn.close()
    print(f"✅ ¡Éxito! Se importaron {registros_insertados} colonias a PostgreSQL.")

if __name__ == "__main__":
    importar_catalogo()
