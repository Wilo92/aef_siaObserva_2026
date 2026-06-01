#  Auditoría a la Contratación Pública 2025 — 53 Sujetos de Control
## Contraloría General de Risaralda · Plataforma SIA Observa

![Python](https://img.shields.io/badge/Python-3.12-3776AB?style=flat&logo=python&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45.1-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![Power BI](https://img.shields.io/badge/Power%20BI-F2C811?style=flat&logo=powerbi&logoColor=black)
![Pandas](https://img.shields.io/badge/Pandas-2.2.3-150458?style=flat&logo=pandas&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-automatizado-181717?style=flat&logo=github&logoColor=white)

---

##  Descripción General

Este proyecto realiza un análisis técnico de la contratación pública reportada por los sujetos de control en la plataforma SIA Observa, con énfasis en la vigencia 2025.

El desarrollo se implementa en Python, utilizando Jupyter Notebook para el análisis exploratorio y módulos especializados para la limpieza, estandarización y procesamiento de los datos.

Su propósito es fortalecer el control fiscal, mejorar la trazabilidad de la información contractual y generar insumos que apoyen la priorización de procesos de auditoría.

---

##  Objetivo General

Analizar el comportamiento de la contratación pública reportada en SIA Observa para la vigencia 2025, con criterios de control fiscal y transparencia, a fin de identificar patrones relevantes, riesgos potenciales y oportunidades de mejora en la rendición de información.

##  Objetivos Específicos

- Estandarizar y depurar los registros contractuales para mejorar su calidad y comparabilidad analítica.
- Caracterizar la contratación pública según modalidad, tipo de contrato, entidad, origen de recursos y comportamiento temporal.
- Identificar contratos con adiciones relevantes como insumo para la generación de alertas tempranas en procesos de auditoría.
- Evaluar los comportamientos de rendición extemporánea y su distribución por entidad.
- Generar salidas tabulares y visuales que faciliten la interpretación técnica de la información y apoyen la toma de decisiones.
- Producir conjuntos de datos limpios y estructurados, listos para su consumo en herramientas de visualización como Power BI.
- Identificar los contratistas con mayor número de contratos, así como los montos y cuantías asociadas a su actividad contractual.

---

##  Alcance del Análisis

- **Cobertura temática:** Información de contratación pública reportada en SIA Observa, incluyendo informes básico y extendido.
- **Cobertura temporal:** Vigencia contractual 2025.
- **Cobertura analítica:** Análisis descriptivo con agregaciones por variables clave, estandarización de categorías y visualizaciones.
- **Propósito de uso:** Apoyar el ejercicio auditor y fortalecer la transparencia en la gestión contractual.

---

##  Fuente de Datos

La fuente principal corresponde a los reportes descargados desde **SIA Observa**, plataforma de rendición de información contractual de la Contraloría General de Risaralda para los 53 sujetos de control.

| Archivo | Contenido | Ubicación |
|---------|-----------|-----------|
| `Informe_Contratos_Basico.xlsx` | Variables generales del contrato y estado de rendición | Descarga SIA Observa |
| `Informe_Contratos_Extendido.xlsx` | Variables adicionales de objeto, recursos y rubros | Descarga SIA Observa |

###  Consideraciones de la Fuente

- La calidad depende de la oportunidad y consistencia del cargue por cada entidad.
- Pueden existir registros actualizados de manera posterior al corte de análisis.
- La rendición extemporánea puede alterar lecturas de temporalidad y oportunidad.
- Diferencias de nomenclatura entre entidades requieren procesos de estandarización.

---

##  Metodología

1. **Ingesta de datos:** lectura de archivos fuente en formato Excel.
2. **Depuración y tipificación:** conversión de tipos de dato (texto, fechas, numéricos), control de nulos y normalización de encabezados.
3. **Estandarización:** homologación de modalidades de contratación, causales y origen de recursos para reducir dispersión semántica.
4. **Análisis exploratorio y agregaciones:** cálculo de frecuencias, montos, participaciones y rankings por entidades y categorías.
5. **Alertas analíticas:** identificación de contratos con adiciones significativas y análisis de extemporaneidad en rendición.
6. **Visualización y exportación:** generación de tablas y gráficas de lectura institucional, además de salidas en Excel.

---

##  Principales Análisis

- Conteo de contratos y sumatoria de valor vigente.
- Distribución por modalidad de contratación (categoría estandarizada).
- Distribución por tipo de contrato.
- Análisis por tipo de entidad y ranking por monto contratado.
- Análisis por origen de recursos (categorías estandarizadas).
- Identificación de contratos con adiciones y clasificación de alertas.
- Medición de rendición extemporánea por entidad.

---

##  Flujo del Pipeline Automatizado

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

##  Estructura del Repositorio

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

##  Dashboards Power BI

| Dashboard | Descripción |
|-----------|-------------|
| [Tablero Oficial 2024](https://app.powerbi.com/view?r=eyJrIjoiOTdiMjNlMTktNzE1My00OWFlLWE2ZGMtMWYxYzVlM2RmMGUzIiwidCI6IjcxZTc1NWExLWI2ZjAtNDQyNC1hNGU1LTI1ZWQwZjY4NDhjZiIsImMiOjR9&pageName=edf64b1f73e863d583df) | Actuación Especial de Fiscalización 2024 |
| [Tablero Oficial 2025](https://app.powerbi.com/view?r=eyJrIjoiNjhiMGZjMGUtZTUwZC00ZjYzLThjZmUtNjc5NTg5NTM1ZGIwIiwidCI6IjcxZTc1NWExLWI2ZjAtNDQyNC1hNGU1LTI1ZWQwZjY4NDhjZiIsImMiOjR9&pageName=c7af198a26c5edb2c43d) | Actuación Especial de Fiscalización 2025 |
| [Dashboard Tiempo Real](https://app.powerbi.com/view?r=eyJrIjoiNDlkNDg4ZmUtY2E1NC00ZTAyLWEzOWItZTVkMGZjNjJkYjYyIiwidCI6IjcxZTc1NWExLWI2ZjAtNDQyNC1hNGU1LTI1ZWQwZjY4NDhjZiIsImMiOjR9&pageName=c7af198a26c5edb2c43d) | Datos dinámicos — se actualiza con cada proceso |

---

##  Cómo Usar la App Web

1. Descarga los archivos desde **SIA Observa**:
   - `Informe_Contratos_Basico.xlsx`
   - `Informe_Contratos_Extendido.xlsx`
2. Abre la aplicación Streamlit
3. Carga los dos archivos en los campos correspondientes
4. Haz clic en **⚙️ Procesar y Publicar**
5. Espera a que el pipeline termine
6. Abre el dashboard de Power BI y refresca

##  Cómo Ejecutar el Proyecto Localmente

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Ejecutar la app
streamlit run app.py

# 4. O ejecutar el notebook
jupyter notebook notebooks/analisis_contratacion_2026.ipynb
```

---

##  Tecnologías Utilizadas

- **Python 3.12**
- **Streamlit 1.45.1** — interfaz web
- **Pandas 2.2.3** — procesamiento y agregación
- **NumPy** — operaciones numéricas
- **Matplotlib / Seaborn / Plotly** — visualización
- **openpyxl / XlsxWriter** — lectura y escritura Excel
- **PyGithub** — integración automática con GitHub
- **Power BI** — visualización interactiva

---

##  Última Actualización del Pipeline

**01/06/2026 09:50** (hora Colombia)

##  Estadísticas del Último Proceso

| Métrica | Valor |
|---------|-------|
| Contratos Básico procesados | 8,289 |
| Contratos Extendido procesados | 8,159 |
| Entidades analizadas | 53 |

---

##  Conclusiones

El proyecto proporciona una base analítica reproducible para el seguimiento de la contratación pública reportada en SIA Observa.
La estandarización de variables y la generación de alertas facilitan la identificación de patrones relevantes para priorizar actuaciones auditoras y robustecer la toma de decisiones institucionales.

---

##  Autor

**Wilmer Fidel Restrepo Orrego**
Técnico Operativo – Código 314-05
Contraloria General del Risaralda
Mayo de 2026
