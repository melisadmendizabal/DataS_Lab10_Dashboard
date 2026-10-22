"""
Pronósticos: resultados de los tres modelos del Laboratorio 1 frente a lo observado.
"""

import plotly.graph_objects as go
import streamlit as st

from utils.estilo import (AQUA_SARIMA, AZUL_OBSERVADO, COLORES_MODELO,
                          ESTILO_LINEA_MODELO, encabezado_visualizacion,
                          etiqueta_mes, mostrar_grafica)
from utils.modelos import resultados_modelos

MODELOS = ["Holt-Winters", "SARIMA", "Ingenuo estacional"]
DESCRIPCION_MODELO = {
    "Holt-Winters": "Suaviza la serie y proyecta su tendencia y su patrón de cada mes.",
    "SARIMA": "Modelo estadístico que usa los valores y errores pasados, incluido el mismo mes del año anterior.",
    "Ingenuo estacional": "Referencia mínima: supone que cada mes se repetirá igual que el último año conocido.",
}

serie_entrenamiento, predicciones, metricas = resultados_modelos()
inicio_prueba = predicciones.index.min()
fin_prueba = predicciones.index.max()

st.title("Pronósticos de modelos")
st.markdown(
    f"Tres modelos aprendieron el comportamiento de las llegadas con datos de "
    f"**{etiqueta_mes(serie_entrenamiento.index.min())} a {etiqueta_mes(serie_entrenamiento.index.max())}**. "
    f"Luego se les pidió estimar los meses de **{etiqueta_mes(inicio_prueba)} a {etiqueta_mes(fin_prueba)}**, "
    "que ellos no conocían, y se compararon sus estimaciones con lo que realmente ocurrió. "
    "Así se puede juzgar qué tan confiables son."
)
st.caption(
    "Los modelos son los mismos del Laboratorio 1 (total mensual de turistas + excursionistas); "
    "no se construyeron modelos nuevos."
)

# =============================================================================
# V4. Estimaciones vs. observado
# =============================================================================
st.divider()
encabezado_visualizacion(
    4, "¿Qué tan cerca estuvieron los modelos de lo que realmente pasó?",
    "La línea azul es lo observado; las demás son las estimaciones de cada modelo para el mismo período.",
    "decidir cuánto confiar en una proyección antes de usarla para planificar presupuesto, "
    "personal o capacidad hotelera.",
)

c1, c2, c3 = st.columns([3, 1.3, 1.3])
elegidos = c1.multiselect("Modelos a mostrar", MODELOS, default=MODELOS,
                          help="\n\n".join(f"**{m}:** {d}" for m, d in DESCRIPCION_MODELO.items()))
ver_historia = c2.toggle("Ver datos de aprendizaje", value=False,
                         help="Muestra también los meses con los que aprendieron los modelos (2009–2021).")
ver_intervalo = c3.toggle("Ver incertidumbre de SARIMA", value=False,
                          help="Rango donde SARIMA espera el valor real con 95 % de probabilidad.",
                          disabled="SARIMA" not in elegidos)

fig4 = go.Figure()
if ver_historia:
    fig4.add_trace(go.Scatter(
        x=serie_entrenamiento.index, y=serie_entrenamiento.values, mode="lines",
        line=dict(color=AZUL_OBSERVADO, width=1.5), opacity=0.45,
        name="Observado (aprendizaje)",
        hovertemplate="%{y:,.0f}<extra>Observado</extra>",
    ))
    fig4.add_vline(x=inicio_prueba, line_width=1, line_color="#898781")
    fig4.add_annotation(x=inicio_prueba, y=1, yref="paper", text="Inicio de la evaluación",
                        showarrow=False, xanchor="left", yanchor="top",
                        font=dict(color="#898781", size=12))

