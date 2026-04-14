import pandas as pd


def calcular_alertas_adicion(df):

    df = df[df["VALOR_INICIAL_CONTRATO"] > 0].copy()
    df["PORCENTAJE_ADICION"] = (df["ADICIONES"] / df["VALOR_INICIAL_CONTRATO"]) * 100

    def clasificar(pct):
        if pct > 50:
            return "ALERTA ROJA"
        if pct > 0:
            return "CON_ADICION"
        return "SIN_ADICION"

    df["ESTADO_ADICION"] = df["PORCENTAJE_ADICION"].apply(clasificar)
    return df


def obtener_resumen_modalidad(df):
    return (
        df.groupby("MODALIDAD_CONTRATACION")["VALOR_VIGENTE"]
        .agg(["count", "sum"])
        .reset_index()
    )


def calcular_resumen_contratos(df):
    total_cantidad = len(df)

    total_valor = df["VALOR_VIGENTE"].sum()

    promedio_valor = total_valor / total_cantidad if total_cantidad > 0 else 0

    if not df.empty:
        idx_max = df["VALOR_VIGENTE"].idxmax()
        max_contrato = df.loc[idx_max]

        datos_max = {
            "valor": max_contrato["VALOR_VIGENTE"],
            "entidad": max_contrato["ENTIDAD"],
            "codigo": max_contrato["CODIGO_CONTRATO"],
            "objeto": max_contrato["OBJETO_CONTRATO"],
        }
    else:
        datos_max = {"valor": 0, "entidad": "N/A", "codigo": "N/A"}

    return {
        "cantidad": total_cantidad,
        "total_suma": total_valor,
        "promedio": promedio_valor,
        "mayor_contrato": datos_max,
    }


def contratacion_por_tipo_entidad(df):
    """
    Agrupa los contratos por TIPO_DE_ENTIDAD y calcula cantidad y suma de valores.
    """
    if "TIPO_DE_ENTIDAD" not in df.columns or "VALOR_VIGENTE" not in df.columns:
        return "⚠️ Columnas no encontradas"

    # Agrupamos y aplicamos múltiples funciones de agregación
    resumen_entidad = (
        df.groupby("TIPO_DE_ENTIDAD")["VALOR_VIGENTE"]
        .agg(CANTIDAD_CONTRATOS="count", VALOR_TOTAL="sum")
        .reset_index()
    )

    # Opcional: Ordenar de mayor a menor monto para identificar dónde está la plata
    resumen_entidad = resumen_entidad.sort_values(by="VALOR_TOTAL", ascending=False)

    return resumen_entidad


def analizar_por_tipo_contrato(df):
    """
    Calcula cantidad, % de participación y valor total por TIPO_CONTRATO.
    """
    if "TIPO_CONTRATO" not in df.columns or "VALOR_VIGENTE" not in df.columns:
        return "⚠️ Columnas no encontradas"

    # 1. Agrupación básica
    resumen = (
        df.groupby("TIPO_CONTRATO")["VALOR_VIGENTE"]
        .agg(CANTIDAD="count", VALOR_TOTAL="sum")
        .reset_index()
    )

    # 2. Calcular el porcentaje sobre el total de la muestra (filas)
    total_muestras = resumen["CANTIDAD"].sum()
    resumen["PORCENTAJE_PARTICIPACION"] = (resumen["CANTIDAD"] / total_muestras) * 100

    # 3. Ordenar por cantidad de mayor a menor
    resumen = resumen.sort_values(by="CANTIDAD", ascending=False)

    return resumen


def analizar_por_modalidad(df):
    """
    Agrupa por MODALIDAD_ESTANDAR y calcula cantidad y valor total.
    """
    col_mod = "MODALIDAD_ESTANDAR"
    col_val = "VALOR_VIGENTE"

    if col_mod not in df.columns or col_val not in df.columns:
        return "⚠️ Columnas no encontradas. Verifique que corrió las funciones de estandarización."

    # Agrupamos
    resumen = (
        df.groupby(col_mod)[col_val]
        .agg(CANTIDAD="count", VALOR_TOTAL="sum")
        .reset_index()
    )

    # Calculamos porcentaje de participación en cantidad para la tabla
    total_contratos = resumen["CANTIDAD"].sum()
    resumen["%_PARTICIPACION"] = (resumen["CANTIDAD"] / total_contratos) * 100

    # Ordenamos de mayor a menor monto
    return resumen.sort_values(by="VALOR_TOTAL", ascending=False)


