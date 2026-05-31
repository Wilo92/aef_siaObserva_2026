import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import sys
import time
import base64
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
URL_DASHBOARD_DINAMICO  = "https://URL_DASHBOARD_DINAMICO_AQUI"
URL_DASHBOARD_OFICIAL_1 = "https://URL_DASHBOARD_OFICIAL_1_AQUI"
URL_DASHBOARD_OFICIAL_2 = "https://URL_DASHBOARD_OFICIAL_2_AQUI"

PBI_LOGO = "https://upload.wikimedia.org/wikipedia/commons/c/cf/New_Power_BI_Logo.svg"
# ────────────────────────────────────────────────────────────────────────────


def get_logo_base64():
    logo_path = os.path.join(os.path.dirname(__file__), "assets", "logo.png")
    with open(logo_path, "rb") as f:
        return base64.b64encode(f.read()).decode()


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

logo_b64 = get_logo_base64()

# ── CSS + spinner overlay ─────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Libre+Baskerville:wght@400;700&family=Source+Sans+3:wght@300;400;600&display=swap');

#MainMenu {{visibility: hidden;}}
header {{visibility: hidden;}}
footer {{visibility: hidden;}}
[data-testid="stToolbar"] {{visibility: hidden;}}

:root {{
    --verde: #2e7d32;
    --verde-claro: #e8f5e9;
    --gris-texto: #2c2c2c;
    --borde: #dde5dd;
}}

.block-container {{
    max-width: 820px !important;
    padding: 0 2rem 6rem 2rem !important;
}}

html, body, [class*="css"] {{
    font-family: 'Source Sans 3', sans-serif;
    color: var(--gris-texto);
}}

.header-institucional {{
    text-align: center;
    padding: 2rem 1rem 1.5rem 1rem;
    border-bottom: 2px solid var(--verde);
    margin-bottom: 2rem;
}}

.header-institucional img.logo-cgr {{
    width: 200px;
    margin-bottom: 1.2rem;
}}

.header-institucional h1 {{
    font-family: 'Libre Baskerville', serif;
    font-size: 2rem;
    font-weight: 700;
    color: var(--gris-texto);
    margin: 0 0 0.4rem 0;
    line-height: 1.3;
}}

.header-institucional p {{
    font-size: 0.82rem;
    color: #777;
    margin: 0;
    letter-spacing: 0.08em;
    text-transform: uppercase;
}}

.seccion-card {{
    background: white;
    border: 1px solid var(--borde);
    border-radius: 10px;
    padding: 1.2rem 1.8rem 1.5rem 1.8rem;
    margin-bottom: 1.5rem;
    box-shadow: 0 2px 8px rgba(0,0,0,0.05);
}}

.seccion-titulo {{
    font-family: 'Libre Baskerville', serif;
    font-size: 0.95rem;
    font-weight: 700;
    color: var(--verde);
    text-transform: uppercase;
    letter-spacing: 0.08em;
    margin-bottom: 1.2rem;
    padding-bottom: 0.5rem;
    border-bottom: 1px solid var(--verde-claro);
}}

[data-testid="stLinkButton"] > a {{
    background-color: white !important;
    color: var(--verde) !important;
    border: 1.5px solid var(--verde) !important;
    border-radius: 6px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-size: 0.85rem !important;
    font-weight: 600 !important;
    transition: all 0.2s ease !important;
}}

[data-testid="stLinkButton"] > a:hover {{
    background-color: var(--verde) !important;
    color: white !important;
}}

[data-testid="stButton"] > button[kind="primary"] {{
    background-color: var(--verde) !important;
    border: none !important;
    border-radius: 6px !important;
    font-family: 'Source Sans 3', sans-serif !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
    padding: 0.6rem 1rem !important;
    letter-spacing: 0.03em !important;
    transition: background-color 0.2s ease !important;
}}

[data-testid="stButton"] > button[kind="primary"]:hover {{
    background-color: #1b5e20 !important;
}}

[data-testid="stMetric"] {{
    background: var(--verde-claro);
    border-radius: 8px;
    padding: 0.8rem 1rem;
    border-left: 3px solid var(--verde);
}}

[data-testid="stDownloadButton"] > button {{
    background-color: white !important;
    color: var(--gris-texto) !important;
    border: 1px solid var(--borde) !important;
    border-radius: 6px !important;
    font-size: 0.9rem !important;
}}

[data-testid="stDownloadButton"] > button:hover {{
    border-color: var(--verde) !important;
    color: var(--verde) !important;
}}

[data-testid="stAlert"] {{
    border-radius: 8px !important;
    font-size: 0.9rem !important;
}}

.logo-pbi {{
    display: flex;
    justify-content: center;
    margin-bottom: 0.6rem;
}}

