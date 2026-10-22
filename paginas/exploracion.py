"""
Llegadas y mercados: tres visualizaciones enlazadas.

    V1 (evolución en el tiempo)  --arrastrar un período-->  V2 (regiones)  --clic en región-->  V3 (países)

Cada paso aumenta el nivel de detalle: todo el mundo -> una región -> sus países.
V1 además permite cambiar la granularidad (anual / trimestral / mensual).
"""

import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.datos import (CAMBIO_METODOLOGICO, FIN_PANDEMIA, INICIO_PANDEMIA,
                         TIPOS_COMPARABLES, cargar_datos)
from utils.estilo import (AZUL_OBSERVADO, GRIS_CONTEXTO, TINTA_SECUNDARIA,
                          TINTA_TENUE, encabezado_visualizacion, etiqueta_mes,
                          mostrar_grafica)

datos = cargar_datos()

st.title("Llegadas y mercados de origen")
st.markdown(
    "¿Cuántos visitantes llegan, cuándo y desde dónde? Las tres gráficas de esta "
    "página están **enlazadas**: lo que seleccione en una cambia el detalle de la siguiente."
)

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

# =============================================================================
# V1. Evolución en el tiempo
# =============================================================================
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
fig1.add_annotation(x=CAMBIO_METODOLOGICO, y=1, yref="paper", text="Cambio metodológico",
                    showarrow=False, xanchor="left", yanchor="top",
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
fig1.update_layout(height=380, dragmode="select", showlegend=False,
                   yaxis=dict(title="Visitantes", tickformat="~s", rangemode="tozero"),
                   xaxis=dict(title=None))

evento1 = mostrar_grafica(fig1, key=f"v1_{granularidad}", on_select="rerun",
                          selection_mode="box")

indices = evento1.selection.point_indices if evento1 else []
if indices:
    seleccion = serie.iloc[sorted(indices)]
    inicio, fin = seleccion["fecha"].min(), seleccion["fin"].max()
    texto_periodo = f"{etiqueta_mes(inicio)} – {etiqueta_mes(fin)}"
    st.success(f"Período seleccionado: **{texto_periodo}**. Doble clic en la gráfica para quitar la selección.",
               icon=":material/date_range:")
else:
    inicio, fin = filtrados["fecha"].min(), filtrados["fecha"].max()
    texto_periodo = f"{etiqueta_mes(inicio)} – {etiqueta_mes(fin)}"
    st.caption(f":material/touch_app: Sin selección: se muestra todo el rango filtrado ({texto_periodo}).")

periodo = filtrados[filtrados["fecha"].between(inicio, fin)]

# =============================================================================
# V2 y V3. Regiones -> países
# =============================================================================
st.divider()
col2, col3 = st.columns(2, gap="large")

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
            x=top.values, y=top.index, orientation="h",
            marker=dict(color=AZUL_OBSERVADO),
            customdata=participacion.loc[top.index].values,
            hovertemplate="<b>%{y}</b><br>%{x:,.0f} visitantes<br>"
                          f"%{{customdata:.1f}} % de {titulo_region}<extra></extra>",
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
        if region_elegida is None:
            st.caption(":material/touch_app: Haga clic en una región de la gráfica 2 para filtrar estos países.")