if ver_intervalo and "SARIMA" in elegidos:
    fig4.add_trace(go.Scatter(
        x=list(predicciones.index) + list(predicciones.index[::-1]),
        y=list(predicciones["sarima_superior"]) + list(predicciones["sarima_inferior"][::-1]),
        fill="toself", fillcolor="rgba(27,175,122,0.12)", line=dict(width=0),
        hoverinfo="skip", name="Incertidumbre SARIMA (95 %)",
    ))

for modelo in elegidos:
    fig4.add_trace(go.Scatter(
        x=predicciones.index, y=predicciones[modelo], mode="lines", name=modelo,
        line=dict(color=COLORES_MODELO[modelo], width=2, dash=ESTILO_LINEA_MODELO[modelo]),
        hovertemplate="%{y:,.0f}<extra>" + modelo + "</extra>",
    ))
    # etiqueta directa al final de cada línea
    fig4.add_annotation(x=fin_prueba, y=predicciones[modelo].iloc[-1], text=modelo,
                        showarrow=False, xanchor="left", xshift=6,
                        font=dict(color="#52514e", size=12))

fig4.add_trace(go.Scatter(
    x=predicciones.index, y=predicciones["real"], mode="lines", name="Observado",
    line=dict(color=AZUL_OBSERVADO, width=2.5),
    hovertemplate="<b>%{y:,.0f}</b><extra>Observado</extra>",
))
fig4.update_layout(
    height=450, hovermode="x unified",
    yaxis=dict(title="Visitantes por mes", tickformat="~s", rangemode="tozero"),
    xaxis=dict(title=None, hoverformat="%m/%Y"),
    margin=dict(r=130),
)
mostrar_grafica(fig4, key="v4_pronosticos")

if not elegidos:
    st.info("Seleccione al menos un modelo para comparar sus estimaciones con lo observado.",
            icon=":material/info:")

# -- tabla comparativa (elemento complementario) -------------------------------
st.markdown("##### Comparación de errores")
tabla = metricas.copy()
tabla.insert(0, "posición", range(1, len(tabla) + 1))
st.dataframe(
    tabla, hide_index=True,
    column_config={
        "posición": st.column_config.NumberColumn("Posición", width="small"),
        "modelo": st.column_config.TextColumn("Modelo"),
        "mae": st.column_config.NumberColumn(
            "Error promedio (visitantes/mes)", format="%,.0f",
            help="MAE: en promedio, cuántos visitantes por mes se equivocó el modelo."),
        "rmse": st.column_config.NumberColumn(
            "Error que castiga fallos grandes", format="%,.0f",
            help="RMSE: como el error promedio, pero pesa más los meses con errores grandes."),
        "mape": st.column_config.NumberColumn(
            "Error promedio (%)", format="%.1f %%",
            help="MAPE: error promedio como porcentaje del valor real."),
    },
)

mejor = metricas.iloc[0]
menor_subestimacion = min(
    (predicciones["real"] > predicciones[modelo]).mean() * 100 for modelo in MODELOS
)
izquierda, derecha = st.columns(2, gap="large")
with izquierda:
    st.markdown("**Lo que muestran los datos**")
    st.markdown(
        f"- **{mejor['modelo']}** tuvo el menor error: en promedio se desvió "
        f"{mejor['mae']:,.0f} visitantes por mes ({mejor['mape']:.0f} %).\n"
        f"- Los tres modelos **estimaron menos visitantes de los que llegaron** en al menos "
        f"el {menor_subestimacion:.0f} % de los meses evaluados."
    )
with derecha:
    st.markdown("**Interpretación y limitaciones**")
    st.markdown(
        "- Los modelos aprendieron con datos que terminan en plena pandemia (marzo 2021), "
        "por lo que proyectan niveles bajos; no anticiparon la recuperación.\n"
        "- En 2023 cambió la forma de clasificar a los viajeros, lo que también afecta la comparación.\n"
        "- Úselos como **referencia de orden de magnitud**, no como cifra exacta."
    )
