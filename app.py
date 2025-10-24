
import streamlit as st
import pandas as pd
import re
import unicodedata
from io import StringIO
from collections import defaultdict

# Configuración de la página
st.set_page_config(page_title="Generador CSV para Moodle", page_icon="📄", layout="centered")

st.title("📄 Generador de CSV compatible con Moodle")
st.markdown("Convierte texto o Excel con datos de alumnos en un archivo CSV listo para importar en Moodle.")

# Función para normalizar texto (eliminar tildes, ñ, partículas, etc.)
def normalizar_username(nombre, segundo_nombre, apellido):
    def limpiar(texto):
        texto = texto.lower()
        texto = unicodedata.normalize('NFKD', texto).encode('ASCII', 'ignore').decode('utf-8')
        texto = re.sub(r'[^\w\s]', '', texto)
        texto = re.sub(r'(de|del|la|las|los|el)', '', texto)
        texto = texto.replace('ñ', 'n')
        texto = texto.replace(' ', '')
        return texto

    nombre = limpiar(nombre)
    segundo = limpiar(segundo_nombre) if segundo_nombre else ''
    apellido = limpiar(apellido)
    username = f"{nombre}{segundo[:1]}.{apellido}"
    return username

# Función para detectar ciclo formativo desde los módulos
def detectar_ciclo(modulos):
    for m in modulos:
        if '_' in m:
            ciclo = m.split('_')[0]
            if ciclo.isalpha() and len(ciclo) >= 2:
                return ciclo
    return "SIN_CICLO"

# Función para procesar texto tabular copiado desde Excel
def procesar_tabular(texto):
    alumnos = defaultdict(lambda: {"firstname": "", "lastname": "", "email": "", "modulos": []})
    lineas = texto.strip().split('\n')
    for linea in lineas:
        partes = re.split(r'\t+', linea.strip())
        if len(partes) >= 3:
            nombre = partes[0].strip()
            apellidos = partes[1].strip()
            correo = partes[2].strip().lower()
            modulos = [m.strip() for m in partes[3:] if m.strip()]
            alumnos[correo]["firstname"] = nombre
            alumnos[correo]["lastname"] = apellidos
            alumnos[correo]["email"] = correo
            alumnos[correo]["modulos"].extend(modulos)
    return alumnos

# Función para generar el DataFrame final
def generar_dataframe(alumnos_dict):
    filas = []
    max_modulos = max(len(a["modulos"]) for a in alumnos_dict.values()) if alumnos_dict else 0
    for alumno in alumnos_dict.values():
        nombres = alumno["firstname"].split()
        nombre = nombres[0]
        segundo = nombres[1] if len(nombres) > 1 else ''
        apellido = alumno["lastname"].split()[0]
        username = normalizar_username(nombre, segundo, apellido)
        ciclo = detectar_ciclo(alumno["modulos"])
        firstname = f"[{ciclo}] {alumno['firstname']}"
        fila = {
            "username": username,
            "firstname": firstname,
            "lastname": alumno["lastname"],
            "email": alumno["email"]
        }
        for i, modulo in enumerate(alumno["modulos"]):
            fila[f"course{i+1}"] = modulo
            fila[f"role{i+1}"] = "student"
        filas.append(fila)
    df = pd.DataFrame(filas)
    return df

# Entrada de texto
st.subheader("✍️ Pega texto tabular copiado desde Excel")
texto_tabular = st.text_area("Pega aquí el texto copiado desde Excel (incluye nombre, apellidos, correo y módulos)", height=200)

# Procesar texto tabular
if texto_tabular:
    alumnos = procesar_tabular(texto_tabular)
    if alumnos:
        df_final = generar_dataframe(alumnos)
        st.success("✅ Datos procesados correctamente.")
        st.dataframe(df_final)

        # Descargar CSV
        csv = df_final.to_csv(index=False, sep=';', encoding='utf-8')
        st.download_button("📥 Descargar CSV para Moodle", data=csv, file_name="moodle_alumnos.csv", mime="text/csv")
    else:
        st.error("⚠️ No se encontraron datos válidos.")