.footer-cgr {{
    position: fixed;
    bottom: 0; left: 0;
    width: 100%;
    background-color: var(--verde);
    text-align: center;
    padding: 10px 0;
    font-size: 0.78rem;
    color: rgba(255,255,255,0.85);
    letter-spacing: 0.05em;
    z-index: 999;
}}

/* Overlay spinner */
#cgr-overlay {{
    display: none;
    position: fixed;
    top: 0; left: 0;
    width: 100%; height: 100%;
    background: rgba(240,244,240,0.95);
    flex-direction: column;
    align-items: center;
    justify-content: center;
    z-index: 99999;
}}

#cgr-overlay.active {{
    display: flex;
}}

#cgr-overlay img {{
    width: 160px;
    animation: cgr-spin 1.2s linear infinite;
}}

#cgr-overlay p {{
    margin-top: 1.5rem;
    font-family: 'Source Sans 3', sans-serif;
    color: #2e7d32;
    font-size: 1.1rem;
    letter-spacing: 0.05em;
    text-align: center;
}}

@keyframes cgr-spin {{
    from {{ transform: rotate(0deg); }}
    to   {{ transform: rotate(360deg); }}
}}
</style>

<!-- Overlay spinner DOM -->
<div id="cgr-overlay">
    <img src="data:image/png;base64,{logo_b64}" alt="Procesando..."/>
    <p>Procesando datos de contratación pública...</p>
</div>

<script>
// Activar overlay cuando se hace clic en el botón Procesar
function bindSpinner() {{
    const buttons = document.querySelectorAll('button');
    buttons.forEach(btn => {{
        if (btn.innerText && btn.innerText.includes('Procesar') && !btn.dataset.cgrBound) {{
            btn.dataset.cgrBound = '1';
            btn.addEventListener('click', () => {{
                const ov = document.getElementById('cgr-overlay');
                if (ov) {{
                    ov.classList.add('active');
                    setTimeout(() => ov.classList.remove('active'), 8000);
                }}
            }});
        }}
    }});
}}
bindSpinner();
setTimeout(bindSpinner, 500);
setTimeout(bindSpinner, 1200);
setTimeout(bindSpinner, 2500);
</script>
""", unsafe_allow_html=True)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="header-institucional">
    <img class="logo-cgr" src="data:image/png;base64,{logo_b64}" alt="CGR Risaralda"/>
    <h1>Sistema de Auditoría Contractual<br>SIA Observa</h1>
    <p>Contraloría General de Risaralda · Control Fiscal 2026</p>
</div>
""", unsafe_allow_html=True)

# ── Dashboards oficiales ──────────────────────────────────────────────────────
st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
st.markdown('<div class="seccion-titulo">📋 Dashboards Oficiales de Auditoría</div>', unsafe_allow_html=True)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="logo-pbi">', unsafe_allow_html=True)
    st.image(PBI_LOGO, width=56)
    st.markdown('</div>', unsafe_allow_html=True)
    st.link_button("Auditoría Oficial — AEF 2024", url=URL_DASHBOARD_OFICIAL_1, use_container_width=True)
