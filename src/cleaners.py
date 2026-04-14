import pandas as pd
import unicodedata


# Esta funcion Limpia y estandariza textos de las muestras de auditoria
# maneja nulos, convierte algunos datos a string como nit o numero de cedula
# elimina tildes y caracteres especiales
# normaliza a mayúsculas y, si es cabecera, formatea el texto como nombre de columna válido.
def limpiar_texto_auditoria(texto, es_cabecera=False):

    if pd.isna(texto):
        return None

    texto = str(texto).strip()

    if texto == "":
        return None

    texto = texto.replace("Ñ", "NH").replace("ñ", "nh")
    texto = (
        unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    )
    texto = texto.replace("NH", "N").upper().strip()

    if es_cabecera:
        return texto.replace(" ", "_").replace(".", "_").replace("__", "_")

    return texto


# Aplica y estandariza tipos de datos a un DataFrame según un mapeo definido, limpiando textos
# convirtiendo valores numéricos y formateando fechas para asegurar consistencia en el análisis.
def aplicar_tipos_datos(df, mapeo_tipos):

    df.columns = [limpiar_texto_auditoria(col, es_cabecera=True) for col in df.columns]

    for col in df.columns:
        if col in mapeo_tipos:
            tipo = mapeo_tipos[col]

            if tipo == "str":
                df[col] = (
                    df[col]
                    .astype(str)
                    .apply(lambda x: limpiar_texto_auditoria(x, es_cabecera=False))
                )
                df[col] = df[col].replace("NONE", "NO_REPORTADO").fillna("NO_REPORTADO")

            elif tipo == "float":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0.0)

            elif tipo == "int":
                df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

            elif tipo == "fecha":

                df[col] = pd.to_datetime(
                    df[col].astype(str).str.strip().str[:10],
                    errors="coerce",
                )

    return df


# Diccionarios de configuración donde se definen el tipo de dato que se espera por cada columna.
# se utilizan para estandarizar y transformar la información del DataFrame durante el proceso de limpieza.
TIPOS_BASICO = {
    "TIPO_DE_ENTIDAD": "str",
    "NIT": "str",
    "ENTIDAD": "str",
    "VIGENCIA": "str",
    "CODIGO_CONTRATO": "str",
    "VALOR_INICIAL_CONTRATO": "float",
    "ADICIONES": "float",
    "LIBERACIONES": "float",
    "VALOR_VIGENTE": "float",
    "FECHA_SUSCRIPCION": "fecha",
    "FECHA_ACTA_DE_INICIO": "fecha",
    "FECHA_TERMINACION": "fecha",
    "TIEMPO_EJECUCION": "int",
    "MODALIDAD_CONTRATACION": "str",
    "CAUSAL_CONTRATO": "str",
    "TIPO_CONTRATO": "str",
    "FECHA_CREACION": "fecha",
    "FECHA_TERMINACION_AMPLIADA": "fecha",
    "ESTADO_CONTRATO": "str",
}

TIPOS_EXTENDIDO = {
    "TIPO_DE_ENTIDAD": "str",
    "NIT": "str",
    "ENTIDAD": "str",
    "VIGENCIA": "str",
    "CODIGO_CONTRATO": "str",
    "OBJETO_CONTRATO": "str",
    "FECHA_SUSCRIPCION": "fecha",
    "FECHA_ACTA_DE_INICIO": "fecha",
    "FECHA_TERMINACION": "fecha",
    "TIEMPO_EJECUCION": "int",
    "VALOR_INICIAL_CONTRATO": "float",
    "ADICIONES": "float",
    "LIBERACIONES": "float",
    "VALOR_VIGENTE": "float",
    "MODALIDAD_CONTRATACION": "str",
    "CAUSAL_CONTRATO": "str",
    "TIPO_CONTRATO": "str",
    "NOMBRE_DEL_RUBRO": "str",
    "APROPIACION_INICIAL": "float",
    "ORIGEN_RECURSOS": "str",
    "CDPS": "str",
    "RPS": "str",
    "FECHA_CREACION": "fecha",
}


# Estandariza los valores de la columna 'MODALIDAD_CONTRATACION'
# mapeándolos a categorías unificadas en 'MODALIDAD_ESTANDAR'
# para facilitar el análisis y la consistencia de la información.
def estandarizar_modalidades(df):

    if "MODALIDAD_CONTRATACION" not in df.columns:
        return df

    mapeo = {
        "SIN OFERTAS": "REGIMEN ESPECIAL",
        "CON OFERTAS": "REGIMEN ESPECIAL",
        "INVITACION DIRECTA": "INVITACION CERRADA",
        "ACUERDOS MARCO DE PRECIOS": "CONTRATACION DIRECTA",
        "INVITACION PUBLICA": "LICITACIONES PUBLICAS",
        "CONTRATACION CON ENTIDADES PRIVADAS SIN ANIMO DE LUCRO A LA QUE HACE REFERENCIA EL ART.355 CP.": "CONTRATACION DIRECTA",
    }

    df["MODALIDAD_ESTANDAR"] = (
        df["MODALIDAD_CONTRATACION"]
        .map(mapeo)
        .fillna(df["MODALIDAD_CONTRATACION"])
    )

    return df


