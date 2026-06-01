import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import os
import sys
import time
import base64
import requests
from github import Github

try:
    from dotenv import load_dotenv

    load_dotenv()
except ImportError:
    pass

sys.path.insert(0, os.path.dirname(__file__))

from src.cleaners import (
    aplicar_tipos_datos,
    TIPOS_BASICO,
    TIPOS_EXTENDIDO,
    estandarizar_modalidades,
    estandarizar_causales,
    estandarizar_recursos_v2,
    validar_columnas_sia,
)
from src.analysis import calcular_duracion_vigencia
from src.system import exportar_para_bi

PROCESSED_PATH = os.path.join(os.path.dirname(__file__), "data", "processed_dinamico")

# ── URLs de los dashboards de Power BI ──────────────────────────────────────
URL_DASHBOARD_DINAMICO = "https://app.powerbi.com/view?r=eyJrIjoiNDlkNDg4ZmUtY2E1NC00ZTAyLWEzOWItZTVkMGZjNjJkYjYyIiwidCI6IjcxZTc1NWExLWI2ZjAtNDQyNC1hNGU1LTI1ZWQwZjY4NDhjZiIsImMiOjR9&pageName=c7af198a26c5edb2c43d"
URL_DASHBOARD_OFICIAL_1 = "https://app.powerbi.com/view?r=eyJrIjoiOTdiMjNlMTktNzE1My00OWFlLWE2ZGMtMWYxYzVlM2RmMGUzIiwidCI6IjcxZTc1NWExLWI2ZjAtNDQyNC1hNGU1LTI1ZWQwZjY4NDhjZiIsImMiOjR9&pageName=edf64b1f73e863d583df"
URL_DASHBOARD_OFICIAL_2 = "https://app.powerbi.com/view?r=eyJrIjoiNjhiMGZjMGUtZTUwZC00ZjYzLThjZmUtNjc5NTg5NTM1ZGIwIiwidCI6IjcxZTc1NWExLWI2ZjAtNDQyNC1hNGU1LTI1ZWQwZjY4NDhjZiIsImMiOjR9&pageName=c7af198a26c5edb2c43d"

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


# ── Log de historial de procesos ─────────────────────────────────────────────
def push_log_a_github(fecha_proceso, n_basico, n_extendido, n_entidades):
    token = os.getenv("GITHUB_TOKEN")
    repo_nombre = os.getenv("GITHUB_REPO")
    branch = os.getenv("GITHUB_BRANCH")

    g = Github(token)
    repo = g.get_repo(repo_nombre)

    ruta_log = "logs/historial_procesos.md"
    nueva_fila = f"| {fecha_proceso} | {n_basico:,} | {n_extendido:,} | {n_entidades:,} |\n"

    try:
        archivo = repo.get_contents(ruta_log, ref=branch)
        contenido_actual = archivo.decoded_content.decode("utf-8")
        contenido_nuevo = contenido_actual + nueva_fila
        repo.update_file(
            ruta_log,
            f"📊 Log pipeline: {fecha_proceso}",
            contenido_nuevo,
            archivo.sha,
            branch=branch,
        )
    except Exception:
        encabezado = (
            "# 📋 Historial de Procesos — CGR Risaralda\n\n"
            "| Fecha | Contratos Básico | Contratos Extendido | Entidades |\n"
            "|-------|-----------------|--------------------|-----------|\n"
        )
        repo.create_file(
            ruta_log,
            f"📊 Creación log pipeline: {fecha_proceso}",
            encabezado + nueva_fila,
            branch=branch,
        )


# ── Commit de ultimo_proceso.txt ─────────────────────────────────────────────
def push_fecha_a_github(fecha_proceso):
    token = os.getenv("GITHUB_TOKEN")
    repo_nombre = os.getenv("GITHUB_REPO")
    branch = os.getenv("GITHUB_BRANCH")

    g = Github(token)
    repo = g.get_repo(repo_nombre)

    ruta_github = "logs/ultimo_proceso.txt"
    contenido = fecha_proceso.encode("utf-8")

    try:
        archivo_existente = repo.get_contents(ruta_github, ref=branch)
        repo.update_file(
            ruta_github,
            f"🕐 Último proceso: {fecha_proceso}",
            contenido,
            archivo_existente.sha,
            branch=branch,
        )
    except Exception:
        repo.create_file(
            ruta_github,
            f"🕐 Último proceso: {fecha_proceso}",
            contenido,
            branch=branch,
        )


