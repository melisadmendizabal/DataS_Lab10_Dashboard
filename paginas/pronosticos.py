"""
Pronósticos: resultados de los tres modelos del Laboratorio 1 frente a lo observado.
"""

import plotly.graph_objects as go
import streamlit as st

from utils.estilo import (AQUA_SARIMA, AZUL_OBSERVADO, COLORES_MODELO,
                          ESTILO_LINEA_MODELO, encabezado_visualizacion,
                          etiqueta_mes, mostrar_grafica, selector_graficas)
from utils.modelos import resultados_modelos


import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from utils.estilo import (CUADRICULA, EJE, GRIS_REFERENCIA, TINTA,  # noqa: E402
                          TINTA_SECUNDARIA, TINTA_TENUE)
from utils.modelos import resultados_lstm  # noqa: E402

# hiperparámetros de la LSTM del Lab 2 que el usuario puede comparar (V10)
HIPERPARAMETROS = {
    "Tasa de aprendizaje": "learning_rate",
    "Meses que mira la red (ventana)": "ventana",
    "Neuronas en la primera capa": "unidades_1",
    "Dropout (apagado aleatorio de neuronas)": "dropout",
    "Tamaño de lote": "batch_size",
    "Arquitectura": "arquitectura",
}
SIMBOLO_ARQUITECTURA = {"LSTM simple": "circle", "LSTM apilada": "diamond"}


def formato_hiperparametro(columna, valor):
    if columna == "learning_rate":
        return f"{valor:g}"
    if columna == "dropout":
        return "Sin dropout" if valor == 0 else f"{valor:.0%}".replace("%", " %")
    if columna == "ventana":
        return f"{int(valor)} meses"
    if columna in ("unidades_1", "batch_size"):
        return str(int(valor))
    return str(valor)



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
visibles = selector_graficas({
    "v4": "4. Estimaciones vs. observado",

    "v9": "9. Error mes a mes",
  
    "tabla": "Comparación de errores",
    
    "v10": "10. Red neuronal (Lab 2)",

}, key="graficas_pronosticos")

