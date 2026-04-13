import pandas as pd
import unicodedata


def limpiar_texto_auditoria(texto, es_cabecera=False):
    # Si es nulo de una vez devolvemos None
    if pd.isna(texto):
        return None

    # Convertimos a string de entrada para no fallar con los NIT numéricos
    texto = str(texto).strip()

    # Si después de convertir a string está vacío
    if texto == "":
        return None

    # El resto de tu lógica de limpieza (Ñ, tildes, etc.)
    texto = texto.replace("Ñ", "NH").replace("ñ", "nh")
    texto = (
        unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode("utf-8")
    )
    texto = texto.replace("NH", "N").upper().strip()

    if es_cabecera:
        return texto.replace(" ", "_").replace(".", "_").replace("__", "_")

    return texto


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


def estandarizar_modalidades(df):
    """
    Estandariza la columna MODALIDAD_CONTRATACION según las reglas de auditoría.
    """
    if "MODALIDAD_CONTRATACION" not in df.columns:
        return df

    # Definimos las reglas de la imagen
    mapeo = {
        "SIN_OFERTAS": "REGIMEN_ESPECIAL",
        "CON_OFERTAS": "REGIMEN_ESPECIAL",
        "INVITACION_DIRECTA": "INVITACION_CERRADA",
        "ACUERDOS_MARCO_DE_PRECIOS": "CONTRATACION_DIRECTA",
        "INVITACION_PUBLICA": "LICITACIONES_PUBLICAS",
        "CONTRATACION_CON_ENTIDADES_PRIVADAS_SIN_ANIMO_DE_LUCRO_A_LA_QUE_HACE_REFERENCIA_EL_ART_355_CP": "CONTRATACION_DIRECTA",
    }

    # IMPORTANTE: Como ya pasamos el limpiador de texto (acentos, espacios, etc.)
    # debemos asegurarnos que las llaves del diccionario coincidan con el texto limpio.

    # Aplicamos la transformación
    df["MODALIDAD_ESTANDAR"] = df["MODALIDAD_CONTRATACION"].replace(mapeo)

    return df


def estandarizar_causales(df):
    """
    Estandariza la columna CAUSAL_CONTRATO según la tabla de equivalencias de la imagen.
    """
    if "CAUSAL_CONTRATO" not in df.columns:
        return df

    # Diccionario de equivalencias (Mapeo de Causales)
    mapeo_causales = {
        # Licitación y Subasta
        "SUBASTA_INVERSA_LICITACION_PUBLICA": "LICITACION_PUBLICA",
        "ADQUISICION_O_SUMINISTRO_DE_BIENES_Y_SERVICIOS_DE_CARACTERISTICAS_TECNICAS_UNIFORMES": "SUBASTA_INVERSA",
        # Tienda Virtual / Acuerdos Marco
        "TIENDA_VIRTUAL_DEL_ESTADO": "ACUERDO_MARCO_DE_PRECIOS",
        "TIENDA_VIRTUAL_DEL_ESTADO_COLOMBIANO": "ACUERDO_MARCO_DE_PRECIOS",
        # Interadministrativos
        "CONVENIOS_INTERADMINISTRATIVOS": "CONTRATOS_INTERADMINISTRATIVOS",
        "CONVENIOS_DE_COOPERACION_INTERINTERISTITUCIONAL": "CONTRATOS_INTERADMINISTRATIVOS",
        # Artículo 355 (ESAL)
        "CONVENIOS_DE_ASOCIACION_ESAL": "AQUELLOS_DE_LOS_QUE_TRATA_EL_ARTICULO_355_DE_LA_CONSTITUCION_POLITICA_DE_COLOMBIA",
        "SELECCION_CUANDO_HAY_MAS_DE_UNA_ESAL": "AQUELLOS_DE_LOS_QUE_TRATA_EL_ARTICULO_355_DE_LA_CONSTITUCION_POLITICA_DE_COLOMBIA",
        # Prestación de servicios
        "PRESTACION_DE_SERVICIOS_(SE_ELIMINARA)": "PRESTACION_DE_SERVICIOS_PROFESIONALES_Y_APOYO",
        # Otros y Manual
        "SIN_PLURALIDAD_DE_OFERENTES": "MANUAL_DE_CONTRATACION",
        "DESARROLLO_ACTIVIDAD_CIENTIFICA_Y_TECNOLOGICA": "OTRAS_FORMAS_DE_CONTRATACION_DIRECTA",
        "ABIERTO": "OTROS",
        "MANUAL_DE_CONTRATACION": "MANUAL_DE_CONTRATACION",
        "MANUAL_DE_CONTRATACION": "MANUAL_DE_CONTRATACION",  # Doble entrada por seguridad
        # Suministros
        "ORDEN_DE_COMPRA": "SUMINISTROS",
        "ORDEN_DE_SERVICIO": "SUMINISTROS",
    }

    # Aplicamos el reemplazo creando una columna nueva para auditoría
    df["CAUSAL_ESTANDAR"] = df["CAUSAL_CONTRATO"].replace(mapeo_causales)

    return df


def estandarizar_recursos_v2(df):
    if "ORIGEN_RECURSOS" not in df.columns:
        return df

    def mapeo_profundo(texto):
        if pd.isna(texto):
            return "NO REPORTADO"
        t = str(texto).upper().strip()

        # Identificadores clave
        tiene_sgp = "SGP" in t
        tiene_sgr = "SGR" in t or "REGALIAS" in t
        tiene_nacion = "NACION" in t and not (tiene_sgp or tiene_sgr)

        # Fuentes locales/propias
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

        # --- LÓGICA DE JERARQUÍA ---

        # 1. MEZCLAS CON SGP
        if tiene_sgp and tiene_propio:
            return "RECURSOS PROPIOS / NACION SGP"

        # 2. MEZCLAS CON SGR (Regalías)
        if tiene_sgr and tiene_propio:
            return "RECURSOS PROPIOS / NACION SGR"

        # 3. NACIÓN SGR PURO
        if tiene_sgr:
            return "NACION SGR"

        # 4. NACIÓN SGP PURO (O NACIÓN solo, que suele ser SGP en estos reportes)
        if tiene_sgp or tiene_nacion:
            return "NACION SGP"

        # 5. OTROS
        if "OTROS" in t:
            return "OTROS"

        # 6. POR DEFECTO (PROPIOS)
        return "RECURSOS PROPIOS"

    df["ORIGEN_RECURSOS_ESTANDAR"] = df["ORIGEN_RECURSOS"].apply(mapeo_profundo)
    return df
