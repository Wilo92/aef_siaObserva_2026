import pandas as pd


def calcular_alertas_adicion(df):

    df = df[df["VALOR_INICIAL_CONTRATO"] > 0].copy()
    df["PORCENTAJE_ADICION"] = (df["ADICIONES"] / df["VALOR_INICIAL_CONTRATO"]) * 100

    def clasificar(pct):
        if pct > 50:
            return "Adiciones que Superan el 50%"
        if pct > 0:
            return "Contrato con Adiciones"
        return "Contrato sin adiciones"

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
