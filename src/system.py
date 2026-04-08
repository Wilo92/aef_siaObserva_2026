import pandas as pd
import numpy as np
import matplotlib
import plotly


def get_library_versions():
    return {
        "pandas": pd.__version__,
        "numpy": np.__version__,
        "matplotlib": matplotlib.__version__,
        "plotly": plotly.__version__,
    }
