"""
Resultados de los modelos del Laboratorio 1 (Lab1/serie_obligatoria_total_mensual.ipynb).

No se construyen modelos nuevos: se reproducen exactamente las tres especificaciones
finales del Lab 1, con la misma división 70 % entrenamiento / 30 % prueba:
    - Holt-Winters: tendencia aditiva, estacionalidad multiplicativa, periodo 12
    - SARIMA(0,1,1)(0,0,1,12) sobre el logaritmo de la serie
    - Ingenuo estacional: repite los últimos 12 meses del entrenamiento
"""

import warnings

import numpy as np
import pandas as pd
import streamlit as st
from sklearn.metrics import mean_absolute_error, mean_squared_error
from statsmodels.tsa.holtwinters import ExponentialSmoothing
from statsmodels.tsa.statespace.sarimax import SARIMAX

from utils.datos import serie_total_mensual

PROPORCION_ENTRENAMIENTO = 0.70


@st.cache_data(show_spinner="Calculando los pronósticos de los modelos del Laboratorio 1…")
def resultados_modelos():
    serie = serie_total_mensual()
    cantidad_entrenamiento = int(len(serie) * PROPORCION_ENTRENAMIENTO)
    serie_entrenamiento = serie.iloc[:cantidad_entrenamiento]
    serie_prueba = serie.iloc[cantidad_entrenamiento:]
    pasos = len(serie_prueba)

    with warnings.catch_warnings():
        warnings.simplefilter("ignore")

        ajuste_hw = ExponentialSmoothing(
            serie_entrenamiento, trend="add", seasonal="mul", seasonal_periods=12
        ).fit()
        prediccion_hw = ajuste_hw.forecast(pasos)

        ajuste_sarima = SARIMAX(
            np.log(serie_entrenamiento),
            order=(0, 1, 1),
            seasonal_order=(0, 0, 1, 12),
            enforce_stationarity=False,
            enforce_invertibility=False,
        ).fit(disp=False)
        pronostico_sarima = ajuste_sarima.get_forecast(steps=pasos)
        prediccion_sarima = np.exp(pronostico_sarima.predicted_mean)
        intervalo_sarima = np.exp(pronostico_sarima.conf_int(alpha=0.05))

    ultimos_12 = serie_entrenamiento.iloc[-12:].to_numpy()
    prediccion_naive = np.tile(ultimos_12, int(np.ceil(pasos / 12)))[:pasos]

    predicciones = pd.DataFrame({
        "real": serie_prueba.to_numpy(),
        "Holt-Winters": np.asarray(prediccion_hw),
        "SARIMA": np.asarray(prediccion_sarima),
        "Ingenuo estacional": prediccion_naive,
        "sarima_inferior": intervalo_sarima.iloc[:, 0].to_numpy(),
        "sarima_superior": intervalo_sarima.iloc[:, 1].to_numpy(),
    }, index=serie_prueba.index)

    filas = []
    for modelo in ["Holt-Winters", "SARIMA", "Ingenuo estacional"]:
        error_absoluto = (predicciones["real"] - predicciones[modelo]).abs()
        filas.append({
            "modelo": modelo,
            "mae": mean_absolute_error(predicciones["real"], predicciones[modelo]),
            "rmse": np.sqrt(mean_squared_error(predicciones["real"], predicciones[modelo])),
            "mape": (error_absoluto / predicciones["real"]).mean() * 100,
        })
    metricas = pd.DataFrame(filas).sort_values("rmse").reset_index(drop=True)

    return serie_entrenamiento, predicciones, metricas

from pathlib import Path  # noqa: E402

RUTA_LSTM = Path(__file__).resolve().parents[1] / "Lab2" / "resultados_lstm_aerea.csv"


@st.cache_data
def resultados_lstm():
    """
    Búsqueda de configuraciones de la red LSTM del Laboratorio 2 (vía aérea): una fila por
    configuración probada, con su error de validación (val_loss, en datos escalados 0–1).
    No se entrena nada aquí: solo se leen los resultados ya guardados.
    """
    return pd.read_csv(RUTA_LSTM)