def analizar_por_origen_recursos(df):
    """
    Agrupa por ORIGEN_RECURSOS_ESTANDAR y calcula cantidad y valor total.
    """
    col_recurso = "ORIGEN_RECURSOS_ESTANDAR"
    col_val = "VALOR_VIGENTE"

    if col_recurso not in df.columns or col_val not in df.columns:
        return "⚠️ Columna 'ORIGEN_RECURSOS_ESTANDAR' no encontrada. Ejecute estandarizar_recursos_v2 primero."

    # Agrupamos por la columna estandarizada
    resumen = (
        df.groupby(col_recurso)[col_val]
        .agg(CANTIDAD_CONTRATOS="count", VALOR_TOTAL="sum")
        .reset_index()
    )

    # Calculamos el porcentaje de inversión (Plata) sobre el total
    total_plata = resumen["VALOR_TOTAL"].sum()
    resumen["%_INVERSION"] = (resumen["VALOR_TOTAL"] / total_plata) * 100

    # Ordenamos de mayor a menor inversión
    return resumen.sort_values(by="VALOR_TOTAL", ascending=False)


def analizar_ranking_entidades(df):
    """
    Calcula cantidad de contratos y valor total por ENTIDAD,
    ordenando de mayor a menor según la inversión.
    """
    col_entidad = "ENTIDAD"
    col_val = "VALOR_VIGENTE"

    if col_entidad not in df.columns or col_val not in df.columns:
        return "⚠️ Columnas no encontradas."

    # Agrupamos por Entidad
    resumen = (
        df.groupby(col_entidad)[col_val]
        .agg(CANTIDAD_CONTRATOS="count", VALOR_TOTAL="sum")
        .reset_index()
    )

    # Ordenamos de mayor a menor valor vigente
    return resumen.sort_values(by="VALOR_TOTAL", ascending=False)


def analizar_rendicion_extemporanea(df):
    """
    Filtra contratos por estado 'RENDIDO EXTEMPORANEO' y calcula los días de retraso.
    """
    # 1. Copia y Filtro inicial por estado
    # Asegúrate de que el nombre de la columna sea ESTADO_CONTRATO
    df_ext = df[df["ESTADO_CONTRATO"] == "RENDIDO EXTEMPORANEO"].copy()

    # 2. Convertir a datetime
    df_ext["FECHA_CREACION"] = pd.to_datetime(df_ext["FECHA_CREACION"], errors="coerce")
    df_ext["FECHA_ACTA_DE_INICIO"] = pd.to_datetime(
        df_ext["FECHA_ACTA_DE_INICIO"], errors="coerce"
    )

    # 3. Calcular días (Fecha Creación - Fecha Inicio)
    # Si se rindió después del inicio, esta resta da los días de "demora" en el registro
    df_ext["DIAS_EXTEMPORANEIDAD"] = (
        df_ext["FECHA_CREACION"] - df_ext["FECHA_ACTA_DE_INICIO"]
    ).dt.days

    return df_ext


def resumen_extemporaneos_por_entidad(df_calculado):
    """
    Crea un resumen agrupado por entidad.
    """
    resumen = (
        df_calculado.groupby("ENTIDAD")
        .agg(
            TOTAL_CONTRATOS_EXTEMPORANEOS=("CODIGO_CONTRATO", "count"),
            PROMEDIO_DIAS_RETRASO=("DIAS_EXTEMPORANEIDAD", "mean"),
        )
        .reset_index()
        .sort_values(by="TOTAL_CONTRATOS_EXTEMPORANEOS", ascending=False)
    )

    return resumen


def calcular_duracion_vigencia(df):

    df = df.copy()

    df["DURACION_REAL"] = (df["FECHA_TERMINACION"] - df["FECHA_ACTA_DE_INICIO"]).dt.days

    df["VIGENCIA"] = (
        pd.to_numeric(df["VIGENCIA"], errors="coerce").fillna(2025).astype("Int64")
    )
    return df
