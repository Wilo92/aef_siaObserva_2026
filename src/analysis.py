import pandas as pd


def calcular_alertas_adicion(df):
    
    df = df[df["VALOR_INICIAL_CONTRATO"] > 0].copy()
    df["PORCENTAJE_ADICION"] = (df["ADICIONES"] / df["VALOR_INICIAL_CONTRATO"]) * 100
    
    def clasificar(pct):
        if pct > 50: return "Adiciones que Superan el 50%"
        if pct > 0: return "Contrato con Adiciones"
        return "Contrato sin adiciones"
        
    df["ESTADO_ADICION"] = df["PORCENTAJE_ADICION"].apply(clasificar)
    return df

def obtener_resumen_modalidad(df):
    return df.groupby("MODALIDAD_CONTRATACION")["VALOR_VIGENTE"].agg(["count", "sum"]).reset_index()