with col2:
    st.markdown('<div class="logo-pbi">', unsafe_allow_html=True)
    st.image(PBI_LOGO, width=56)
    st.markdown('</div>', unsafe_allow_html=True)
    st.link_button("Auditoría Oficial — AEF 2025", url=URL_DASHBOARD_OFICIAL_2, use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# ── Carga de archivos ─────────────────────────────────────────────────────────
st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
st.markdown('<div class="seccion-titulo">📂 Carga de Archivos Fuente</div>', unsafe_allow_html=True)
st.caption("Informes Básico y Extendido descargados desde SIA Observa.")

col1, col2 = st.columns(2)
with col1:
    archivo_basico = st.file_uploader("Informe Básico", type=["xlsx"], key="basico")
with col2:
    archivo_extendido = st.file_uploader("Informe Extendido", type=["xlsx"], key="extendido")

st.markdown('</div>', unsafe_allow_html=True)

# ── Validación y procesamiento ────────────────────────────────────────────────
if archivo_basico and archivo_extendido:

    nombre_basico_valido = archivo_basico.name == "Informe_Contratos_Basico.xlsx"
    nombre_extendido_valido = archivo_extendido.name == "Informe_Contratos_Extendido.xlsx"

    if not nombre_basico_valido:
        st.error(f"❌ El archivo básico debe llamarse **Informe_Contratos_Basico.xlsx** — recibido: `{archivo_basico.name}`")
    if not nombre_extendido_valido:
        st.error(f"❌ El archivo extendido debe llamarse **Informe_Contratos_Extendido.xlsx** — recibido: `{archivo_extendido.name}`")

    if nombre_basico_valido and nombre_extendido_valido:
        if st.button("⚙️ Procesar y Publicar", type="primary", use_container_width=True):
            st.cache_data.clear()

            with st.status("Procesando archivos...", expanded=True) as status:

                st.write("📂 Leyendo archivos Excel...")
                df_basico = pd.read_excel(archivo_basico, skiprows=1)
                df_extendido = pd.read_excel(archivo_extendido, skiprows=1)

                faltantes_basico = {"NIT", "ENTIDAD", "VIGENCIA"} - set(df_basico.columns)
                faltantes_extendido = {"NIT", "ENTIDAD", "VIGENCIA"} - set(df_extendido.columns)

                if faltantes_basico or faltantes_extendido:
                    if faltantes_basico:
                        st.error(f"❌ Informe Básico sin columnas esperadas: {faltantes_basico}")
                    if faltantes_extendido:
                        st.error(f"❌ Informe Extendido sin columnas esperadas: {faltantes_extendido}")
                    status.update(label="❌ Error de validación", state="error")
                    st.stop()

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

                from datetime import datetime
                fecha_proceso = datetime.now().strftime("%d/%m/%Y %H:%M")
                with open(os.path.join(PROCESSED_PATH, "ultimo_proceso.txt"), "w") as f:
                    f.write(fecha_proceso)

                sin_clasificar = (df_basico["TIPO_DE_ENTIDAD"] == "NO CLASIFICADO").sum()
                if sin_clasificar > 0:
                    st.warning(f"⚠️ {sin_clasificar} entidades sin clasificar — revisar diccionario.")

                status.update(label="✅ Procesamiento completado — Dashboard actualizado", state="complete")

            # ── Resumen ───────────────────────────────────────────────────────
            st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
            st.markdown('<div class="seccion-titulo">📊 Resumen del Procesamiento</div>', unsafe_allow_html=True)

            col1, col2, col3 = st.columns(3)
            col1.metric("Contratos Básico", f"{len(df_basico):,}")
            col2.metric("Contratos Extendido", f"{len(df_extendido):,}")
            col3.metric("Entidades", f"{df_basico['ENTIDAD'].nunique():,}")

            st.markdown('</div>', unsafe_allow_html=True)

            # ── Previsualización ──────────────────────────────────────────────
            st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
            st.markdown('<div class="seccion-titulo">🔍 Previsualización de Datos Procesados</div>', unsafe_allow_html=True)

            tab1, tab2 = st.tabs(["Informe Básico", "Informe Extendido"])
            with tab1:
                st.caption(f"{len(df_basico):,} contratos · {len(df_basico.columns)} columnas")
                st.dataframe(df_basico.head(50), use_container_width=True, hide_index=True)
            with tab2:
                st.caption(f"{len(df_extendido):,} contratos · {len(df_extendido.columns)} columnas")
                st.dataframe(df_extendido.head(50), use_container_width=True, hide_index=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # ── Descarga ──────────────────────────────────────────────────────
            st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
            st.markdown('<div class="seccion-titulo">⬇️ Descargar Archivos Procesados</div>', unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                path_b = os.path.join(PROCESSED_PATH, "Informe_Basico_Procesado.csv")
                with open(path_b, "rb") as f:
                    st.download_button("Informe Básico Procesado", f, file_name="Informe_Basico_Procesado.csv", mime="text/csv", use_container_width=True)
            with col2:
                path_e = os.path.join(PROCESSED_PATH, "Informe_Extendido_Procesado.csv")
                with open(path_e, "rb") as f:
                    st.download_button("Informe Extendido Procesado", f, file_name="Informe_Extendido_Procesado.csv", mime="text/csv", use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

            # ── Dashboard dinámico ────────────────────────────────────────────
            st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
            st.markdown('<div class="seccion-titulo">📈 Dashboard Contratación en Tiempo Real</div>', unsafe_allow_html=True)
            st.caption("Datos actualizados. Abre el dashboard y refresca para ver los cambios.")

            ruta_fecha = os.path.join(PROCESSED_PATH, "ultimo_proceso.txt")
            if os.path.exists(ruta_fecha):
                with open(ruta_fecha, "r") as f:
                    ultima_fecha = f.read()
                st.info(f"🕐 Última actualización: **{ultima_fecha}**")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown('<div class="logo-pbi">', unsafe_allow_html=True)
                st.image(PBI_LOGO, width=56)
                st.markdown('</div>', unsafe_allow_html=True)
                st.link_button("Ver Dashboard en Tiempo Real", url=URL_DASHBOARD_DINAMICO, use_container_width=True)

            st.markdown('</div>', unsafe_allow_html=True)

else:
    st.info("⬆️ Carga los dos archivos Excel para habilitar el procesamiento.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="footer-cgr">
    © 2026 CGR Risaralda &nbsp;·&nbsp; Pipeline de Auditoría Contractual &nbsp;·&nbsp; Desarrollado por @wilo
</div>
""", unsafe_allow_html=True)