# ── README dinámico ───────────────────────────────────────────────────────────
def push_readme_a_github(fecha_proceso, n_basico, n_extendido, n_entidades):
    token = os.getenv("GITHUB_TOKEN")
    repo_nombre = os.getenv("GITHUB_REPO")
    branch = os.getenv("GITHUB_BRANCH")

    g = Github(token)
    repo = g.get_repo(repo_nombre)

    contenido_readme = f"""# 🏛️ Auditoría a la Contratación Pública 2025 — 53 Sujetos de Control
## Contraloría General de Risaralda · Plataforma SIA Observa

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat&logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-2.2.3-150458?style=flat&logo=pandas&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-automatizado-181717?style=flat&logo=github&logoColor=white)

---

## 📌 Descripción General

Este proyecto realiza un análisis técnico de la contratación pública reportada por los sujetos de control en la plataforma SIA Observa, con énfasis en la vigencia 2025.

El desarrollo se implementa en Python, utilizando Jupyter Notebook para el análisis exploratorio y módulos especializados para la limpieza, estandarización y procesamiento de los datos.

Su propósito es fortalecer el control fiscal, mejorar la trazabilidad de la información contractual y generar insumos que apoyen la priorización de procesos de auditoría.

---

## 🎯 Objetivo General

Analizar el comportamiento de la contratación pública reportada en SIA Observa para la vigencia 2025, con criterios de control fiscal y transparencia, a fin de identificar patrones relevantes, riesgos potenciales y oportunidades de mejora en la rendición de información.

## 🎯 Objetivos Específicos

- Estandarizar y depurar los registros contractuales para mejorar su calidad y comparabilidad analítica.
- Caracterizar la contratación pública según modalidad, tipo de contrato, entidad, origen de recursos y comportamiento temporal.
- Identificar contratos con adiciones relevantes como insumo para la generación de alertas tempranas en procesos de auditoría.
- Evaluar los comportamientos de rendición extemporánea y su distribución por entidad.
- Generar salidas tabulares y visuales que faciliten la interpretación técnica de la información y apoyen la toma de decisiones.
- Producir conjuntos de datos limpios y estructurados, listos para su consumo en herramientas de visualización como Power BI.
- Identificar los contratistas con mayor número de contratos, así como los montos y cuantías asociadas a su actividad contractual.

---

## 📐 Alcance del Análisis

- **Cobertura temática:** Información de contratación pública reportada en SIA Observa, incluyendo informes básico y extendido.
- **Cobertura temporal:** Vigencia contractual 2025.
- **Cobertura analítica:** Análisis descriptivo con agregaciones por variables clave, estandarización de categorías y visualizaciones.
- **Propósito de uso:** Apoyar el ejercicio auditor y fortalecer la transparencia en la gestión contractual.

---

## 🗂️ Fuente de Datos

La fuente principal corresponde a los reportes descargados desde **SIA Observa**, plataforma de rendición de información contractual de la Contraloría General de Risaralda para los 53 sujetos de control.

| Archivo | Contenido | Ubicación |
|---------|-----------|-----------|
| `Informe_Contratos_Basico.xlsx` | Variables generales del contrato y estado de rendición | Descarga SIA Observa |
| `Informe_Contratos_Extendido.xlsx` | Variables adicionales de objeto, recursos y rubros | Descarga SIA Observa |

### ⚠️ Consideraciones de la Fuente

- La calidad depende de la oportunidad y consistencia del cargue por cada entidad.
- Pueden existir registros actualizados de manera posterior al corte de análisis.
- La rendición extemporánea puede alterar lecturas de temporalidad y oportunidad.
- Diferencias de nomenclatura entre entidades requieren procesos de estandarización.

---

## 🔬 Metodología

1. **Ingesta de datos:** lectura de archivos fuente en formato Excel.
2. **Depuración y tipificación:** conversión de tipos de dato (texto, fechas, numéricos), control de nulos y normalización de encabezados.
3. **Estandarización:** homologación de modalidades de contratación, causales y origen de recursos para reducir dispersión semántica.
4. **Análisis exploratorio y agregaciones:** cálculo de frecuencias, montos, participaciones y rankings por entidades y categorías.
5. **Alertas analíticas:** identificación de contratos con adiciones significativas y análisis de extemporaneidad en rendición.
6. **Visualización y exportación:** generación de tablas y gráficas de lectura institucional, además de salidas en Excel.

---

## 📊 Principales Análisis

- Conteo de contratos y sumatoria de valor vigente.
- Distribución por modalidad de contratación (categoría estandarizada).
- Distribución por tipo de contrato.
- Análisis por tipo de entidad y ranking por monto contratado.
- Análisis por origen de recursos (categorías estandarizadas).
- Identificación de contratos con adiciones y clasificación de alertas.
- Medición de rendición extemporánea por entidad.

---

## ⚙️ Flujo del Pipeline Automatizado

```
Archivos SIA Observa (.xlsx)
        ↓
   Validación de columnas
        ↓
   Pipeline ETL
   ├── Limpieza y tipificación de datos
   ├── Estandarización de modalidades
   ├── Estandarización de causales
   ├── Estandarización de recursos
   └── Cálculo de duración y vigencia
        ↓
   Exportación CSV procesados
        ↓
   Push automático a GitHub
        ↓
   Power BI se actualiza en tiempo real
```

---

## 📂 Estructura del Repositorio

```
aef_siaObserva_2026/
├── app.py                              # Interfaz principal Streamlit
├── requirements.txt                    # Dependencias del proyecto
├── src/
│   ├── cleaners.py                     # Limpieza y estandarización de datos
│   ├── analysis.py                     # Cálculo de duraciones y vigencias
│   ├── formatters.py                   # Formateo de salidas
│   ├── config.py                       # Configuración del proyecto
│   ├── environment.py                  # Variables de entorno
│   ├── system.py                       # Exportación para Power BI
│   └── __init__.py
├── data/
│   ├── processed/                      # CSVs del análisis notebook
│   └── processed_dinamico/             # CSVs procesados (fuente Power BI)
│       ├── Informe_Basico_Procesado.csv
│       └── Informe_Extendido_Procesado.csv
├── notebooks/
│   └── analisis_contratacion_2026.ipynb
├── logs/
│   ├── historial_procesos.md           # Historial de cada ejecución
│   └── ultimo_proceso.txt              # Fecha del último proceso
└── assets/
    └── logo.png                        # Logo CGR Risaralda
```

---

## 📈 Dashboards Power BI

| Dashboard | Descripción |
|-----------|-------------|
| [Tablero Oficial 2024]({URL_DASHBOARD_OFICIAL_1}) | Actuación Especial de Fiscalización 2024 |
| [Tablero Oficial 2025]({URL_DASHBOARD_OFICIAL_2}) | Actuación Especial de Fiscalización 2025 |
| [Dashboard Tiempo Real]({URL_DASHBOARD_DINAMICO}) | Datos dinámicos — se actualiza con cada proceso |

---

## 🚀 Cómo Usar la App Web

1. Descarga los archivos desde **SIA Observa**:
   - `Informe_Contratos_Basico.xlsx`
   - `Informe_Contratos_Extendido.xlsx`
2. Abre la aplicación Streamlit
3. Carga los dos archivos en los campos correspondientes
4. Haz clic en **⚙️ Procesar y Publicar**
5. Espera a que el pipeline termine
6. Abre el dashboard de Power BI y refresca

## 💻 Cómo Ejecutar el Proyecto Localmente

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\\Scripts\\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la app
streamlit run app.py

# 4. O ejecutar el notebook
jupyter notebook notebooks/analisis_contratacion_2026.ipynb
```

---

## 🛠️ Tecnologías Utilizadas

- **Python 3.12**
- **Streamlit 1.45.1** — interfaz web
- **Pandas 2.2.3** — procesamiento y agregación
- **NumPy** — operaciones numéricas
- **Matplotlib / Seaborn / Plotly** — visualización
- **openpyxl / XlsxWriter** — lectura y escritura Excel
- **PyGithub** — integración automática con GitHub
- **Power BI** — visualización interactiva

---

## 🕐 Última Actualización del Pipeline

**{fecha_proceso}** (hora Colombia)

## 📊 Estadísticas del Último Proceso

| Métrica | Valor |
|---------|-------|
| Contratos Básico procesados | {n_basico:,} |
| Contratos Extendido procesados | {n_extendido:,} |
| Entidades analizadas | {n_entidades:,} |

---

## ✅ Conclusiones

El proyecto proporciona una base analítica reproducible para el seguimiento de la contratación pública reportada en SIA Observa.
La estandarización de variables y la generación de alertas facilitan la identificación de patrones relevantes para priorizar actuaciones auditoras y robustecer la toma de decisiones institucionales.

---

## 👤 Autor

**Wilmer Fidel Restrepo Orrego**
Técnico Operativo – Código 314-05
Contraloria General del Risaralda
Mayo de 2026
"""

    try:
        archivo = repo.get_contents("README.md", ref=branch)
        repo.update_file(
            "README.md",
            f"📝 README actualizado: {fecha_proceso}",
            contenido_readme,
            archivo.sha,
            branch=branch,
        )
    except Exception:
        repo.create_file(
            "README.md",
            f"📝 README inicial: {fecha_proceso}",
            contenido_readme,
            branch=branch,
        )
