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
        "SIN_OFERTAS": "REGIMEN_ESPECIAL",
        "CON_OFERTAS": "REGIMEN_ESPECIAL",
        "INVITACION_DIRECTA": "INVITACION_CERRADA",
        "ACUERDOS_MARCO_DE_PRECIOS": "CONTRATACION_DIRECTA",
        "INVITACION_PUBLICA": "LICITACIONES_PUBLICAS",
        "CONTRATACION_CON_ENTIDADES_PRIVADAS_SIN_ANIMO_DE_LUCRO_A_LA_QUE_HACE_REFERENCIA_EL_ART_355_CP": "CONTRATACION_DIRECTA",
    }

    df["MODALIDAD_ESTANDAR"] = df["MODALIDAD_CONTRATACION"].replace(mapeo)

    return df


# Estandariza los valores de la columna 'CAUSAL_CONTRATO' mediante un mapeo
# de categorías homogéneas, generando la columna 'CAUSAL_ESTANDAR' para
# facilitar el análisis, la depuración y la consistencia de los datos.
def estandarizar_causales(df):

    if "CAUSAL_CONTRATO" not in df.columns:
        return df

    mapeo_causales = {
        "SUBASTA_INVERSA_LICITACION_PUBLICA": "LICITACION_PUBLICA",
        "ADQUISICION_O_SUMINISTRO_DE_BIENES_Y_SERVICIOS_DE_CARACTERISTICAS_TECNICAS_UNIFORMES": "SUBASTA_INVERSA",
        "TIENDA_VIRTUAL_DEL_ESTADO": "ACUERDO_MARCO_DE_PRECIOS",
        "TIENDA_VIRTUAL_DEL_ESTADO_COLOMBIANO": "ACUERDO_MARCO_DE_PRECIOS",
        "CONVENIOS_INTERADMINISTRATIVOS": "CONTRATOS_INTERADMINISTRATIVOS",
        "CONVENIOS_DE_COOPERACION_INTERINTERISTITUCIONAL": "CONTRATOS_INTERADMINISTRATIVOS",
        "CONVENIOS_DE_ASOCIACION_ESAL": "AQUELLOS_DE_LOS_QUE_TRATA_EL_ARTICULO_355_DE_LA_CONSTITUCION_POLITICA_DE_COLOMBIA",
        "SELECCION_CUANDO_HAY_MAS_DE_UNA_ESAL": "AQUELLOS_DE_LOS_QUE_TRATA_EL_ARTICULO_355_DE_LA_CONSTITUCION_POLITICA_DE_COLOMBIA",
        "PRESTACION_DE_SERVICIOS_(SE_ELIMINARA)": "PRESTACION_DE_SERVICIOS_PROFESIONALES_Y_APOYO",
        "SIN_PLURALIDAD_DE_OFERENTES": "MANUAL_DE_CONTRATACION",
        "DESARROLLO_ACTIVIDAD_CIENTIFICA_Y_TECNOLOGICA": "OTRAS_FORMAS_DE_CONTRATACION_DIRECTA",
        "ABIERTO": "OTROS",
        "MANUAL_DE_CONTRATACION": "MANUAL_DE_CONTRATACION",
        "MANUAL_DE_CONTRATACION": "MANUAL_DE_CONTRATACION",
        "ORDEN_DE_COMPRA": "SUMINISTROS",
        "ORDEN_DE_SERVICIO": "SUMINISTROS",
    }

    df["CAUSAL_ESTANDAR"] = df["CAUSAL_CONTRATO"].replace(mapeo_causales)

    return df


# Estandariza la columna 'ORIGEN_RECURSOS' aplicando una lógica jerárquica
# para clasificar las fuentes de financiación en categorías homogéneas.
# La función identifica combinaciones de recursos (SGP, SGR, Nación y propios)
# y asigna una clasificación final en 'ORIGEN_RECURSOS_ESTANDAR' para mejorar
# la consistencia y el análisis de los datos.


def estandarizar_recursos_v2(df):
    if "ORIGEN_RECURSOS" not in df.columns:
        return df

    def mapeo_profundo(texto):
        if pd.isna(texto):
            return "NO REPORTADO"
        t = str(texto).upper().strip()

        tiene_sgp = "SGP" in t
        tiene_sgr = "SGR" in t or "REGALIAS" in t
        tiene_nacion = "NACION" in t and not (tiene_sgp or tiene_sgr)

        tiene_propio = any(
            p in t
            for p in [
                "PROPIOS",
                "DEPARTAMENTALES",
                "MUNICIPALES",
                "MIXTOS",
                "EMPRESTITOS",
            ]
        )

        if tiene_sgp and tiene_propio:
            return "RECURSOS PROPIOS / NACION SGP"

        if tiene_sgr and tiene_propio:
            return "RECURSOS PROPIOS / NACION SGR"

        if tiene_sgr:
            return "NACION SGR"

        if tiene_sgp or tiene_nacion:
            return "NACION SGP"

        if "OTROS" in t:
            return "OTROS"

        return "RECURSOS PROPIOS"

    df["ORIGEN_RECURSOS_ESTANDAR"] = df["ORIGEN_RECURSOS"].apply(mapeo_profundo)
    return df
