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

    # manejo de errores
    for name, lib in libraries.items():
        try:
            versions[name] = lib.__version__
        except AttributeError:
            versions[name] = "libreria no instalada"

    return versions