# ─────────────────────────────────────────────────────────────────────────────


def actualizar_powerbi():
    email = os.getenv("POWERBI_EMAIL")
    password = os.getenv("POWERBI_PASSWORD")
    dataset = os.getenv("POWERBI_DATASET_ID")

    if not all([email, password, dataset]):
        return False, "Variables de entorno no configuradas"

    # 1. Obtener token de acceso
    try:
        r = requests.post(
            "https://login.microsoftonline.com/common/oauth2/token",
            data={
                "grant_type": "password",
                "resource": "https://analysis.windows.net/powerbi/api",
                "client_id": "7f67af8a-fedc-4b08-8b4e-aa9179657f9d",
                "username": email,
                "password": password,
                "scope": "openid",
            },
            timeout=30,
        )
        token = r.json().get("access_token")
        if not token:
            return False, f"No se obtuvo token: {r.json().get('error_description', '')}"
    except Exception as e:
        return False, str(e)

    # 2. Llamar al endpoint de refresco
    try:
        r2 = requests.post(
            f"https://api.powerbi.com/v1.0/myorg/datasets/{dataset}/refreshes",
            headers={"Authorization": f"Bearer {token}"},
            timeout=30,
        )
        if r2.status_code == 202:
            return True, "OK"
        else:
            return False, f"Status {r2.status_code}: {r2.text}"
    except Exception as e:
        return False, str(e)


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
st.markdown(
    f"""
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

<div id="cgr-overlay">
    <img src="data:image/png;base64,{logo_b64}" alt="Procesando..."/>
    <p>Procesando datos de contratación pública...</p>
</div>

<script>
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
""",
    unsafe_allow_html=True,
)

