import streamlit as st
import pandas as pd
import os
import sys
from datetime import datetime
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

URL_DASHBOARD_DINAMICO  = "https://URL_DASHBOARD_DINAMICO_AQUI"
URL_DASHBOARD_OFICIAL_1 = "https://URL_DASHBOARD_OFICIAL_1_AQUI"
URL_DASHBOARD_OFICIAL_2 = "https://URL_DASHBOARD_OFICIAL_2_AQUI"

PBI_LOGO = "https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg"


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
    except Exception:
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

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    [data-testid="stToolbar"] {visibility: hidden;}
    </style>
""", unsafe_allow_html=True)

col1, col2, col3 = st.columns([1, 2, 1])
with col2:
    st.image("assets/logo.png", width=500)

st.title("Sistema de Auditoría Contractual SIA Observa — CGR Risaralda")
st.caption("Contraloría General de Risaralda — Plataforma SIA Observa")
st.divider()

st.subheader("📋 Dashboards Oficiales de Auditoría")

col1, col2 = st.columns(2)
with col1:
    st.image(PBI_LOGO, width=80)
    st.link_button(
        "Auditoría Oficial — Muestra 1",
        url=URL_DASHBOARD_OFICIAL_1,
        use_container_width=True,
    )
with col2:
    st.image(PBI_LOGO, width=80)
    st.link_button(
        "Auditoría Oficial — Muestra 2",
        url=URL_DASHBOARD_OFICIAL_2,
        use_container_width=True,
    )

st.divider()

st.subheader("📁 Carga de Archivos Fuente")
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

            st.write("🚀 Subiendo archivos a GitHub...")
            ok1 = push_a_github(
                os.path.join(PROCESSED_PATH, "Informe_Basico_Procesado.csv"),
                "Informe_Basico_Procesado.csv",
            )
            ok2 = push_a_github(
                os.path.join(PROCESSED_PATH, "Informe_Extendido_Procesado.csv"),
                "Informe_Extendido_Procesado.csv",
            )

            st.session_state["ultima_actualizacion"] = datetime.now().strftime(
                "%d/%m/%Y a las %H:%M:%S"
            )
            st.session_state["df_basico"] = df_basico
            st.session_state["df_extendido"] = df_extendido

            sin_clasificar = (df_basico["TIPO_DE_ENTIDAD"] == "NO CLASIFICADO").sum()
            if sin_clasificar > 0:
                st.warning(
                    f"⚠️ {sin_clasificar} entidades sin clasificar — revisar diccionario."
                )

            if not ok1 or not ok2:
                st.error("❌ Uno o más archivos no se pudieron subir a GitHub.")
                status.update(label="⚠️ Procesado con errores", state="error")
            else:
                status.update(
                    label="✅ Procesamiento completado — Dashboard actualizado",
                    state="complete",
                )

elif not archivo_basico or not archivo_extendido:
    if "df_basico" not in st.session_state:
        st.info("⬆️ Carga los dos archivos Excel para habilitar el procesamiento.")

if "df_basico" in st.session_state:
    df_basico = st.session_state["df_basico"]
    df_extendido = st.session_state["df_extendido"]
    ultima_actualizacion = st.session_state["ultima_actualizacion"]

    st.divider()

    # ── Métricas ─────────────────────────────────────────────────────────────
    st.subheader("📊 Resumen del Procesamiento")
    col1, col2, col3 = st.columns(3)
    col1.metric("Contratos Básico", f"{len(df_basico):,}")
    col2.metric("Contratos Extendido", f"{len(df_extendido):,}")
    col3.metric("Entidades", f"{df_basico['ENTIDAD'].nunique():,}")

    # ── Card última ejecución ─────────────────────────────────────────────────
    st.markdown(
        f"""
        <div style="
            background-color: #f0f7f0;
            border: 1px solid #b2d8b2;
            border-left: 5px solid #2e7d32;
            border-radius: 8px;
            padding: 12px 20px;
            margin-top: 12px;
            font-size: 14px;
            color: #1b5e20;
        ">
            ✅ <strong>Último pipeline ejecutado:</strong> {ultima_actualizacion}
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.divider()

    # ── Previsualización con tabs ─────────────────────────────────────────────
    st.subheader("🔍 Previsualización de Datos Procesados")
    tab1, tab2 = st.tabs(["📄 Informe Básico", "📄 Informe Extendido"])

    with tab1:
        st.caption(f"Mostrando las primeras 10 filas de {len(df_basico):,} contratos")
        st.dataframe(df_basico.head(10), use_container_width=True)

    with tab2:
        st.caption(f"Mostrando las primeras 10 filas de {len(df_extendido):,} contratos")
        st.dataframe(df_extendido.head(10), use_container_width=True)

    st.divider()

    # ── Descargas ─────────────────────────────────────────────────────────────
    st.subheader("⬇️ Descargar Archivos Procesados")

    col1, col2 = st.columns(2)
    with col1:
        path_b = os.path.join(PROCESSED_PATH, "Informe_Basico_Procesado.csv")
        if os.path.exists(path_b):
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
        if os.path.exists(path_e):
            with open(path_e, "rb") as f:
                st.download_button(
                    "⬇️ Informe Extendido Procesado",
                    f,
                    file_name="Informe_Extendido_Procesado.csv",
                    mime="text/csv",
                    use_container_width=True,
                )

    st.divider()

    # ── Dashboard dinámico ────────────────────────────────────────────────────
    st.subheader("📊 Dashboard Contratación en Tiempo Real")

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.image(PBI_LOGO, width=80)
        st.link_button(
            "📈 Ver Contratación en Tiempo Real",
            url=URL_DASHBOARD_DINAMICO,
            use_container_width=True,
        )
        st.caption("Abre el dashboard y presiona **Actualizar** para ver los datos más recientes.")

# ── Footer ───────────────────────────────────────────────────────────────────
st.markdown("""
    <style>
    .footer {
        position: fixed;
        bottom: 0;
        left: 0;
        width: 100%;
        background-color: #f0f4f0;
        border-top: 1px solid #d0d8d0;
        text-align: center;
        padding: 8px 0;
        font-size: 12px;
        color: #555555;
        z-index: 999;
    }
    </style>
    <div class="footer">
        © 2026 CGR Risaralda &nbsp;|&nbsp; Pipeline de Auditoría Contractual &nbsp;|&nbsp; Desarrollado por @wilo
    </div>
""", unsafe_allow_html=True)