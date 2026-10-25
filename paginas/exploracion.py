"""
Llegadas y mercados: tres visualizaciones enlazadas.

    V1 (evolución en el tiempo)  --arrastrar un período-->  V2 (regiones)  --clic en región-->  V3 (países)

Cada paso aumenta el nivel de detalle: todo el mundo -> una región -> sus países.
V1 además permite cambiar la granularidad (anual / trimestral / mensual).
El usuario puede ocultar cualquiera de las tres; las demás siguen funcionando
(sin V1 se usa todo el rango filtrado, sin V2 se muestran todas las regiones).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.datos import (CAMBIO_METODOLOGICO, FIN_PANDEMIA, INICIO_PANDEMIA,
                         TIPOS_COMPARABLES, cargar_datos)
from utils.estilo import (AZUL_OBSERVADO, GRIS_CONTEXTO, TINTA_SECUNDARIA,
                          TINTA_TENUE, columnas_visibles, encabezado_visualizacion,
                          etiqueta_mes, etiquetas_cortas, mostrar_grafica,
                          selector_graficas)

datos = cargar_datos()

st.title("Llegadas y mercados de origen")
st.markdown(
    "¿Cuántos visitantes llegan, cuándo y desde dónde? Las tres gráficas de esta "
    "página están **enlazadas**: lo que seleccione en una cambia el detalle de la siguiente."
)
visibles = selector_graficas({
    "v1": "1. Evolución en el tiempo",
    "v2": "2. Regiones de origen",
    "v3": "3. Países",
}, key="graficas_exploracion")

# -- filtros generales (una sola fila, arriba de las gráficas) -----------------
anio_min, anio_max = int(datos["anio"].min()), int(datos["anio"].max())
f1, f2, f3 = st.columns([2, 2, 2])
rango_anios = f1.slider("Años", anio_min, anio_max, (anio_min, anio_max))
tipos = f2.multiselect(
    "Tipo de visitante", sorted(datos["tipo"].cat.categories),
    default=TIPOS_COMPARABLES,
    help="Turista: pernocta al menos una noche. Excursionista: entra y sale el mismo día. "
         "La categoría «Viajero» cambió de definición en 2023, por eso no se incluye por defecto.",
)
vias = f3.multiselect("Vía de ingreso", sorted(datos["via"].cat.categories),
                      default=sorted(datos["via"].cat.categories))

filtrados = datos[
    datos["anio"].between(*rango_anios)
    & datos["tipo"].isin(tipos)
    & datos["via"].isin(vias)
]

if filtrados.empty or filtrados["visitantes"].sum() == 0:
    st.warning(
        "No hay registros para esta combinación de filtros. "
        "Pruebe ampliando el rango de años o agregando tipos de visitante o vías.",
        icon=":material/search_off:",
    )
    st.stop()

if "Viajero" in tipos:
    st.caption(
        ":material/warning: Incluyó la categoría «Viajero»: sus cifras antes y después "
        "de 2023 no son comparables por un cambio metodológico."
    )

# sin selección en V1 (u oculta) se usa todo el rango filtrado
inicio, fin = filtrados["fecha"].min(), filtrados["fecha"].max()

# =============================================================================
# V1. Evolución en el tiempo
# =============================================================================
if "v1" in visibles:
    st.divider()
    encabezado_visualizacion(
        1, "¿Cómo ha evolucionado la llegada de visitantes?",
        "Total de visitantes internacionales por período. Cambie la granularidad para ver "
        "el panorama general (anual) o el detalle mes a mes.",
        "dimensionar la recuperación después de la pandemia y detectar cambios de tendencia. "
        "**Arrastre sobre la gráfica** para elegir un período y ver de dónde vinieron esos visitantes.",
    )

    granularidad = st.segmented_control(
        "Nivel de detalle", ["Anual", "Trimestral", "Mensual"], default="Anual",
        key="granularidad",
    ) or "Anual"

    frecuencia, meses_por_periodo = {"Anual": ("YS", 12), "Trimestral": ("QS", 3),
                                      "Mensual": ("MS", 1)}[granularidad]
    serie = (
        filtrados.groupby("fecha")["visitantes"].sum()
        .resample(frecuencia).agg(["sum", "count"])
        .rename(columns={"sum": "visitantes", "count": "meses"})
    )
    serie = serie[serie["meses"] > 0].reset_index()
    # fin = último mes del período (las fechas siempre son el día 1 del mes)
    serie["fin"] = serie["fecha"] + pd.DateOffset(months=meses_por_periodo - 1)
    serie["incompleto"] = serie["meses"] < meses_por_periodo

    def etiqueta_periodo(fila):
        if frecuencia == "YS":
            texto = str(fila["fecha"].year)
        elif frecuencia == "QS":
            texto = f"T{(fila['fecha'].month - 1) // 3 + 1} {fila['fecha'].year}"
        else:
            texto = etiqueta_mes(fila["fecha"])
        return texto + (" (período incompleto)" if fila["incompleto"] else "")

    serie["etiqueta"] = serie.apply(etiqueta_periodo, axis=1)

    fig1 = go.Figure()
    fig1.add_vrect(x0=INICIO_PANDEMIA, x1=FIN_PANDEMIA, fillcolor=GRIS_CONTEXTO,
                   line_width=0, layer="below",
                   annotation_text="Pandemia", annotation_position="top left",
                   annotation_font=dict(color=TINTA_TENUE, size=12))
    fig1.add_vline(x=CAMBIO_METODOLOGICO, line_width=1, line_dash="dot", line_color=TINTA_TENUE)
    # abajo y a la izquierda de la línea (zona que casi siempre queda libre), para que no se encime con
    # "Pandemia" ni con la serie, ni se corte el texto en pantallas angostas
    fig1.add_annotation(x=CAMBIO_METODOLOGICO, y=0.02, yref="paper", text="Cambio metodológico",
                        showarrow=False, xanchor="right", xshift=-4, yanchor="bottom",
                        font=dict(color=TINTA_TENUE, size=12))
    fig1.add_trace(go.Scatter(
        x=serie["fecha"], y=serie["visitantes"],
        mode="lines+markers",
        line=dict(color=AZUL_OBSERVADO, width=2),
        marker=dict(size=5 if frecuencia == "MS" else 8, color=AZUL_OBSERVADO,
                    line=dict(color="#fcfcfb", width=1)),
        customdata=serie[["etiqueta"]],
        hovertemplate="<b>%{customdata[0]}</b><br>%{y:,.0f} visitantes<extra></extra>",
        selected=dict(marker=dict(color=AZUL_OBSERVADO)),
        unselected=dict(marker=dict(opacity=0.25)),
        name="Visitantes",
    ))
    # rango fijo a los datos (medio período de margen) para que el eje no se estire en el celular
    margen = pd.DateOffset(months=max(1, meses_por_periodo // 2))
    fig1.update_layout(height=380, dragmode="select", showlegend=False,
                       yaxis=dict(title="Visitantes", tickformat="~s", rangemode="tozero"),
                       xaxis=dict(title=None, range=[serie["fecha"].min() - margen,
                                                     serie["fecha"].max() + margen]))

    evento1 = mostrar_grafica(fig1, key=f"v1_{granularidad}", on_select="rerun",
                              selection_mode="box")

    indices = evento1.selection.point_indices if evento1 else []
    if indices:
        seleccion = serie.iloc[sorted(indices)]
        inicio, fin = seleccion["fecha"].min(), seleccion["fin"].max()
        st.success(f"Período seleccionado: **{etiqueta_mes(inicio)} – {etiqueta_mes(fin)}**. "
                   "Doble clic en la gráfica para quitar la selección.",
                   icon=":material/date_range:")
    else:
        st.caption(":material/touch_app: Sin selección: se muestra todo el rango filtrado "
                   f"({etiqueta_mes(inicio)} – {etiqueta_mes(fin)}).")

texto_periodo = f"{etiqueta_mes(inicio)} – {etiqueta_mes(fin)}"
periodo = filtrados[filtrados["fecha"].between(inicio, fin)]

# =============================================================================
# V2 y V3. Regiones -> países
# =============================================================================
region_elegida = None
detalle_visible = visibles & {"v2", "v3"}
if detalle_visible:
    st.divider()
    columnas = columnas_visibles(len(detalle_visible))
    col2, col3 = columnas[0], columnas[-1]

if "v2" in visibles:
    with col2:
        encabezado_visualizacion(
            2, "¿De qué regiones del mundo vienen?",
            f"Visitantes por región de residencia, {texto_periodo}.",
            "identificar los mercados que sostienen la demanda y qué tan dependiente es el "
            "destino de pocas regiones. **Haga clic en una barra** para ver sus países.",
        )
        regiones = (
            periodo.groupby("region", observed=True)["visitantes"].sum()
            .loc[lambda s: s > 0].sort_values().reset_index()
        )
        regiones["participacion"] = regiones["visitantes"] / regiones["visitantes"].sum() * 100

        fig2 = go.Figure(go.Bar(
            x=regiones["visitantes"], y=regiones["region"], orientation="h",
            marker=dict(color=AZUL_OBSERVADO),
            text=regiones["participacion"].map(lambda p: f"{p:.1f} %"),
            textposition="outside", textfont=dict(color=TINTA_SECUNDARIA, size=12),
            cliponaxis=False,
            customdata=regiones[["participacion"]],
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} visitantes<br>%{customdata[0]:.1f} % del total<extra></extra>",
            selected=dict(marker=dict(color=AZUL_OBSERVADO)),
            unselected=dict(marker=dict(opacity=0.3)),
        ))
        fig2.update_layout(height=420, clickmode="event+select", dragmode=False,
                           xaxis=dict(title="Visitantes", tickformat="~s", showgrid=True,
                                      gridcolor="#e1e0d9"),
                           yaxis=dict(title=None, showgrid=False),
                           margin=dict(r=60))

        evento2 = mostrar_grafica(fig2, key="v2_regiones", on_select="rerun",
                                  selection_mode="points")
        puntos = evento2.selection.points if evento2 else []
        region_elegida = puntos[0]["y"] if puntos else None

if "v3" in visibles:
    with col3:
        titulo_region = region_elegida if region_elegida else "todas las regiones"
        encabezado_visualizacion(
            3, "¿Qué países lideran?",
            f"Principales países de residencia en **{titulo_region}**, {texto_periodo}.",
            "priorizar mercados concretos para promoción, conectividad aérea o acuerdos.",
        )
        detalle = periodo if region_elegida is None else periodo[periodo["region"] == region_elegida]
        cantidad = st.slider("Cantidad de países a mostrar", 5, 20, 10, key="top_paises")
        paises = (
            detalle.groupby("pais", observed=True)["visitantes"].sum()
            .loc[lambda s: s > 0].sort_values(ascending=False)
        )
        if paises.empty:
            st.info("La región seleccionada no tiene visitantes registrados en este período.",
                    icon=":material/info:")
        else:
            participacion = paises / paises.sum() * 100
            top = paises.head(cantidad).iloc[::-1]
            fig3 = go.Figure(go.Bar(
                x=top.values, y=etiquetas_cortas(top.index), orientation="h",
                marker=dict(color=AZUL_OBSERVADO),
                customdata=list(zip(top.index, participacion.loc[top.index].values)),
                hovertemplate="<b>%{customdata[0]}</b><br>%{x:,.0f} visitantes<br>"
                              f"%{{customdata[1]:.1f}} % de {titulo_region}<extra></extra>",
            ))
            fig3.update_layout(height=max(300, 28 * len(top) + 60),
                               xaxis=dict(title="Visitantes", tickformat="~s", showgrid=True,
                                          gridcolor="#e1e0d9"),
                               yaxis=dict(title=None, showgrid=False))
            mostrar_grafica(fig3, key="v3_paises")
            concentracion = participacion.head(3).sum()
            st.caption(
                f"Los 3 primeros países concentran el **{concentracion:.0f} %** de los visitantes "
                f"de {titulo_region} en el período (dato observado)."
            )
            if region_elegida is None and "v2" in visibles:
                st.caption(":material/touch_app: Haga clic en una región de la gráfica 2 para filtrar estos países.")
            elif "v2" not in visibles:
                st.caption(":material/visibility_off: La gráfica 2 está oculta: se muestran los "
                           "países de todas las regiones. Actívela para filtrar por región.")
