import streamlit as st
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

# ── URLs de los dashboards de Power BI ──────────────────────────────────────
# Reemplaza cada URL cuando tengas los links publicados
URL_DASHBOARD_DINAMICO  = "https://URL_DASHBOARD_DINAMICO_AQUI"
URL_DASHBOARD_OFICIAL_1 = "https://URL_DASHBOARD_OFICIAL_1_AQUI"
URL_DASHBOARD_OFICIAL_2 = "https://URL_DASHBOARD_OFICIAL_2_AQUI"

# Logo oficial de Power BI desde Wikipedia (no requiere archivos locales)
PBI_LOGO = "https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg"
# ────────────────────────────────────────────────────────────────────────────


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
    page_title="Contraloría General de Risaralda",
    page_icon="assets/logo.png",
    layout="centered",
)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/logo.png", width=500)

st.title("Sistema de Auditoría Contractual SIA Observa — CGR Risaralda")
st.caption("Contraloría General de Risaralda — Plataforma SIA Observa")
st.divider()

# ── Sección dashboards ───────────────────────────────────────────────────────
st.subheader("📊 Dashboards de Control Fiscal")

col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(
        f'<a href="{URL_DASHBOARD_DINAMICO}" target="_blank">'
        f'<img src="{PBI_LOGO}" width="80" style="cursor:pointer;display:block;margin:auto"></a>'
        f'<p style="text-align:center;font-size:13px;margin-top:8px">Contratación en Tiempo Real</p>',
        unsafe_allow_html=True,
    )

with col2:
    st.markdown(
        f'<a href="{URL_DASHBOARD_OFICIAL_1}" target="_blank">'
        f'<img src="{PBI_LOGO}" width="80" style="cursor:pointer;display:block;margin:auto"></a>'
        f'<p style="text-align:center;font-size:13px;margin-top:8px">Auditoría Oficial — Muestra 1</p>',
        unsafe_allow_html=True,
    )

with col3:
    st.markdown(
        f'<a href="{URL_DASHBOARD_OFICIAL_2}" target="_blank">'
        f'<img src="{PBI_LOGO}" width="80" style="cursor:pointer;display:block;margin:auto"></a>'
        f'<p style="text-align:center;font-size:13px;margin-top:8px">Auditoría Oficial — Muestra 2</p>',
        unsafe_allow_html=True,
    )

st.divider()

# ── Sección carga de archivos ────────────────────────────────────────────────
st.subheader("Carga de Archivos Fuente")
st.caption("Carga los informes Básico y Extendido descargados desde SIA Observa.")

col1, col2 = st.columns(2)
with col1:
    archivo_basico = st.file_uploader(
        "Informe Básico", type=["xlsx"], key="basico"
    )
with col2:
    archivo_extendido = st.file_uploader(
        "Informe Extendido", type=["xlsx"], key="extendido"
    )

st.divider()

if archivo_basico and archivo_extendido:
    if st.button("⚙️ Procesar y Publicar", type="primary", use_container_width=True):
        st.cache_data.clear()

        with st.status("Procesando archivos...", expanded=True) as status:

            st.write("📂 Leyendo archivos Excel...")
            df_basico = pd.read_excel(archivo_basico, skiprows=1)
            df_extendido = pd.read_excel(archivo_extendido, skiprows=1)

            st.write("⚙️ Ejecutando pipeline ETL...")
            df_basico = procesar_pipeline(df_basico, TIPOS_BASICO)
            df_extendido = procesar_pipeline(df_extendido, TIPOS_EXTENDIDO)

            st.write("💾 Exportando archivos procesados...")
            exportar_para_bi(
                {
                    "Informe_Basico_Procesado": df_basico,
                    "Informe_Extendido_Procesado": df_extendido,
                },
                PROCESSED_PATH,
            )

            time.sleep(3)

            st.write("🚀 Subiendo archivos a GitHub...")
            push_a_github(
                os.path.join(PROCESSED_PATH, "Informe_Basico_Procesado.csv"),
                "Informe_Basico_Procesado.csv",
            )
            push_a_github(
                os.path.join(PROCESSED_PATH, "Informe_Extendido_Procesado.csv"),
                "Informe_Extendido_Procesado.csv",
            )

            sin_clasificar = (df_basico["TIPO_DE_ENTIDAD"] == "NO CLASIFICADO").sum()
            if sin_clasificar > 0:
                st.warning(
                    f"⚠️ {sin_clasificar} entidades sin clasificar — revisar diccionario."
                )

            status.update(
                label="✅ Procesamiento completado — Dashboard actualizado",
                state="complete",
            )

        st.divider()
        st.subheader("Resumen del Procesamiento")

        col1, col2, col3 = st.columns(3)
        col1.metric("Contratos Básico", f"{len(df_basico):,}")
        col2.metric("Contratos Extendido", f"{len(df_extendido):,}")
        col3.metric("Entidades", f"{df_basico['ENTIDAD'].nunique():,}")

        st.divider()
        st.subheader("Descargar Archivos Procesados")

        col1, col2 = st.columns(2)
        with col1:
            path_b = os.path.join(PROCESSED_PATH, "Informe_Basico_Procesado.csv")
            with open(path_b, "rb") as f:
                st.download_button(
                    "⬇️ Informe Básico Procesado",
                    f,
                    file_name="Informe_Basico_Procesado.csv",
                    mime="text/csv",
                    use_container_width=True,
                )
        with col2:
            path_e = os.path.join(PROCESSED_PATH, "Informe_Extendido_Procesado.csv")
            with open(path_e, "rb") as f:
                st.download_button(
                    "⬇️ Informe Extendido Procesado",
                    f,
                    file_name="Informe_Extendido_Procesado.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

        st.divider()
        st.info("💡 Abre el dashboard de Contratación en Tiempo Real y refresca para ver los datos actualizados.")

else:
    st.info("⬆️ Carga los dos archivos Excel para habilitar el procesamiento.")