# ── Header ────────────────────────────────────────────────────────────────────
st.markdown(
    f"""
<div class="header-institucional">
    <img class="logo-cgr" src="data:image/png;base64,{logo_b64}" alt="CGR Risaralda"/>
    <h1>Sistema de Auditoría Contractual<br>SIA Observa</h1>
    <p>Contraloría General de Risaralda · Grupo de Control Fiscal 2026</p>
</div>
""",
    unsafe_allow_html=True,
)

# ── Dashboards oficiales ──────────────────────────────────────────────────────
st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
st.markdown(
    '<div class="seccion-titulo">Estos son los Dashboards Oficiales Utilizados para Auditoría</div>',
    unsafe_allow_html=True,
)

col1, col2 = st.columns(2)
with col1:
    st.markdown('<div class="logo-pbi">', unsafe_allow_html=True)
    st.image(PBI_LOGO, width=56)
    st.markdown("</div>", unsafe_allow_html=True)
    st.link_button(
        "Tablero Oficial — Actuación Especial de Fiscalizacion 2024",
        url=URL_DASHBOARD_OFICIAL_1,
        use_container_width=True,
    )
with col2:
    st.markdown('<div class="logo-pbi">', unsafe_allow_html=True)
    st.image(PBI_LOGO, width=56)
    st.markdown("</div>", unsafe_allow_html=True)
    st.link_button(
        "Tablero Oficial — Actuación Especial de Fiscalizacion 2025",
        url=URL_DASHBOARD_OFICIAL_2,
        use_container_width=True,
    )

