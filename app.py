import streamlit as st
import traceback
import sys
import pandas as pd
import os
import sys
import time
from github import Github

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass


sys.path.insert(0, os.path.dirname(__file__))

from src.cleaners import aplicar_tipos_datos, TIPOS_BASICO, TIPOS_EXTENDIDO
from src.analysis import calcular_duracion_vigencia
from src.cleaners import (
    estandarizar_modalidades,
    estandarizar_causales,
    estandarizar_recursos_v2,
)
from src.system import exportar_para_bi

PROCESSED_PATH = os.path.join(os.path.dirname(__file__), "data", "processed_dinamico")


def push_a_github(ruta_local, nombre_archivo):
    token = os.getenv("GITHUB_TOKEN")
    repo_nombre = os.getenv("GITHUB_REPO")
    branch = os.getenv("GITHUB_BRANCH")

    g = Github(token)
    repo = g.get_repo(repo_nombre)

    ruta_github = f"data/processed_dinamico/{nombre_archivo}"

    with open(ruta_local, "rb") as f:
        contenido = f.read()

    try:
        archivo_existente = repo.get_contents(ruta_github, ref=branch)
        repo.update_file(
            ruta_github,
            f"Actualización automática: {nombre_archivo}",
            contenido,
            archivo_existente.sha,
            branch=branch,
        )
        return True
    except Exception as e1:
        try:
            repo.create_file(
                ruta_github,
                f"Creación automática: {nombre_archivo}",
                contenido,
                branch=branch,
            )
            return True
        except Exception as e2:
            st.error(f"Error subiendo {nombre_archivo}: {e2}")
            return False


def procesar_pipeline(df, tipos):
    df = aplicar_tipos_datos(df, tipos)
    df = estandarizar_modalidades(df)
    df = estandarizar_causales(df)
    df = estandarizar_recursos_v2(df)
    df = calcular_duracion_vigencia(df)
    return df


st.set_page_config(
    page_title="Contraloria General del Risaralda",
    page_icon="assets/logo.png",
    layout="centered",
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/logo.png", width=500)

st.title("Sistema de Auditoría Contractual SIA Observa — CGR Risaralda")
st.caption("Contraloría General de Risaralda — Plataforma SIA Observa")
st.divider()

st.subheader(
    "Aqui se cargan los formatos Basicos y Extendidos que entrega el sistema de informacion Sia Observa"
)

col1, col2 = st.columns(2)
with col1:
    archivo_basico = st.file_uploader(
        "Aqui va el Informe Básico", type=["xlsx"], key="basico"
    )
with col2:
    archivo_extendido = st.file_uploader(
        "Aqui va el Informe Extendido", type=["xlsx"], key="extendido"
    )

st.divider()

if archivo_basico and archivo_extendido:
    if st.button("Procesar", type="primary", use_container_width=True):
        st.cache_data.clear()

        with st.status("Procesando archivos...", expanded=True) as status:

            st.write("Leyendo archivos Excel...")
            df_basico = pd.read_excel(archivo_basico, skiprows=1)
            df_extendido = pd.read_excel(archivo_extendido, skiprows=1)

            st.write("Ejecutando pipeline ETL...")
            df_basico = procesar_pipeline(df_basico, TIPOS_BASICO)
            df_extendido = procesar_pipeline(df_extendido, TIPOS_EXTENDIDO)

            st.write("Exportando archivos procesados...")
            exportar_para_bi(
                {
                    "Informe_Basico_Procesado": df_basico,
                    "Informe_Extendido_Procesado": df_extendido,
                },
                PROCESSED_PATH,
            )

            # Esperamos que el sistema de archivos termine de escribir
            time.sleep(5)

            # Verificamos cuántas filas quedaron en disco
            basico_local = pd.read_csv(
                os.path.join(PROCESSED_PATH, "Informe_Basico_Procesado.csv"),
                sep=";",
                decimal=",",
                encoding="utf-8-sig",
            )
            st.write(f"Filas en disco antes del push: {len(basico_local):,}")

            st.write("Subiendo archivos a GitHub...")
            resultado_basico = push_a_github(
                os.path.join(PROCESSED_PATH, "Informe_Basico_Procesado.csv"),
                "Informe_Basico_Procesado.csv",
            )
            st.write(f"Resultado básico: {resultado_basico}")

            resultado_extendido = push_a_github(
                os.path.join(PROCESSED_PATH, "Informe_Extendido_Procesado.csv"),
                "Informe_Extendido_Procesado.csv",
            )
            st.write(f"Resultado extendido: {resultado_extendido}")

            sin_clasificar = (df_basico["TIPO_DE_ENTIDAD"] == "NO CLASIFICADO").sum()
            if sin_clasificar > 0:
                st.warning(
                    f"{sin_clasificar} entidades sin clasificar — revisar diccionario."
                )

            status.update(label="Procesamiento completado", state="complete")

        st.divider()
        st.subheader("Resumen del procesamiento")

        col1, col2, col3 = st.columns(3)
        col1.metric("Contratos básico", f"{len(df_basico):,}")
        col2.metric("Contratos extendido", f"{len(df_extendido):,}")
        col3.metric("Entidades", f"{df_basico['ENTIDAD'].nunique():,}")

        st.divider()
        st.subheader("Descargar archivos procesados")

        col1, col2 = st.columns(2)
        with col1:
            path_b = os.path.join(PROCESSED_PATH, "Informe_Basico_Procesado.csv")
            with open(path_b, "rb") as f:
                st.download_button(
                    "Informe Básico Procesado",
                    f,
                    file_name="Informe_Basico_Procesado.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        with col2:
            path_e = os.path.join(PROCESSED_PATH, "Informe_Extendido_Procesado.csv")
            with open(path_e, "rb") as f:
                st.download_button(
                    "Informe Extendido Procesado",
                    f,
                    file_name="Informe_Extendido_Procesado.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

else:
    st.info("Carga los dos archivos Excel para habilitar el procesamiento.")
# Debug temporal
try:
    from src.cleaners import aplicar_tipos_datos
    st.success("imports OK")
except Exception as e:
    st.error(f"Error de import: {traceback.format_exc()}")
