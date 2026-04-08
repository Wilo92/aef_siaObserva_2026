import pandas as pd
import os
import matplotlib.pyplot as plt


BASE_DIR = os.path.abspath(os.path.join(os.getcwd(), ".."))
RAW_DATA_PATH = os.path.join(BASE_DIR, "data", "raw")

PROCESSED_DATA_PATH = os.path.join(BASE_DIR, "data", "processed")


def setup_environment():

    pd.options.display.float_format = "{:,.2f}".format
    pd.set_option("display.max_columns", None)
    pd.set_option("display.max_rows", 50)
    plt.style.use("ggplot")