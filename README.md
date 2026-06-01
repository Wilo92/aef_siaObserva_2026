# 📋 Pipeline de Auditoría Contractual — CGR Risaralda

> Sistema automatizado de procesamiento de datos de contratación pública.
> Contraloría General de Risaralda · Grupo de Control Fiscal 2026

---

## 🕐 Última Actualización

**31/05/2026 22:21** (hora Colombia)

## 📊 Estadísticas del Último Proceso

| Métrica | Valor |
|---------|-------|
| Contratos Básico | 870 |
| Contratos Extendido | 870 |
| Entidades | 38 |

---

## 🔗 Dashboards Power BI

- [Tablero Oficial 2024](https://app.powerbi.com/view?r=eyJrIjoiOTdiMjNlMTktNzE1My00OWFlLWE2ZGMtMWYxYzVlM2RmMGUzIiwidCI6IjcxZTc1NWExLWI2ZjAtNDQyNC1hNGU1LTI1ZWQwZjY4NDhjZiIsImMiOjR9&pageName=edf64b1f73e863d583df)
- [Tablero Oficial 2025](https://app.powerbi.com/view?r=eyJrIjoiNjhiMGZjMGUtZTUwZC00ZjYzLThjZmUtNjc5NTg5NTM1ZGIwIiwidCI6IjcxZTc1NWExLWI2ZjAtNDQyNC1hNGU1LTI1ZWQwZjY4NDhjZiIsImMiOjR9&pageName=c7af198a26c5edb2c43d)
- [Dashboard en Tiempo Real](https://app.powerbi.com/view?r=eyJrIjoiNDlkNDg4ZmUtY2E1NC00ZTAyLWEzOWItZTVkMGZjNjJkYjYyIiwidCI6IjcxZTc1NWExLWI2ZjAtNDQyNC1hNGU1LTI1ZWQwZjY4NDhjZiIsImMiOjR9&pageName=c7af198a26c5edb2c43d)

---

## ⚙️ Flujo del Pipeline

```
Archivos SIA Observa (.xlsx)
        ↓
   Validación de columnas
        ↓
   Pipeline ETL (limpieza, estandarización, duraciones)
        ↓
   Exportación CSV procesados
        ↓
   Push automático a GitHub → Power BI se actualiza
```

---

*Actualizado automáticamente por el pipeline — @WILO*