st.markdown("</div>", unsafe_allow_html=True)

# ── Carga de archivos ─────────────────────────────────────────────────────────
st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
st.markdown(
    '<div class="seccion-titulo">📂 Aqui se Cargan los Archivos Fuente</div>',
    unsafe_allow_html=True,
)
st.caption(
    "Inserta cada uno de los archivos de muestra (Informes Básico y Extendido) descargados desde la plataforma SIA Observa."
)

col1, col2 = st.columns(2)
with col1:
    archivo_basico = st.file_uploader(
        "Insertar Informe Básico", type=["xlsx"], key="basico"
    )
with col2:
    archivo_extendido = st.file_uploader(
        "Insertar Informe Extendido", type=["xlsx"], key="extendido"
    )

st.markdown("</div>", unsafe_allow_html=True)

# ── Validación y procesamiento ────────────────────────────────────────────────
if archivo_basico and archivo_extendido:

    nombre_basico_valido = archivo_basico.name == "Informe_Contratos_Basico.xlsx"
    nombre_extendido_valido = (
        archivo_extendido.name == "Informe_Contratos_Extendido.xlsx"
    )

    if not nombre_basico_valido:
        st.error(
            f"❌ El archivo básico debe llamarse **Informe_Contratos_Basico.xlsx** — recibido: `{archivo_basico.name}`"
        )
    if not nombre_extendido_valido:
        st.error(
            f"❌ El archivo extendido debe llamarse **Informe_Contratos_Extendido.xlsx** — recibido: `{archivo_extendido.name}`"
        )

    if nombre_basico_valido and nombre_extendido_valido:
        if st.button(
            "⚙️ Procesar y Publicar", type="primary", use_container_width=True
        ):
            st.cache_data.clear()

            with st.status("Procesando archivos...", expanded=True) as status:

                st.write("📂 Leyendo las muestra de Sia Observa...")
                df_basico = pd.read_excel(archivo_basico, skiprows=1)
                df_extendido = pd.read_excel(archivo_extendido, skiprows=1)

                errores_validacion = validar_columnas_sia(df_basico, df_extendido)
                if errores_validacion:
                    for error in errores_validacion:
                        st.error(f" {error}")
                    status.update(label="Archivos no válidos", state="error")
                    st.stop()

                st.write("⚙️ Ejecutando pipeline ETL...")
                df_basico = procesar_pipeline(df_basico, TIPOS_BASICO)
                df_extendido = procesar_pipeline(df_extendido, TIPOS_EXTENDIDO)

                st.write("💾 Exportando los archivos procesados...")
                exportar_para_bi(
                    {
                        "Informe_Basico_Procesado": df_basico,
                        "Informe_Extendido_Procesado": df_extendido,
                    },
                    PROCESSED_PATH,
                )

                time.sleep(3)

                st.write("🚀 Subiendo archivos a GitHub push automatico...")
                push_a_github(
                    os.path.join(PROCESSED_PATH, "Informe_Basico_Procesado.csv"),
                    "Informe_Basico_Procesado.csv",
                )
                push_a_github(
                    os.path.join(PROCESSED_PATH, "Informe_Extendido_Procesado.csv"),
                    "Informe_Extendido_Procesado.csv",
                )

                from datetime import datetime
                from datetime import timezone, timedelta

                zona_colombia = timezone(timedelta(hours=-5))
                fecha_proceso = datetime.now(zona_colombia).strftime("%d/%m/%Y %H:%M")
                with open(os.path.join(PROCESSED_PATH, "ultimo_proceso.txt"), "w") as f:
                    f.write(fecha_proceso)

                # ── NUEVO: log de historial ───────────────────────────────────
                st.write("📋 Actualizando log de historial...")
                push_log_a_github(
                    fecha_proceso,
                    len(df_basico),
                    len(df_extendido),
                    df_basico["ENTIDAD"].nunique(),
                )

                # ── NUEVO: commit de ultimo_proceso.txt ───────────────────────
                st.write("🕐 Registrando fecha de proceso...")
                push_fecha_a_github(fecha_proceso)

                # ── NUEVO: README dinámico ────────────────────────────────────
                st.write("📝 Actualizando README del repositorio...")
                push_readme_a_github(
                    fecha_proceso,
                    len(df_basico),
                    len(df_extendido),
                    df_basico["ENTIDAD"].nunique(),
                )
                # ─────────────────────────────────────────────────────────────

                sin_clasificar = (
                    df_basico["TIPO_DE_ENTIDAD"] == "NO CLASIFICADO"
                ).sum()
                if sin_clasificar > 0:
                    st.warning(
                        f"⚠️ {sin_clasificar} entidades sin clasificar — revisar diccionario."
                    )

                status.update(
                    label="El Procesamiento se ha completado — El Dashboard se ha actualizado",
                    state="complete",
                )

            # ── Resumen ───────────────────────────────────────────────────────
            st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
            st.markdown(
                '<div class="seccion-titulo"> Resumen del Procesamiento</div>',
                unsafe_allow_html=True,
            )

            col1, col2, col3 = st.columns(3)
            col1.metric("Contratos Básico", f"{len(df_basico):,}")
            col2.metric("Contratos Extendido", f"{len(df_extendido):,}")
            col3.metric("Entidades", f"{df_basico['ENTIDAD'].nunique():,}")

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Previsualización ──────────────────────────────────────────────
            st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
            st.markdown(
                '<div class="seccion-titulo"> Previsualización de Datos Procesados</div>',
                unsafe_allow_html=True,
            )

            tab1, tab2 = st.tabs(["Informe Básico", "Informe Extendido"])
            with tab1:
                st.caption(
                    f"{len(df_basico):,} contratos · {len(df_basico.columns)} columnas"
                )
                st.dataframe(
                    df_basico.head(50), use_container_width=True, hide_index=True
                )
            with tab2:
                st.caption(
                    f"{len(df_extendido):,} contratos · {len(df_extendido.columns)} columnas"
                )
                st.dataframe(
                    df_extendido.head(50), use_container_width=True, hide_index=True
                )

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Descarga ──────────────────────────────────────────────────────
            st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
            st.markdown(
                '<div class="seccion-titulo">⬇️ Descargar Archivos Procesados</div>',
                unsafe_allow_html=True,
            )

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

            st.markdown("</div>", unsafe_allow_html=True)

            # ── Dashboard dinámico ────────────────────────────────────────────
            st.markdown('<div class="seccion-card">', unsafe_allow_html=True)
            st.markdown(
                '<div class="seccion-titulo">📈 Ver el Dashboard de Contratación en Tiempo Real</div>',
                unsafe_allow_html=True,
            )
            st.caption(
                "Datos actualizados. Abre el dashboard y refresca para ver los cambios."
            )

            ruta_fecha = os.path.join(PROCESSED_PATH, "ultimo_proceso.txt")
            if os.path.exists(ruta_fecha):
                with open(ruta_fecha, "r") as f:
                    ultima_fecha = f.read()
                st.info(f" Última actualización: **{ultima_fecha}**")

            col1, col2, col3 = st.columns([1, 2, 1])
            with col2:
                st.markdown('<div class="logo-pbi">', unsafe_allow_html=True)
                st.image(PBI_LOGO, width=56)
                st.markdown("</div>", unsafe_allow_html=True)
                st.link_button(
                    "Ver Dashboard en Tiempo Real",
                    url=URL_DASHBOARD_DINAMICO,
                    use_container_width=True,
                )

            st.markdown("</div>", unsafe_allow_html=True)

else:
    st.info("⬆️ Carga los dos archivos Excel para habilitar el procesamiento.")

# ── Footer ────────────────────────────────────────────────────────────────────
st.markdown(
    """
<div class="footer-cgr">
    © 2026 CGR Risaralda &nbsp;·&nbsp; Pipeline de Auditoría Contractual &nbsp;·&nbsp; @WILO
</div>
""",
    unsafe_allow_html=True,
)
