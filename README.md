# Generador CSV para Moodle

Esta aplicación web permite generar archivos CSV compatibles con Moodle a partir de texto estructurado o archivos Excel con datos de alumnos.

## 🚀 Funcionalidades

- Entrada de texto estructurado o archivo Excel
- Generación automática de `username`, `firstname`, `lastname`, `email`
- Extracción de módulos y asignación dinámica a columnas `courseX`, `roleX`
- Exportación a CSV con codificación UTF-8 y delimitador `;`
- Listo para importar en Moodle

## 🧪 Cómo usar en Streamlit Cloud

1. Crea un repositorio en GitHub y sube los archivos:
   - `app.py`
   - `requirements.txt`
   - `README.md`

2. Ve a [https://streamlit.io/cloud](https://streamlit.io/cloud) e inicia sesión con tu cuenta de GitHub.

3. Selecciona tu repositorio y despliega la aplicación.

4. ¡Listo! Comparte la URL pública con tus compañeros o alumnos.

## 📦 Requisitos

- Python 3.8+
- Streamlit
- Pandas
- Openpyxl