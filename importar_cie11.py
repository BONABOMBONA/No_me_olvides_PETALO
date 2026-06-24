import csv
from database import get_connection

def importar_enfermedades():
    conexion = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        print("Limpiando el catálogo actual y reiniciando IDs...")
        cursor.execute("TRUNCATE TABLE catalogo_enfermedades RESTART IDENTITY CASCADE;")

        print("Leyendo el archivo cie11.csv...")
        with open('Database/cie11.csv', mode='r', encoding='utf-8') as archivo:
            lector_csv = csv.DictReader(archivo)
            
            contador = 0
            for fila in lector_csv:
                cursor.execute(
                    "INSERT INTO catalogo_enfermedades (codigo_oms, nombre) VALUES (%s, %s)",
                    (fila['codigo_oms'], fila['nombre'])
                )
                contador += 1
                print(f"Insertado: {fila['codigo_oms']} - {fila['nombre']}")

        conexion.commit()
        print(f"\n¡Éxito! Se importaron {contador} enfermedades al catálogo.")

    except Exception as e:
        print(f"\nOcurrió un error al importar: {e}")
        if conexion:
            conexion.rollback()
    finally:
        if conexion:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    importar_enfermedades()
