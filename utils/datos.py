"""
Carga y preparación de la base de migración (la misma usada en los Laboratorios 1 y 2).
"""

from pathlib import Path

import pandas as pd
import streamlit as st

RUTA_DATOS = Path(__file__).resolve().parents[1] / "Lab1" / "migracion_guatemala_2009_2026.csv"

# Según las notas de la base, la categoría "Viajero" cambió de forma fuerte entre 2022 y 2023,
# por eso la serie comparable de todo el período usa solo Turista + Excursionista (igual que en Lab 1).
TIPOS_COMPARABLES = ["Turista", "Excursionista"]
INICIO_PANDEMIA = pd.Timestamp("2020-03-01")
FIN_PANDEMIA = pd.Timestamp("2021-12-01")
CAMBIO_METODOLOGICO = pd.Timestamp("2023-01-01")


@st.cache_data(show_spinner="Cargando datos de migración…")
def cargar_datos():
    datos = pd.read_csv(RUTA_DATOS, encoding="utf-8-sig")

    datos = datos.rename(columns={
        "Año": "anio",
        "Mes cod": "mes",
        "Vía": "via",
        "Frontera": "frontera",
        "País": "pais",
        "Región dos": "region",
        "Tipo de Viajero": "tipo",
        "Viajero": "visitantes",
    })

    datos["fecha"] = pd.to_datetime(
        {"year": datos["anio"], "month": datos["mes"], "day": 1}
    )
    datos["region"] = datos["region"].replace({
        "0": "Sin clasificar",
        "Cruceristas": "Cruceros",
    })
    # "01 La Aurora" -> "La Aurora"
    datos["frontera"] = datos["frontera"].str.replace(r"^\d+\s+", "", regex=True)

    columnas = ["fecha", "anio", "mes", "via", "frontera", "pais", "region", "tipo", "visitantes"]
    datos = datos[columnas]
    for columna in ["via", "frontera", "pais", "region", "tipo"]:
        datos[columna] = datos[columna].astype("category")

    return datos


@st.cache_data
def serie_total_mensual():
    """Total mensual de turistas + excursionistas (serie obligatoria del Lab 1)."""
    datos = cargar_datos()
    serie = (
        datos[datos["tipo"].isin(TIPOS_COMPARABLES)]
        .groupby("fecha")["visitantes"]
        .sum()
        .sort_index()
        .asfreq("MS")
    )
    serie.name = "total_mensual"
    return serie


def ultimo_anio_completo(datos):
    meses_por_anio = datos.groupby("anio")["mes"].nunique()
    return int(meses_por_anio[meses_por_anio == 12].index.max())