# Estandariza los valores de la columna 'CAUSAL_CONTRATO' mediante un mapeo
# de categorías homogéneas, generando la columna 'CAUSAL_ESTANDAR' para
# facilitar el análisis, la depuración y la consistencia de los datos.
def estandarizar_causales(df):

    if "CAUSAL_CONTRATO" not in df.columns:
        return df

    mapeo_causales = {
        "SUBASTA INVERSA - LICITACION PUBLICA": "LICITACION PUBLICA",
        "ADQUISICION O SUMINISTRO DE BIENES Y SERVICIOS DE CARACTERISTICAS TECNICAS UNIFORMES": "SUBASTA INVERSA",##REVISAR
        "TIENDA VIRTUAL DEL ESTADO": "ACUERDO MARCO DE PRECIOS",
        "TIENDA VIRTUAL DEL ESTADO COLOMBIANO": "ACUERDO MARCO DE PRECIOS",
        "CONVENIOS INTERADMINISTRATIVOS": "CONTRATOS INTERADMINISTRATIVOS",
        "CONVENIOS DE COOPERACION INTERINSTITUCIONAL": "CONTRATOS INTERADMINISTRATIVOS",##REVISAR
        "CONVENIOS DE ASOCIACION ESAL": "AQUELLOS DE LOS QUE TRATA EL ARTICULO 355 DE LA CONSTITUCION POLITICA DE COLOMBIA",
        "SELECCION CUANDO HAY MAS DE UNA ESAL": "AQUELLOS DE LOS QUE TRATA EL ARTICULO 355 DE LA CONSTITUCION POLITICA DE COLOMBIA",
        "PRESTACION DE SERVICIOS - (SE ELIMINARA)": "PRESTACION DE SERVICIOS PROFESIONALES Y APOYO",
        "SIN PLURALIDAD DE OFERENTES": "MANUAL DE CONTRATACION",
        "DESARROLLO ACTIVIDAD CIENTIFICA Y TECNOLOGICA": "OTRAS FORMAS DE CONTRATACION DIRECTA",
        "ORDEN DE COMPRA": "SUMINISTROS",
        "ORDEN DE SERVICIO": "SUMINISTROS",
        "ABIERTO": "OTROS",
        "MANUAL DE CONTRATACION": "MANUAL DE CONTRATACION",
    }

    col_limpia = df["CAUSAL_CONTRATO"]

    df["CAUSAL_ESTANDAR"] = col_limpia.map(mapeo_causales).fillna(col_limpia)

    return df


# Estandariza la columna 'ORIGEN_RECURSOS' aplicando una lógica jerárquica
# para clasificar las fuentes de financiación en categorías homogéneas.
# La función identifica combinaciones de recursos (SGP, SGR, Nación y propios)
# y asigna una clasificación final en 'ORIGEN_RECURSOS_ESTANDAR' para mejorar
# la consistencia y el análisis de los datos.


import re
import unicodedata
import pandas as pd


def estandarizar_recursos_v2(df):
    if "ORIGEN_RECURSOS" not in df.columns:
        return df

    def mapeo_profundo(texto):
        if pd.isna(texto):
            return "NO REPORTADO"

        # 🔥 1. Normalización completa
        t = str(texto).upper().strip()

        # Quitar tildes (CLAVE)
        t = unicodedata.normalize("NFKD", t).encode("ascii", "ignore").decode("utf-8")

        # Limpiar espacios múltiples
        t = re.sub(r"\s+", " ", t)

        # 🔥 2. Tokenización inteligente
        tokens = set(t.split())

        # 🔥 3. Flags robustos
        tiene_sgp = "SGP" in tokens
        tiene_sgr = "SGR" in tokens or "REGALIA" in tokens or "REGALIAS" in tokens
        tiene_nacion = "NACION" in tokens
        tiene_otros = "OTROS" in tokens

        tiene_propio = (
            "PROPIOS" in tokens
            or "RECURSOS PROPIOS" in t
            or any(
                p in tokens
                for p in [
                    "DEPARTAMENTALES",
                    "MUNICIPALES",
                    "MIXTOS",
                    "EMPRESTITOS",
                ]
            )
        )

        # =========================
        # 🔥 4. REGLAS DEFINITIVAS
        # =========================

        # 1. SGR manda sobre todo
        if tiene_sgr:
            if tiene_propio:
                return "RECURSOS PROPIOS / NACION SGR"
            return "NACION SGR"

        # 2. SGP manda
        if tiene_sgp:
            if tiene_propio:
                return "RECURSOS PROPIOS / NACION SGP"
            return "NACION SGP"

        # 3. Nación sin SGP explícito
        if tiene_nacion:
            if tiene_propio:
                return "RECURSOS PROPIOS / NACION SGP"
            return "NACION SGP"

        # 4. Otros (solo si no hay nada más fuerte)
        if tiene_otros:
            if tiene_propio:
                return "RECURSOS PROPIOS"
            return "OTROS"

        # 5. Solo propios
        if tiene_propio:
            return "RECURSOS PROPIOS"

        return "OTROS"

    df["ORIGEN_RECURSOS_ESTANDAR"] = df["ORIGEN_RECURSOS"].apply(mapeo_profundo)

    return df
