import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

def importar_catalogo():
    print(" Conectando a la base de datos ")
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS")
    )
    cur = conn.cursor()

    print(" Tabla catalogo_sepomex antigua ")
    cur.execute("TRUNCATE TABLE catalogo_sepomex RESTART IDENTITY CASCADE;")

    print(" Archivo CPdescarga.txt ")
    
    with open("CPdescarga.txt", "r", encoding="iso-8859-1") as file:
        lineas = file.readlines()

    registros_insertados = 0
    print(" Procesando e importando datos")
    
    for linea in lineas:
        if "Catálogo Nacional" in linea or "d_codigo" in linea or not linea.strip():
            continue
        
        datos = linea.split('|')
        
        if len(datos) > 4:
            cp = datos[0]               
            asentamiento = datos[1]     
            municipio = datos[3]        
            estado = datos[4]          
            
            cur.execute("""
                INSERT INTO catalogo_sepomex (codigo_postal, asentamiento, municipio, entidad_federativa) 
                VALUES (%s, %s, %s, %s)
            """, (cp, asentamiento, municipio, estado))
            registros_insertados += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f" ¡Éxito! Se importaron {registros_insertados} colonias a PostgreSQL.")

if __name__ == "__main__":
    importar_catalogo()
