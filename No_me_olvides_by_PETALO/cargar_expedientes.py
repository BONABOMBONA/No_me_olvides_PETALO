import random
from datetime import date, timedelta
from database import get_connection

nombres_m = ["Sofía", "Valentina", "Regina", "Ximena", "Camila", "María", "Renata", "Daniela", "Fernanda", "Lucía", "Andrea", "Paola"]
nombres_h = ["Santiago", "Mateo", "Diego", "Emiliano", "Sebastián", "Leonardo", "Daniel", "Gael", "Ángel", "Iker", "Bruno", "Adrián"]
apellidos = ["García", "Hernández", "López", "Martínez", "Rodríguez", "Pérez", "Sánchez", "Ramírez",
             "Cruz", "Flores", "Gómez", "Morales", "Vázquez", "Reyes", "Jiménez", "Torres", "Mendoza", "Ortiz"]
calles = ["Av. Insurgentes", "Calle Morelos", "Av. Juárez", "Calle Hidalgo", "Av. Reforma",
          "Calle 5 de Mayo", "Av. Universidad", "Calle Allende", "Calle Guerrero", "Av. Constituyentes"]
referencias = ["Frente a la primaria", "Casa de portón verde", "Junto a la tienda", "Esquina con farmacia", "Cerca del parque"]
delitos = ["Feminicidio", "Homicidio doloso", "Violencia familiar", "Desaparición"]
agencias = ["Agencia Central de Investigación", "Fiscalía Desconcentrada", "Unidad de Atención a Víctimas"]
juzgados = ["Juzgado 1° Familiar", "Juzgado 3° Penal", "Juzgado 2° de lo Civil"]
organismos = ["CNDH", "Comisión Estatal de Derechos Humanos"]
relatos = [
    "El menor ingresa a la fundación tras el fallecimiento de su madre. Se canaliza para atención integral y acompañamiento.",
    "Caso remitido por el DIF estatal. Se da seguimiento al proceso de atención psicológica y resguardo del menor.",
    "Ingreso por orfandad materna. El menor queda bajo el cuidado de un familiar directo registrado como tutor.",
    "Se recibe a la niña en situación de vulnerabilidad. Se inicia valoración y plan de atención multidisciplinaria.",
    "El expediente se abre por canalización de la fiscalía. Se brinda acompañamiento jurídico y emocional al menor.",
]
parentescos = ["Abuelo/a", "Tío/a", "Hermano/a", "Tutor legal"]

def al(lista):
    return random.choice(lista)

def uid(cur, sql, *args):
    cur.execute(sql, args)
    r = cur.fetchone()
    return r[0] if r else None

