import unicodedata
import pandas as pd

def limpiar_texto(texto):
    if not isinstance(texto, str): return texto
    texto = texto.replace("Ñ", "NH").replace("ñ", "nh")
    texto = (unicodedata.normalize("NFKD", texto)
             .encode("ascii", "ignore").decode("utf-8"))
    return texto.replace("NH", "N").strip().upper().replace(" ", "_").replace(".", "_")

def normalizar_cabeceras(df):
    df.columns = [limpiar_texto(col) for col in df.columns]
    return df

def procesar_fechas(df, columnas):
    for col in columnas:
        df[col] = pd.to_datetime(
            df[col].astype(str).str.strip().str[:10],
            format="%Y/%m/%d", errors="coerce"
        )
    return df