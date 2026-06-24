import csv
from database import get_connection

def importar_lenguas():
    conexion = None
    try:
        conexion = get_connection()
        cursor = conexion.cursor()

        print("Asegurando que la tabla esté limpia...")
        cursor.execute("TRUNCATE TABLE catalogo_lenguas RESTART IDENTITY CASCADE;")

        print("Leyendo el archivo lenguas.csv...")
        with open('Database/lenguas.csv', mode='r', encoding='utf-8') as archivo:
            lector_csv = csv.DictReader(archivo)
            
            contador = 0
            for fila in lector_csv:
                cursor.execute(
                    "INSERT INTO catalogo_lenguas (familia, agrupacion, variante) VALUES (%s, %s, %s)",
                    (fila['familia'], fila['agrupacion'], fila['variante'])
                )
                contador += 1
                print(f"Insertado: {fila['variante']}")

        conexion.commit()
        print(f"\n¡Éxito! Se importaron {contador} variantes lingüísticas al catálogo.")

    except Exception as e:
        print(f"\nOcurrió un error al importar: {e}")
        if conexion:
            conexion.rollback()
    finally:
        if conexion:
            cursor.close()
            conexion.close()

if __name__ == "__main__":
    importar_lenguas()
