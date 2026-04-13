# Auditoría a la Contratación Pública 2025 - 53 sujetos de control.  
## Contraloría General de Risaralda - Plataforma SIA Observa

## Descripción general

Este proyecto realiza un análisis técnico de la contratación pública reportada por los sujetos de control en la plataforma SIA Observa, con énfasis en la vigencia 2025.

El desarrollo se implementa en Python, utilizando Jupyter Notebook para el análisis exploratorio y módulos especializados para la limpieza, estandarización y procesamiento de los datos.

Su propósito es fortalecer el control fiscal, mejorar la trazabilidad de la información contractual y generar insumos que apoyen la priorización de procesos de auditoría.

## Objetivo general

Analizar el comportamiento de la contratación pública reportada en SIA Observa para la vigencia 2025, con criterios de control fiscal y transparencia, a fin de identificar patrones relevantes, riesgos potenciales y oportunidades de mejora en la rendición de información.

## Objetivos específicos

- Estandarizar y depurar los registros contractuales para mejorar su calidad y comparabilidad analítica.
- Caracterizar la contratación pública según modalidad, tipo de contrato, entidad, origen de recursos y comportamiento temporal.
- Identificar contratos con adiciones relevantes como insumo para la generación de alertas tempranas en procesos de auditoría.
- Evaluar los comportamientos de rendición extemporánea y su distribución por entidad.
- Generar salidas tabulares y visuales que faciliten la interpretación técnica de la información y apoyen la toma de decisiones.
- Producir conjuntos de datos limpios y estructurados, listos para su consumo en herramientas de visualización como Power BI.
- Identificar los contratistas con mayor número de contratos, así como los montos y cuantías asociadas a su actividad contractual.

## Alcance del análisis

- **Cobertura temática:** Información de contratación pública reportada en la plataforma SIA Observa, incluyendo los informes básico y extendido.
- **Cobertura temporal:** Vigencia contractual 2025 (con procesamiento y análisis realizados durante el año 2026).
- **Cobertura analítica:** Análisis descriptivo de la información, incluyendo agregaciones por variables clave, estandarización de categorías y generación de visualizaciones.
- **Propósito de uso:** Apoyar el ejercicio auditor y fortalecer la transparencia en la gestión contractual.

Este ejercicio no sustituye la revisión integral de legalidad contractual ni constituye, por sí mismo, un pronunciamiento fiscal definitivo.

## Fuente de datos

La fuente principal corresponde a los reportes de contratación descargados desde **SIA Observa**, plataforma de rendición de información contractual de la Contraloria General del Risaralda para los 55 sujetos de control.

### Insumos usados en el proyecto

| Archivo | Contenido general | Ubicación |
|---|---|---|
| `Informe_Basico.xlsx` | Variables generales del contrato y estado de rendición | `data/raw/` |
| `Informe_Extendido.xlsx` | Variables adicionales de objeto, recursos y rubros | `data/raw/` |

### Consideraciones y posibles limitaciones de la fuente

- La calidad de los resultados depende de la oportunidad y consistencia del cargue realizado por cada entidad.
- Pueden existir registros actualizados de manera posterior al corte de análisis.
- La rendición extemporánea puede alterar lecturas de temporalidad y oportunidad del reporte.
- Diferencias de nomenclatura entre entidades requieren procesos de estandarización para análisis comparables.

## Metodología

La metodología combina prácticas de analítica de datos con enfoque de auditoría pública:

1. **Ingesta de datos:** lectura de archivos fuente en formato Excel.
2. **Depuración y tipificación:** conversión de tipos de dato (texto, fechas, numéricos), control de nulos y normalización de encabezados.
3. **Estandarización:** homologación de modalidades de contratación, causales y origen de recursos para reducir dispersión semántica.
4. **Análisis exploratorio y agregaciones:** cálculo de frecuencias, montos, participaciones y rankings por entidades y categorías.
5. **Alertas analíticas:** identificación de contratos con adiciones significativas y análisis de extemporaneidad en rendición.
6. **Visualización y exportación:** generación de tablas y gráficas de lectura institucional, además de salidas en Excel.

## Principales análisis realizados

- Conteo de contratos y sumatoria de valor vigente.
- Distribución por modalidad de contratación (categoría estandarizada).
- Distribución por tipo de contrato.
- Análisis por tipo de entidad y ranking por monto contratado.
- Análisis por origen de recursos (categorías estandarizadas).
- Identificación de contratos con adiciones y clasificación de alertas.
- Medición de rendición extemporánea (días de diferencia entre creación en el sistema y acta de inicio del contrato) y resumen por entidad.



## Resultados del análisis

Los resultados del análisis se generan a partir de la ejecución del notebook y los scripts incluidos en este repositorio, utilizando el conjunto de datos correspondiente al corte procesado.

Las salidas incluyen:

-Tablas agregadas por entidad, modalidad de contratación y tipo de contrato.
-Identificación de contratos con adiciones relevantes.
-Análisis de comportamientos de rendición extemporánea.
-Caracterización de contratistas según número de contratos y montos asociados.
-Visualizaciones que apoyan la interpretación de los datos.

Nota: Los hallazgos oficiales, conclusiones y análisis jurídico se presentan en el informe técnico en PDF elaborado en conjunto con el equipo auditor.



## Estructura del proyecto

```text
AUDITORIA_SIA/
|- notebooks/
|  `- analisis_contratacion_2026.ipynb
|- data/
|  |- raw/
|  |  |- Informe_Basico.xlsx
|  |  `- Informe_Extendido.xlsx
|  `- processed/
|- src/
|  |- cleaners.py
|  |- analysis.py
|  |- formatters.py
|  |- config.py
|  |- environment.py
|  |- system.py
|  `- __init__.py
|- requirements.txt
`- README.md
```

## Tecnologías utilizadas

- **Python 3.12**
- **Jupyter Notebook**
- **Pandas** (procesamiento y agregación de datos)
- **NumPy** (operaciones numéricas)
- **Matplotlib** (visualización)
- **openpyxl / xlrd** (lectura y escritura de Excel)

## Cómo ejecutar el proyecto

### 1) Preparar entorno

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 2) Verificar insumos de datos

- Ubicar `Informe_Basico.xlsx` y `Informe_Extendido.xlsx` en `data/raw/`.
- Confirmar que los nombres de archivo coincidan con los esperados por el notebook.

### 3) Ejecutar análisis

```bash
jupyter notebook
```

Luego abrir y ejecutar secuencialmente:

- `notebooks/analisis_contratacion_2026.ipynb`

### 4) Revisar resultados

- Tablas y gráficas en el notebook.
- Archivos exportados en `data/processed/` (según celdas de exportación ejecutadas).

## Conclusiones

El proyecto proporciona una base analítica reproducible para el seguimiento de la contratación pública reportada en SIA Observa.  
La estandarización de variables y la generación de alertas facilitan la identificación de patrones relevantes para priorizar actuaciones auditoras y robustecer la toma de decisiones institucionales.


## Autor

**Wilmer Fidel Restrepo Orrego**  
Técnico Operativo – Código 314-05  
Contraloria General del Risaralda
Mayo de 2026