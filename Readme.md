# Auditoría Analítica de la Contratación Pública 2025  
## Contraloría General de Risaralda - Plataforma SIA Observa

## Descripción general

Este proyecto desarrolla un análisis técnico de la contratación pública reportada por los sujetos de control en la Plataforma SIA Observa, con énfasis en la vigencia 2025.  
El trabajo se implementa en Python mediante Jupyter Notebook y módulos de apoyo para limpieza, estandarización y análisis de datos contractuales.

El propósito institucional es fortalecer el control fiscal, mejorar la trazabilidad de la información contractual y aportar evidencia para la priorización de actuaciones auditoras.

## Objetivo general

Analizar el comportamiento de la contratación pública reportada en SIA Observa para la vigencia 2025, con criterios de control fiscal y transparencia, a fin de identificar patrones relevantes, riesgos potenciales y oportunidades de mejora en la rendición de información.

## Objetivos específicos

- Estandarizar y depurar los registros contractuales para mejorar su comparabilidad analítica.
- Caracterizar la contratación por modalidad, tipo de contrato, entidad, origen de recursos y temporalidad.
- Identificar contratos con adiciones relevantes como insumo de alertas tempranas de auditoría.
- Evaluar comportamientos de rendición extemporánea y su distribución por entidad.
- Generar salidas tabulares y visuales que faciliten la lectura técnica y la toma de decisiones.

## Alcance del análisis

- **Cobertura temática:** contratación reportada en SIA Observa (informes básico y extendido).
- **Cobertura temporal:** vigencia contractual 2025 (procesamiento y análisis ejecutados en 2026).
- **Cobertura analítica:** exploración descriptiva, agregaciones por variables clave, estandarización de categorías y visualización de resultados.
- **Propósito de uso:** apoyo al ejercicio auditor y a la transparencia institucional.

Este ejercicio no sustituye la revisión integral de legalidad contractual ni constituye, por sí mismo, un pronunciamiento fiscal definitivo.

## Fuente de datos

La fuente principal corresponde a los reportes de contratación descargados desde **SIA Observa**, plataforma de rendición de información contractual de los sujetos de control.

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
- Medición de rendición extemporánea (días de diferencia entre creación y acta de inicio) y resumen por entidad.

## Principales hallazgos

Los hallazgos concretos dependen de la ejecución del notebook con el corte de datos vigente. Con base en la lógica implementada, los resultados se reportan bajo una redacción de auditoría como la siguiente:

- Se evidenció concentración de valor contratado en un conjunto acotado de entidades, lo que orienta focos de seguimiento fiscal.
- Se identificó una participación diferenciada entre modalidades de contratación, con comportamiento heterogéneo en monto y frecuencia.
- Se observó comportamiento atípico en contratos con adiciones elevadas, clasificados como alertas para priorización de revisión.
- Se evidenció presencia de rendición extemporánea en registros contractuales, con variaciones en magnitud entre entidades.
- Se identificaron inconsistencias de nomenclatura y clasificación en variables contractuales, mitigadas parcialmente mediante estandarización.

> Nota: este repositorio no incorpora en el README cifras cerradas para evitar desactualización o inferencias sin validación del último corte procesado.

## Limitaciones del análisis

- Dependencia de la completitud y calidad de la información reportada por cada sujeto de control.
- Posibles cambios posteriores en SIA Observa no reflejados en el corte descargado.
- El enfoque es descriptivo y exploratorio; no reemplaza procedimientos auditorios de fondo (jurídico, financiero y técnico).
- La detección de alertas no implica automáticamente hallazgo fiscal, disciplinario o penal.

## Estructura del proyecto

```text
AUDITORIA SIA PARA CURSOR/
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

El proyecto proporciona una base analítica reproducible para el seguimiento de la contratación pública reportada en SIA Observa, con enfoque en control fiscal preventivo y transparencia.  
La estandarización de variables y la generación de alertas facilitan la identificación de patrones relevantes para priorizar actuaciones auditoras y robustecer la toma de decisiones institucionales.

## Posibles líneas futuras de análisis

- Incorporar series históricas multivigencia para evaluar tendencias y cambios estructurales.
- Integrar indicadores de riesgo por entidad, modalidad y tipo de contrato.
- Cruzar información contractual con ejecución presupuestal y resultados de auditorías previas.
- Implementar tableros interactivos para monitoreo continuo por dependencias misionales.
- Profundizar en análisis de redes de contratistas y concentración de proveedores.


## Creado por
Wilmer Fidel Restrepo Orrego.
Tecnico Operativo 314-05