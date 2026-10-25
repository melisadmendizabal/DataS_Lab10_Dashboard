"""
Vías de ingreso y puestos fronterizos: dos visualizaciones enlazadas.

    V7 (visitantes por vía, paneles pequeños)  --clic en un punto-->  V8 (puestos de esa vía)

V7 compara las tres vías con la misma escala (o la propia de cada vía, para ver la forma
de las pequeñas). Al hacer clic en un punto, V8 baja al detalle de los puestos fronterizos
de esa vía en ese período. Si el usuario oculta V7, V8 muestra un selector de vía.
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

from utils.datos import TIPOS_COMPARABLES, cargar_datos
from utils.estilo import (AZUL_OBSERVADO, CUADRICULA, TINTA, TINTA_SECUNDARIA,
                          columnas_visibles, encabezado_visualizacion, etiqueta_mes,
                          etiquetas_cortas, mostrar_grafica, selector_graficas)

datos = cargar_datos()

st.title("Vías de ingreso y puestos fronterizos")
st.markdown(
    "¿Por dónde entran los visitantes: aeropuertos, fronteras terrestres o puertos? Las dos "
    "gráficas de esta página están **enlazadas**: al hacer clic en un punto de la primera, la "
    "segunda muestra los puestos de esa vía en ese período."
)
visibles = selector_graficas({
    "v7": "7. Vías de ingreso",
    "v8": "8. Puestos fronterizos",
}, key="graficas_vias")

# -- filtros generales (una sola fila, arriba de las gráficas) -----------------
anio_min, anio_max = int(datos["anio"].min()), int(datos["anio"].max())
f1, f2 = st.columns(2)
rango_anios = f1.slider("Años", anio_min, anio_max, (anio_min, anio_max), key="anios_vias")
tipos = f2.multiselect(
    "Tipo de visitante", sorted(datos["tipo"].cat.categories),
    default=TIPOS_COMPARABLES, key="tipos_vias",
    help="Turista: pernocta al menos una noche. Excursionista: entra y sale el mismo día. "
         "Crucerista: pasajero de crucero que desembarca por el día (registrado hasta 2022). "
         "La categoría «Viajero» cambió de definición en 2023, por eso no se incluye por defecto.",
)

filtrados = datos[datos["anio"].between(*rango_anios) & datos["tipo"].isin(tipos)]

if filtrados.empty or filtrados["visitantes"].sum() == 0:
    st.warning(
        "No hay registros para esta combinación de filtros. "
        "Pruebe ampliando el rango de años o agregando tipos de visitante.",
        icon=":material/search_off:",
    )
    st.stop()

if "Viajero" in tipos:
    st.caption(
        ":material/warning: Incluyó la categoría «Viajero»: sus cifras antes y después "
        "de 2023 no son comparables por un cambio metodológico."
    )

VIAS = sorted(datos["via"].cat.categories)
meses_por_anio = datos.groupby("anio")["mes"].nunique()

# sin clic en V7 (u oculta) se usan todas las vías y todo el rango filtrado
via_elegida, periodo_elegido = None, None
inicio, fin = filtrados["fecha"].min(), filtrados["fecha"].max()

st.divider()
columnas = columnas_visibles(len(visibles), proporciones=[1.2, 1])
col7, col8 = columnas[0], columnas[-1]

# =============================================================================
# V7. Visitantes por vía de ingreso (paneles pequeños)
# =============================================================================
if "v7" in visibles:
    with col7:
        encabezado_visualizacion(
            7, "¿Por dónde ingresan los visitantes?",
            "Visitantes por vía de ingreso, un panel por vía. Con la misma escala, la altura "
            "de cada panel se puede comparar directamente.",
            "dimensionar la demanda sobre aeropuertos, fronteras terrestres y puertos, y ver qué "
            "vía se recuperó después de la pandemia. **Haga clic en un punto** para ver los "
            "puestos de esa vía en ese período.",
        )
        # un control por línea: lado a lado se cortan en esta columna angosta
        granularidad = st.segmented_control(
            "Nivel de detalle", ["Anual", "Mensual"], default="Anual", key="granularidad_vias",
        ) or "Anual"
        escala = st.segmented_control(
            "Escala", ["Misma para todas", "Propia de cada vía"], default="Misma para todas",
            key="escala_vias",
            help="«Misma para todas» compara el tamaño de las vías. «Propia de cada vía» amplía "
                 "las vías pequeñas (como la marítima) para ver su forma, pero entonces las "
                 "alturas de los paneles ya no se comparan entre sí.",
        ) or "Misma para todas"
        anual = granularidad == "Anual"

        series = {}
        for via in VIAS:
            serie = filtrados[filtrados["via"] == via].groupby("fecha")["visitantes"].sum()
            if anual:
                serie = serie.resample("YS").sum(min_count=1)
            serie = serie.dropna().reset_index()
            if anual:
                incompleto = serie["fecha"].dt.year.map(meses_por_anio) < 12
                serie["etiqueta"] = serie["fecha"].dt.year.astype(str).where(
                    ~incompleto, serie["fecha"].dt.year.astype(str) + " (año incompleto)")
            else:
                serie["etiqueta"] = serie["fecha"].map(etiqueta_mes)
            series[via] = serie

        fig7 = make_subplots(rows=len(VIAS), cols=1, shared_xaxes=True,
                             vertical_spacing=0.09, subplot_titles=VIAS)
        trazas = []  # vía de cada traza, en orden (para leer el clic)
        for fila, via in enumerate(VIAS, start=1):
            serie = series[via]
            if serie.empty:
                fig7.add_annotation(text="Sin registros con estos filtros", showarrow=False,
                                    x=0.5, y=0.5, xref="x domain", yref="y domain",
                                    font=dict(color=TINTA_SECUNDARIA, size=12), row=fila, col=1)
                continue
            fig7.add_trace(go.Scatter(
                x=serie["fecha"], y=serie["visitantes"], mode="lines+markers", name=via,
                fill="tozeroy", fillcolor="rgba(42,120,214,0.12)",
                line=dict(color=AZUL_OBSERVADO, width=2),
                marker=dict(size=7 if anual else 4, color=AZUL_OBSERVADO,
                            line=dict(color="#fcfcfb", width=1)),
                customdata=serie[["etiqueta"]],
                hovertemplate=f"<b>{via}</b> · %{{customdata[0]}}<br>%{{y:,.0f}} visitantes<extra></extra>",
                selected=dict(marker=dict(color=AZUL_OBSERVADO)),
                unselected=dict(marker=dict(opacity=0.25)),
                showlegend=False,
            ), row=fila, col=1)
            trazas.append(via)

        maximo = max((s["visitantes"].max() for s in series.values() if not s.empty), default=0)
        if escala == "Misma para todas":
            fig7.update_yaxes(range=[0, maximo * 1.1])
        else:
            fig7.update_yaxes(rangemode="tozero")
        fig7.update_yaxes(tickformat="~s", gridcolor=CUADRICULA, nticks=4)
        fig7.update_annotations(font=dict(color=TINTA, size=13))
        fig7.update_layout(height=190 * len(VIAS) + 40, clickmode="event+select",
                           dragmode=False, showlegend=False, margin=dict(t=40))

        evento7 = mostrar_grafica(fig7, key=f"v7_{granularidad}", on_select="rerun",
                                  selection_mode="points")
        puntos = evento7.selection.points if evento7 else []
        if puntos and puntos[0].get("curve_number") is not None and puntos[0]["curve_number"] < len(trazas):
            via_elegida = trazas[puntos[0]["curve_number"]]
            punto = series[via_elegida].iloc[puntos[0]["point_index"]]
            inicio_p = punto["fecha"]
            fin_p = inicio_p + pd.DateOffset(months=11) if anual else inicio_p
            periodo_elegido = (inicio_p, fin_p, punto["etiqueta"])
            st.success(f"Seleccionó **{via_elegida} · {punto['etiqueta']}**. "
                       "Doble clic en la gráfica para quitar la selección.",
                       icon=":material/touch_app:")
        else:
            st.caption(":material/touch_app: Sin selección: la gráfica 8 muestra todas las vías.")

        # -- hallazgos observados ----------------------------------------------
        por_via = filtrados.groupby("via", observed=True)["visitantes"].sum()
        participacion = (por_via / por_via.sum() * 100).sort_values(ascending=False)
        st.caption(
            "En el período filtrado: " + " · ".join(
                f"**{via}** {valor:.1f} %" for via, valor in participacion.items()
            ) + " de los visitantes (dato observado)."
        )
        for via in VIAS:
            ultima = filtrados.loc[filtrados["via"] == via, "fecha"].max()
            if pd.notna(ultima) and ultima < fin - pd.DateOffset(months=11):
                st.caption(
                    f":material/info: {via}: no hay registros después de {etiqueta_mes(ultima)} "
                    "con los tipos de visitante elegidos. Pruebe agregando otros tipos "
                    "(por ejemplo, «Cruceristas» para la vía marítima)."
                )

# =============================================================================
# V8. Principales puestos fronterizos de la vía elegida
# =============================================================================
if "v8" in visibles:
    with col8:
        encabezado_visualizacion(
            8, "¿Qué puestos fronterizos reciben más visitantes?",
            "Visitantes por puesto de ingreso (aeropuerto, frontera terrestre o puerto) de la "
            "vía elegida en la gráfica 7.",
            "priorizar inversión en infraestructura, personal migratorio y servicios turísticos "
            "en los puntos de entrada más usados.",
        )
        if "v7" not in visibles:
            # sin la gráfica 7 no hay clic: la vía se elige aquí
            opcion = st.selectbox("Vía de ingreso", ["Todas las vías"] + VIAS, key="via_v8",
                                  help="Active la gráfica 7 para elegir la vía con un clic.")
            via_elegida = None if opcion == "Todas las vías" else opcion

        if periodo_elegido is not None:
            alcance = st.segmented_control(
                "Período de los puestos", ["Solo el período elegido", "Todo el rango de años"],
                default="Solo el período elegido", key="alcance_vias",
            ) or "Solo el período elegido"
            if alcance == "Solo el período elegido":
                inicio, fin = periodo_elegido[0], periodo_elegido[1]
        cantidad = st.slider("Cantidad de puestos a mostrar", 5, 15, 10, key="top_puestos")

        nombre_via = via_elegida if via_elegida else "todas las vías"
        texto_periodo = (periodo_elegido[2] if periodo_elegido is not None and
                         (inicio, fin) == periodo_elegido[:2]
                         else f"{etiqueta_mes(inicio)} – {etiqueta_mes(fin)}")
        st.markdown(f"Mostrando: **{nombre_via}**, {texto_periodo}.")

        detalle = filtrados[filtrados["fecha"].between(inicio, fin)]
        if via_elegida is not None:
            detalle = detalle[detalle["via"] == via_elegida]
        puestos = (
            detalle.groupby("frontera", observed=True)["visitantes"].sum()
            .loc[lambda s: s > 0].sort_values(ascending=False)
        )
        if puestos.empty:
            st.info(
                "No hay visitantes registrados para esta vía en el período elegido. "
                "Pruebe con otro período o agregue tipos de visitante.",
                icon=":material/info:",
            )
        else:
            participacion = puestos / puestos.sum() * 100
            top = puestos.head(cantidad).iloc[::-1]
            fig8 = go.Figure(go.Bar(
                x=top.values, y=etiquetas_cortas(top.index), orientation="h",
                marker=dict(color=AZUL_OBSERVADO),
                text=participacion.loc[top.index].map(lambda p: f"{p:.1f} %"),
                textposition="outside", textfont=dict(color=TINTA_SECUNDARIA, size=12),
                cliponaxis=False,
                customdata=list(zip(top.index, participacion.loc[top.index].values)),
                hovertemplate="<b>%{customdata[0]}</b><br>%{x:,.0f} visitantes<br>"
                              f"%{{customdata[1]:.1f}} % de {nombre_via}<extra></extra>",
            ))
            fig8.update_layout(height=max(260, 34 * len(top) + 80),
                               xaxis=dict(title="Visitantes", tickformat="~s", showgrid=True,
                                          gridcolor=CUADRICULA),
                               yaxis=dict(title=None, showgrid=False),
                               margin=dict(r=60))
            mostrar_grafica(fig8, key="v8_puestos")

            principal = participacion.index[0]
            st.markdown("**Lo que muestran los datos**")
            lineas = [f"- **{principal}** recibió el **{participacion.iloc[0]:.0f} %** de los "
                      f"visitantes de {nombre_via} en el período."]
            if len(puestos) > 3:
                lineas.append(f"- Los 3 primeros puestos suman el "
                              f"**{participacion.head(3).sum():.0f} %**.")
            lineas.append(f"- Puestos con visitantes registrados: **{len(puestos)}**.")
            st.markdown("\n".join(lineas))
            st.caption(
                ":material/info: Muestra cuántos visitantes entraron por cada puesto, no la "
                "capacidad del puesto ni las razones de esa concentración."
            )
            if via_elegida is None and "v7" in visibles:
                st.caption(":material/touch_app: Haga clic en un punto de la gráfica 7 para "
                           "ver los puestos de una sola vía.")