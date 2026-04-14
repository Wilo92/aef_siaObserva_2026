# Observabilidad del entorno

import platform

from datetime import datetime


def get_environment_info():
    return {
        "os": f"{platform.system()} {platform.release()}",
        "python": platform.python_version(),
        "kernel": platform.python_implementation(),
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