def cargar():
    conn = get_connection()
    cur = conn.cursor()
    plan = [("en_proceso", 19), ("concluido", 14)]
    total = 0

    id_mexicana = uid(cur, "SELECT id_nacionalidad FROM cat_nacionalidad WHERE nombre='Mexicana'")
    id_soltero = uid(cur, "SELECT id_estado_civil FROM cat_estado_civil WHERE nombre='Soltero/a'")
    id_cel = uid(cur, "SELECT id_tipo_contacto FROM cat_tipo_contacto WHERE nombre='Celular'")
    id_correo = uid(cur, "SELECT id_tipo_contacto FROM cat_tipo_contacto WHERE nombre='Correo'")
    tipos_victima = ["Directa", "Indirecta", "Ofendido"]
    tipos_violencia = ["Feminicida", "Física", "Psicológica", "Sexual", "Económica"]
    tipos_dano = ["Físico", "Psicológico", "Sexual", "Patrimonial"]
    tipos_disc = ["Física", "Sensorial", "Intelectual/Cognitiva", "Psicosocial"]
    grados = ["Moderada", "Severa", "Gran dependencia"]
    tipos_sol = ["Familiar o persona de confianza", "Servidor/a público/a o autoridad", "Representante legal"]

    cur.execute("SELECT id_entidad FROM cat_entidad")
    entidades = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id_asentamiento FROM cat_asentamiento ORDER BY random() LIMIT 60")
    asentamientos = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id_lengua FROM cat_lengua ORDER BY random() LIMIT 20")
    lenguas = [r[0] for r in cur.fetchall()]
    cur.execute("SELECT id_enfermedad FROM cat_enfermedad")
    enfermedades = [r[0] for r in cur.fetchall()]

    for estatus, cantidad in plan:
        for _ in range(cantidad):
            es_mujer = random.random() < 0.5
            nombre = al(nombres_m if es_mujer else nombres_h)
            sexo = "Mujer" if es_mujer else "Hombre"
            p_ap = al(apellidos); s_ap = al(apellidos)
            anio = random.randint(2008, 2018)
            fnac = date(anio, random.randint(1, 12), random.randint(1, 28))
            curp = f"{p_ap[:2].upper()}{s_ap[0].upper()}{nombre[0].upper()}{str(anio)[2:]}{random.randint(10,99)}{random.randint(100,999)}"
            madre = f"{al(nombres_m)} {al(apellidos)} {al(apellidos)}"
            id_ent_nac = al(entidades)

            id_nna = uid(cur, """
                INSERT INTO nna (nombre, primer_apellido, segundo_apellido, fecha_nacimiento,
                    id_sexo, id_nacionalidad, curp, id_estado_civil, lugar_nac_pais,
                    id_entidad_nac, lugar_nac_municipio, lugar_nac_comunidad, estatus)
                VALUES (%s,%s,%s,%s,(SELECT id_sexo FROM cat_sexo WHERE nombre=%s),%s,%s,%s,'México',%s,%s,%s,%s)
                RETURNING id_nna
            """, nombre, p_ap, s_ap, fnac, sexo, id_mexicana, curp, id_soltero,
                 id_ent_nac, al(["Centro", "San Pedro", "La Magdalena"]), al(["Col. Centro", "Barrio Norte"]), estatus)

            id_asent = al(asentamientos)
            cur.execute("""INSERT INTO domicilio (id_nna, tipo, id_asentamiento, calle, numero_exterior, numero_interior, referencias)
                           VALUES (%s,'residencia',%s,%s,%s,%s,%s)""",
                        (id_nna, id_asent, al(calles), str(random.randint(1, 300)), str(random.randint(1, 20)), al(referencias)))

            fhechos = fnac + timedelta(days=random.randint(2000, 4000))
            cur.execute("""INSERT INTO hechos_victimizantes (id_nna, id_tipo_victima, nombre_victima_directa, relacion_victima, fecha_hechos, relato)
                           VALUES (%s,(SELECT id_tipo_victima FROM cat_tipo_victima WHERE nombre=%s),%s,'Madre',%s,%s)""",
                        (id_nna, al(tipos_victima), madre, fhechos, al(relatos)))

            for nd in random.sample(tipos_dano, random.randint(1, 3)):
                cur.execute("""INSERT INTO nna_dano (id_nna, id_tipo_dano) VALUES (%s,(SELECT id_tipo_dano FROM cat_tipo_dano WHERE nombre=%s)) ON CONFLICT DO NOTHING""", (id_nna, nd))
            for nv in random.sample(tipos_violencia, random.randint(1, 2)):
                cur.execute("""INSERT INTO nna_violencia (id_nna, id_tipo_violencia) VALUES (%s,(SELECT id_tipo_violencia FROM cat_tipo_violencia WHERE nombre=%s)) ON CONFLICT DO NOTHING""", (id_nna, nv))

            if estatus != "sin_proceso":
                cur.execute("""INSERT INTO investigacion_ministerial (id_nna, denuncio_mp, fecha, competencia, id_entidad, agencia_mp, tipo_registro, numero_registro, delito, estado_investigacion)
                               VALUES (%s,true,%s,'Local',%s,%s,'CI',%s,%s,%s)""",
                            (id_nna, fhechos, al(entidades), al(agencias),
                             f"CI/{random.randint(100,999)}/{anio}", al(delitos),
                             "Concluida" if estatus == "concluido" else "En integración"))
            if estatus == "concluido":
                cur.execute("""INSERT INTO proceso_judicial (id_nna, tiene_proceso, fecha_inicio, competencia, id_entidad, delito, numero_juzgado, numero_proceso, estado_proceso)
                               VALUES (%s,true,%s,'Local',%s,%s,%s,%s,'Sentencia firme')""",
                            (id_nna, fhechos + timedelta(days=120), al(entidades), al(delitos),
                             al(juzgados), f"{random.randint(100,999)}/{anio}"))
                cur.execute("""INSERT INTO organismo_ddhh (id_nna, presento_queja, fecha, competencia, organismo, violacion_ddhh, autoridad_responsable, tipo_resolucion, folio, estado_actual)
                               VALUES (%s,true,%s,'Federal',%s,'Derecho a la familia','Autoridad local','Recomendación',%s,'Concluido')""",
                            (id_nna, fhechos + timedelta(days=60), al(organismos), f"FOLIO/{random.randint(1000,9999)}"))

            es_ind = random.random() < 0.25
            cur.execute("""INSERT INTO vulnerabilidad (id_nna, es_nna, situacion_calle, tiene_discapacidad, es_migrante, habla_espanol, requiere_traductor, es_indigena, comunidad_indigena, motivo_hecho)
                           VALUES (%s,true,false,%s,false,true,%s,%s,%s,%s)""",
                        (id_nna, random.random() < 0.25, es_ind, es_ind,
                         "Comunidad originaria" if es_ind else None, "Orfandad por feminicidio"))

            if es_ind:
                cur.execute("INSERT INTO nna_lengua (id_nna, id_lengua) VALUES (%s,%s) ON CONFLICT DO NOTHING", (id_nna, al(lenguas)))
            if random.random() < 0.25:
                cur.execute("""INSERT INTO nna_discapacidad (id_nna, id_tipo_discapacidad, id_grado_dependencia)
                               VALUES (%s,(SELECT id_tipo_discapacidad FROM cat_tipo_discapacidad WHERE nombre=%s),(SELECT id_grado_dependencia FROM cat_grado_dependencia WHERE nombre=%s))""",
                            (id_nna, al(tipos_disc), al(grados)))

            tnom = al(nombres_m + nombres_h); tap1 = al(apellidos); tap2 = al(apellidos)
            id_tutor = uid(cur, "INSERT INTO tutor (id_nna, nombre, primer_apellido, segundo_apellido, parentesco, fecha_nacimiento) VALUES (%s,%s,%s,%s,%s,%s) RETURNING id_tutor",
                           id_nna, tnom, tap1, tap2, al(parentescos), date(random.randint(1965, 1996), random.randint(1,12), random.randint(1,28)))
            for ie in random.sample(enfermedades, random.randint(1, 2)):
                cur.execute("INSERT INTO nna_enfermedad (id_nna, id_enfermedad, esta_controlada) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                            (id_nna, ie, random.random() < 0.6))
            for ie in random.sample(enfermedades, random.randint(1, 2)):
                cur.execute("INSERT INTO tutor_enfermedad (id_tutor, id_enfermedad, esta_controlada) VALUES (%s,%s,%s) ON CONFLICT DO NOTHING",
                            (id_tutor, ie, random.random() < 0.6))
            tel_tutor = f"55{random.randint(10000000,99999999)}"
            cur.execute("INSERT INTO contacto (id_tutor, id_tipo_contacto, valor) VALUES (%s,%s,%s)", (id_tutor, id_cel, tel_tutor))
            cur.execute("INSERT INTO contacto (id_tutor, id_tipo_contacto, valor) VALUES (%s,%s,%s)",
                        (id_tutor, id_correo, f"{tnom.lower()}.{tap1.lower()}@correo.com"))
            cur.execute("INSERT INTO contacto (id_nna, id_tipo_contacto, valor) VALUES (%s,%s,%s)",
                        (id_nna, id_cel, f"55{random.randint(10000000,99999999)}"))

            cur.execute("""INSERT INTO solicitante (id_nna, id_tipo_solicitante, nombre, primer_apellido, segundo_apellido, parentesco, cargo, dependencia, telefono_movil, fecha_solicitud, lugar_solicitud)
                           VALUES (%s,(SELECT id_tipo_solicitante FROM cat_tipo_solicitante WHERE nombre=%s),%s,%s,%s,%s,%s,%s,%s,%s,'Ciudad de México')""",
                        (id_nna, al(tipos_sol), tnom, tap1, tap2, al(parentescos),
                         "Trabajador/a social", "DIF", tel_tutor, fhechos + timedelta(days=200)))

            total += 1

    conn.commit()
    cur.close()
    conn.close()
    print(f"{total} expedientes registrados.")

if __name__ == "__main__":
    cargar()
