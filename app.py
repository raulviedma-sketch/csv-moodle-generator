
import streamlit as st
import pandas as pd
import re
import unicodedata
from collections import defaultdict
import io

st.set_page_config(page_title="Generador CSV para Moodle", page_icon="📄", layout="centered")

st.title("📄 Generador de CSV para Moodle")
st.markdown("Sube un archivo Excel o pega texto estructurado para generar un archivo CSV compatible con Moodle.")

# Función para normalizar nombres y generar username
def generar_username(nombre_completo):
    nombre_completo = nombre_completo.lower()
    nombre_completo = unicodedata.normalize('NFKD', nombre_completo).encode('ascii', 'ignore').decode('utf-8')
    nombre_completo = re.sub(r"[.,'’´`]", '', nombre_completo)
    nombre_completo = re.sub(r"\b(de|del|la|las|los|el)\b", '', nombre_completo)
    nombre_completo = nombre_completo.replace('ñ', 'n')
    nombre_completo = re.sub(r"\s+", ' ', nombre_completo).strip()

    partes = nombre_completo.split()
    if len(partes) < 2:
        return nombre_completo.replace(' ', '')
    nombre = partes[0]
    inicial_segundo = partes[1][0] if len(partes) > 2 else ''
    apellido = partes[-2] if len(partes) > 2 else partes[-1]
    return f"{nombre}{inicial_segundo}.{apellido}".replace(' ', '')

# Función para extraer módulos
def extraer_modulos(texto):
    texto = texto.replace('.', '')
    partes = re.split(r"con los módulos?:", texto, flags=re.IGNORECASE)
    if len(partes) < 2:
        return []
    modulos = re.split(r",| y ", partes[1])
    return [m.strip() for m in modulos if m.strip()]

# Función para detectar ciclo formativo
def detectar_ciclo(modulos):
    for m in modulos:
        match = re.search(r"\[(.*?)\]", m)
        if match:
            return match.group(1)
    return "SIN_CICLO"

# Procesamiento de texto estructurado
def procesar_texto(texto):
    alumnos = defaultdict(lambda: {"firstname": "", "lastname": "", "username": "", "email": "", "modulos": set()})
    lineas = texto.strip().split('\n')
    for linea in lineas:
        match = re.match(r"(.*?),\s*(.*?)\s+con correo\s+(\S+)\s+con los módulos?:\s*(.*)", linea, re.IGNORECASE)
        if match:
            apellidos, nombres, correo, mods = match.groups()
            nombre_completo = f"{nombres} {apellidos}"
            username = generar_username(nombre_completo)
            modulos = extraer_modulos("con los módulos: " + mods)
            ciclo = detectar_ciclo(modulos)
            alumnos[correo]["firstname"] = f"[{ciclo}] {nombres}"
            alumnos[correo]["lastname"] = apellidos
            alumnos[correo]["username"] = username
            alumnos[correo]["email"] = correo
            alumnos[correo]["modulos"].update(modulos)
    return alumnos

# Generar CSV
def generar_csv(alumnos):
    max_mods = max((len(data["modulos"]) for data in alumnos.values()), default=0)
    columnas = ["username", "firstname", "lastname", "email"]
    for i in range(1, max_mods + 1):
        columnas += [f"course{i}", f"role{i}"]

    filas = []
    for data in alumnos.values():
        fila = [data["username"], data["firstname"], data["lastname"], data["email"]]
        mods = sorted(data["modulos"])
        for m in mods:
            fila += [m, "student"]
        fila += [""] * (2 * (max_mods - len(mods)))
        filas.append(fila)

    df = pd.DataFrame(filas, columns=columnas)
    return df

# Entrada de texto
texto_input = st.text_area("✍️ Pega aquí el texto estructurado", height=200)

# Entrada de archivo Excel
archivo_excel = st.file_uploader("📄 O sube un archivo Excel (.xlsx)", type=["xlsx"])

# Botón para procesar
if st.button("🚀 Generar CSV"):
    alumnos = {}

    if texto_input:
        alumnos = procesar_texto(texto_input)

    if archivo_excel:
        df_excel = pd.read_excel(archivo_excel, engine="openpyxl")
        for _, row in df_excel.iterrows():
            linea = f"{row[0]}, {row[1]} con correo {row[2]} con los módulos: {row[3]}"
            alumnos.update(procesar_texto(linea))

    if not alumnos:
        st.warning("No se encontraron datos válidos.")
    else:
        df_csv = generar_csv(alumnos)
        buffer = io.StringIO()
        df_csv.to_csv(buffer, sep=";", index=False, encoding="utf-8")
        st.success("✅ Archivo CSV generado correctamente.")
        st.download_button("📥 Descargar CSV", buffer.getvalue(), file_name="moodle_alumnos.csv", mime="text/csv")