# =============================================================================
# V4. Estimaciones vs. observado
# =============================================================================
if "v4" in visibles:
    st.divider()
    encabezado_visualizacion(
        4, "¿Qué tan cerca estuvieron los modelos de lo que realmente pasó?",
        "La línea azul es lo observado; las demás son las estimaciones de cada modelo para el mismo período.",
        "decidir cuánto confiar en una proyección antes de usarla para planificar presupuesto, "
        "personal o capacidad hotelera.",
    )

   
    # columnas y etiqueta ajustadas: "Ver incertidumbre de SARIMA" se cortaba en pantallas medianas
    c1, c2, c3 = st.columns([2.6, 1.4, 1.6])
 
    elegidos = c1.multiselect("Modelos a mostrar", MODELOS, default=MODELOS,
                              help="\n\n".join(f"**{m}:** {d}" for m, d in DESCRIPCION_MODELO.items()))
    ver_historia = c2.toggle("Ver datos de aprendizaje", value=False,
                             help="Muestra también los meses con los que aprendieron los modelos (2009–2021).")
 
    ver_intervalo = c3.toggle("Incertidumbre de SARIMA", value=False,
    
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
        # etiqueta directa al final de cada línea, dentro del área de la gráfica
        # (sin margen extra a la derecha, que en pantallas angostas quita mucho ancho)
        fig4.add_annotation(x=fin_prueba, y=predicciones[modelo].iloc[-1], text=modelo,
                            showarrow=False, xanchor="right", yanchor="bottom", yshift=4,
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
    )
    mostrar_grafica(fig4, key="v4_pronosticos")

    if not elegidos:
        st.info("Seleccione al menos un modelo para comparar sus estimaciones con lo observado.",
                icon=":material/info:")


# =============================================================================
# V9. Error mes a mes de cada modelo (observado − estimado)
# =============================================================================
if "v9" in visibles:
    st.divider()
    encabezado_visualizacion(
        9, "¿En qué meses se equivocaron más los modelos?",
        "Diferencia entre lo observado y lo estimado por cada modelo, mes a mes. Arriba de la "
        "línea de cero el modelo **estimó menos** visitantes de los que llegaron; abajo, **estimó más**.",
        "saber en qué épocas una proyección es menos confiable y si su error crece con el tiempo, "
        "antes de usarla para fijar metas.",
    )
    c1, c2 = st.columns([3, 2])
    if "v4" in visibles:
        # enlazada con V4: muestra los mismos modelos elegidos allí
        modelos_v9 = elegidos
        c1.caption(":material/link: Muestra los mismos modelos elegidos en la gráfica 4.")
    else:
        modelos_v9 = c1.multiselect("Modelos a mostrar", MODELOS, default=MODELOS, key="modelos_v9")
    unidad_error = c2.segmented_control(
        "Mostrar el error en", ["Visitantes", "% del valor real"], default="Visitantes",
        key="unidad_v9",
        help="«% del valor real» compara el error con el tamaño de cada mes: un error de "
             "50 mil pesa más en un mes de 100 mil visitantes que en uno de 300 mil.",
    ) or "Visitantes"

    if not modelos_v9:
        st.info("Seleccione al menos un modelo para ver su error.", icon=":material/info:")
    else:
        errores = predicciones[MODELOS].rsub(predicciones["real"], axis=0)  # observado − estimado
        en_porcentaje = unidad_error == "% del valor real"
        if en_porcentaje:
            errores = errores.div(predicciones["real"], axis=0) * 100
        formato, sufijo = (".0f", " %") if en_porcentaje else (",.0f", "")

        fig9 = go.Figure()
        fig9.add_hline(y=0, line_width=1, line_color=TINTA_TENUE)
        fig9.add_annotation(x=inicio_prueba, y=0, text="Sin error", showarrow=False,
                            xanchor="left", yanchor="top", font=dict(color=TINTA_TENUE, size=12))
        for modelo in modelos_v9:
            fig9.add_trace(go.Scatter(
                x=errores.index, y=errores[modelo], mode="lines", name=modelo,
                line=dict(color=COLORES_MODELO[modelo], width=2, dash=ESTILO_LINEA_MODELO[modelo]),
                hovertemplate=f"%{{y:{formato}}}{sufijo}<extra>{modelo}</extra>",
            ))
        fig9.update_layout(
            height=380, hovermode="x unified",
            yaxis=dict(title="Observado − estimado" + (" (%)" if en_porcentaje else ""),
                       tickformat=".0f" if en_porcentaje else "~s", ticksuffix=sufijo,
                       zeroline=False),
            xaxis=dict(title=None, hoverformat="%m/%Y"),
        )
        mostrar_grafica(fig9, key="v9_errores")

        # -- hallazgos observados ------------------------------------------
        lineas = []
        for modelo in modelos_v9:
            subestimo = (errores[modelo] > 0).mean() * 100
            peor_mes = errores[modelo].abs().idxmax()
            lineas.append(
                f"- **{modelo}** estimó menos de lo observado en el **{subestimo:.0f} %** de los "
                f"meses; su mayor error fue en **{etiqueta_mes(peor_mes)}** "
                f"({errores[modelo][peor_mes]:{formato}}{sufijo})."
            )
        referencia = metricas.iloc[0]["modelo"] if metricas.iloc[0]["modelo"] in modelos_v9 else modelos_v9[0]
        primeros, ultimos = errores[referencia].iloc[:12].abs().mean(), errores[referencia].iloc[-12:].abs().mean()
        lineas.append(
            f"- El error promedio de **{referencia}** pasó de {primeros:{formato}}{sufijo} en los "
            f"primeros 12 meses a {ultimos:{formato}}{sufijo} en los últimos 12."
        )
        st.markdown("**Lo que muestran los datos**")
        st.markdown("\n".join(lineas))
        st.caption(
            ":material/info: Interpretación: es esperable que el error cambie con el tiempo, porque "
            "entre más lejos está un mes del último dato de aprendizaje (marzo 2021), menos "
            "información tiene el modelo sobre él."
        )


# -- tabla comparativa (elemento complementario) -------------------------------
if "tabla" in visibles:
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


# =============================================================================
# V10. Desempeño de las configuraciones de la red neuronal LSTM (Lab 2)
# =============================================================================
if "v10" in visibles:
    st.divider()
    lstm = resultados_lstm()
    encabezado_visualizacion(
        10, "¿Qué configuración de red neuronal aprendió mejor?",
        f"En el Laboratorio 2 se probaron **{len(lstm)} configuraciones** de una red neuronal "
        "(LSTM) para pronosticar la **vía aérea**. Cada punto es una configuración: "
        "**más abajo = menor error** al validar con meses que la red no vio al aprender.",
        "entender qué decisiones de diseño mejoran un modelo y cuánto cambia el resultado según "
        "ellas, antes de invertir en un modelo nuevo. **Haga clic en un punto** para ver su "
        "configuración completa.",
    )
    st.caption(
        ":material/info: Es otro tipo de modelo y otra serie (solo vía aérea). Su error está en "
        "datos escalados de 0 a 1, por eso sirve para comparar configuraciones entre sí, pero no "
        "se puede comparar con los errores en visitantes de las gráficas 4 y 9."
    )
    c1, c2 = st.columns([2, 3])
    comparar_por = c1.selectbox(
        "Comparar por", list(HIPERPARAMETROS), key="lstm_comparar",
        help="Tasa de aprendizaje: qué tan grandes son los ajustes que hace la red en cada paso. "
             "Ventana: cuántos meses anteriores mira para estimar el siguiente. "
             "Dropout: apaga neuronas al azar al aprender para que no memorice. "
             "Tamaño de lote: cuántos ejemplos revisa antes de cada ajuste.",
    )
    opciones_arquitectura = sorted(lstm["arquitectura"].unique())
    arquitecturas = c2.pills(
        "Arquitectura", opciones_arquitectura, selection_mode="multi",
        default=opciones_arquitectura, key="lstm_arquitecturas",
        help="Simple: una capa LSTM. Apilada: dos capas LSTM, una sobre otra.",
    )
    datos_lstm = lstm[lstm["arquitectura"].isin(arquitecturas)]

    if datos_lstm.empty:
        st.info("Seleccione al menos una arquitectura.", icon=":material/info:")
    else:
        columna = HIPERPARAMETROS[comparar_por]
        valores = sorted(datos_lstm[columna].dropna().unique())
        posicion = {valor: i for i, valor in enumerate(valores)}
        # dispersión horizontal fija (semilla) para que los puntos no se encimen
        desplazamiento = pd.Series(np.random.default_rng(0).uniform(-0.18, 0.18, len(lstm)),
                                   index=lstm.index)

        def resumen_configuracion(fila):
            capas = (f"{int(fila.unidades_1)} neuronas" if pd.isna(fila.unidades_2)
                     else f"{int(fila.unidades_1)} + {int(fila.unidades_2)} neuronas")
            return (f"{fila.arquitectura}, {capas}, ventana de {int(fila.ventana)} meses, "
                    f"dropout {fila.dropout:g}, tasa {fila.learning_rate:g}, lote {int(fila.batch_size)}")

        def texto_configuracion(fila):
            return f"{resumen_configuracion(fila)}<br>error de validación: {fila.val_loss:.4f}"

        fig10 = go.Figure()
        # caja de fondo por valor: mediana y rango central de los errores
        for valor in valores:
            grupo = datos_lstm.loc[datos_lstm[columna] == valor, "val_loss"]
            fig10.add_trace(go.Box(
                x=[posicion[valor]] * len(grupo), y=grupo, boxpoints=False, width=0.55,
                fillcolor="rgba(0,0,0,0)", line=dict(color=EJE, width=1.5),
                hoverinfo="skip", showlegend=False,
            ))
        trazas_lstm = []  # filas de cada traza de puntos, en orden (para leer el clic)
        for arquitectura in arquitecturas:
            sub = datos_lstm[(datos_lstm["arquitectura"] == arquitectura) & datos_lstm[columna].notna()]
            fig10.add_trace(go.Scatter(
                x=sub[columna].map(posicion) + desplazamiento[sub.index], y=sub["val_loss"],
                mode="markers", name=arquitectura,
                marker=dict(symbol=SIMBOLO_ARQUITECTURA.get(arquitectura, "circle"), size=8,
                            color=GRIS_REFERENCIA, opacity=0.75,
                            line=dict(color="#fcfcfb", width=1)),
                text=[texto_configuracion(f) for f in sub.itertuples()],
                hovertemplate="%{text}<extra></extra>",
                selected=dict(marker=dict(color=TINTA, opacity=1)),
                unselected=dict(marker=dict(opacity=0.35)),
            ))
            trazas_lstm.append(sub)
        mejor_lstm = datos_lstm.loc[datos_lstm["val_loss"].idxmin()]
        if pd.notna(mejor_lstm[columna]):
            fig10.add_trace(go.Scatter(
                x=[posicion[mejor_lstm[columna]] + desplazamiento[mejor_lstm.name]],
                y=[mejor_lstm["val_loss"]], mode="markers", name="Mejor configuración",
                marker=dict(symbol="star", size=16, color=TINTA, line=dict(color="#fcfcfb", width=1)),
                hoverinfo="skip",
            ))
        fig10.update_layout(
            height=420, clickmode="event+select", dragmode=False,
            xaxis=dict(title=comparar_por, tickmode="array", tickvals=list(range(len(valores))),
                       ticktext=[formato_hiperparametro(columna, v) for v in valores],
                       range=[-0.6, len(valores) - 0.4]),
            yaxis=dict(title="Error de validación (menor es mejor)", rangemode="tozero",
                       gridcolor=CUADRICULA, tickformat=".2f"),
        )
        evento10 = mostrar_grafica(fig10, key="v10_lstm", on_select="rerun", selection_mode="points")

        # -- detalle bajo demanda: la configuración del punto elegido ---------
        puntos = evento10.selection.points if evento10 else []
        curva = puntos[0].get("curve_number", -1) - len(valores) if puntos else -1
        if 0 <= curva < len(trazas_lstm):
            fila = trazas_lstm[curva].iloc[puntos[0]["point_index"]]
            st.markdown("**Configuración seleccionada**")
            st.dataframe(pd.DataFrame([{
                "Arquitectura": fila["arquitectura"],
                "Neuronas": (f"{int(fila['unidades_1'])}" if pd.isna(fila["unidades_2"])
                             else f"{int(fila['unidades_1'])} + {int(fila['unidades_2'])}"),
                "Ventana (meses)": int(fila["ventana"]),
                "Dropout": fila["dropout"],
                "Tasa de aprendizaje": fila["learning_rate"],
                "Tamaño de lote": int(fila["batch_size"]),
                "Épocas usadas": int(fila["epocas_utilizadas"]),
                "Error de validación": round(fila["val_loss"], 4),
                "Posición (de menor a mayor error)": int((datos_lstm["val_loss"] < fila["val_loss"]).sum() + 1),
            }]), hide_index=True)
        else:
            st.caption(":material/touch_app: Haga clic en un punto para ver su configuración completa.")

        # -- hallazgos observados ------------------------------------------
        medianas = datos_lstm.groupby(columna)["val_loss"].median()
        st.markdown("**Lo que muestran los datos**")
        st.markdown("\n".join([
            f"- La mejor configuración fue **{resumen_configuracion(mejor_lstm)}**, "
            f"con error {mejor_lstm['val_loss']:.3f}.",
            "- Error mediano según " + comparar_por.lower() + ": " + " · ".join(
                f"{formato_hiperparametro(columna, v)}: **{m:.3f}**" for v, m in medianas.items()) + ".",
            f"- La peor configuración tuvo un error **{datos_lstm['val_loss'].max() / mejor_lstm['val_loss']:.1f} veces** "
            "mayor que la mejor.",
        ]))
        st.caption(
            ":material/info: Cada configuración se entrenó una sola vez; diferencias pequeñas entre "
            "grupos pueden deberse al azar del entrenamiento y no a la decisión comparada."
        )
