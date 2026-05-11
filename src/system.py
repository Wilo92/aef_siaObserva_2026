# importacion de librerias
import pandas as pd
import numpy as np
import matplotlib
import plotly
import seaborn as sns
import platform


def get_library_versions():
    # Definicion del diccionario de librerias
    libraries = {
        "pandas": pd,
        "numpy": np,
        "matplotlib": matplotlib,
        "plotly": plotly,
        "seaborn": sns,
    }

    versions = {}

    for name, lib in libraries.items():
        try:
            versions[name] = lib.__version__
        except AttributeError:
            versions[name] = "libreria no instalada"

    return versions


# Prepara y exporta DataFrames para consumo en Power BI/Excel.


def exportar_para_bi(dfs_dict, path):
    import os

    os.makedirs(path, exist_ok=True)

    for nombre, df in dfs_dict.items():
        df_export = df.copy()

        # Fechas
        cols_fecha = df_export.select_dtypes(include=["datetime64"]).columns
        for col in cols_fecha:
            df_export[col] = df_export[col].dt.strftime("%Y-%m-%d")

        # Limpiar ';' internos en texto
        cols_texto = df_export.select_dtypes(include=["object"]).columns
        for col in cols_texto:
            df_export[col] = (
                df_export[col].astype(str).str.replace(";", ",", regex=False)
            )

        # ── NUEVO: truncar OBJETO_CONTRATO para que no rompa filas en Excel ──
        if "OBJETO_CONTRATO" in df_export.columns:
            df_export["OBJETO_CONTRATO"] = df_export["OBJETO_CONTRATO"].str[:200]

        full_path = os.path.join(path, f"{nombre}.csv")
        df_export.to_csv(full_path, index=False, encoding="utf-8-sig", sep=";",decimal=",",)
        print(f"Exportado: {nombre}.csv")
