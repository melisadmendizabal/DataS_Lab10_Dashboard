"""
Estacionalidad: dos visualizaciones enlazadas.

    V5 (mapa de calor año × mes)  --clic en una celda-->  V6 (perfil mensual de ese año)

V5 da la vista general de todos los años; V6 baja al detalle de un año y lo compara
con una referencia (promedio prepandemia o año anterior). Si el usuario oculta V5,
V6 muestra un selector de año en su lugar.

Nota técnica: Streamlit no devuelve los clics de un go.Heatmap, por eso encima del mapa
hay una capa de puntos transparentes (uno por celda) que recibe el clic y el tooltip.
La figura de V5 no debe cambiar según su propia selección: si cambia, Streamlit la
trata como un gráfico nuevo y borra la selección.
"""

import numpy as np
import pandas as pd
import plotly.graph_objects as go
import streamlit as st

from utils.datos import TIPOS_COMPARABLES, cargar_datos, ultimo_anio_completo
from utils.estilo import (AZUL_OBSERVADO, CUADRICULA, ESCALA_AZUL, GRIS_REFERENCIA,
                          MESES_ES, TINTA, columnas_visibles, encabezado_visualizacion,
                          mostrar_grafica, selector_graficas)

INICIO_REFERENCIA, FIN_REFERENCIA = 2009, 2019
MESES = list(range(1, 13))

datos = cargar_datos()

st.title("Estacionalidad de la demanda")
st.markdown(
    "¿En qué meses llegan más visitantes y se repite ese patrón cada año? Las dos gráficas "
    "de esta página están **enlazadas**: al hacer clic en el mapa, la segunda gráfica muestra "
    "ese año mes a mes."
)
visibles = selector_graficas({
    "v5": "5. Mapa de temporadas",
    "v6": "6. Detalle de un año",
}, key="graficas_estacionalidad")

# -- filtros generales (una sola fila, arriba de las gráficas) -----------------
f1, f2, f3 = st.columns(3)
tipos = f1.multiselect(
    "Tipo de visitante", sorted(datos["tipo"].cat.categories),
    default=TIPOS_COMPARABLES, key="tipos_estacionalidad",
    help="Turista: pernocta al menos una noche. Excursionista: entra y sale el mismo día. "
         "La categoría «Viajero» cambió de definición en 2023, por eso no se incluye por defecto.",
)
vias = f2.multiselect("Vía de ingreso", sorted(datos["via"].cat.categories),
                      default=sorted(datos["via"].cat.categories), key="vias_estacionalidad")
modo = f3.segmented_control(
    "Mostrar como", ["Visitantes", "% del año"], default="Visitantes",
    key="modo_estacionalidad",
    help="«% del año» indica qué parte de los visitantes de cada año llegó en cada mes. "
         "Así se comparan años de tamaño muy distinto (por ejemplo, los de la pandemia). "
         "2026 no aparece en este modo porque solo tiene enero a junio.",
) or "Visitantes"

filtrados = datos[datos["tipo"].isin(tipos) & datos["via"].isin(vias)]

if filtrados.empty or filtrados["visitantes"].sum() == 0:
    st.warning(
        "No hay registros para esta combinación de filtros. "
        "Pruebe agregando tipos de visitante o vías.",
        icon=":material/search_off:",
    )
    st.stop()

if "Viajero" in tipos:
    st.caption(
        ":material/warning: Incluyó la categoría «Viajero»: sus cifras antes y después "
        "de 2023 no son comparables por un cambio metodológico."
    )

# -- cuadrícula año × mes ------------------------------------------------------
# Los meses que existen en la base pero no tienen visitantes con estos filtros valen 0;
# los meses que la base todavía no cubre (jul–dic 2026) quedan vacíos.
anios = sorted(datos["anio"].unique())
cuadricula = pd.MultiIndex.from_product([anios, MESES], names=["anio", "mes"])
meses_en_base = pd.MultiIndex.from_frame(datos[["anio", "mes"]].drop_duplicates())
celdas = (
    filtrados.groupby(["anio", "mes"])["visitantes"].sum()
    .reindex(meses_en_base, fill_value=0)
    .reindex(cuadricula)
    .rename("visitantes")
    .reset_index()
)
anios_completos = celdas.groupby("anio")["visitantes"].count().loc[lambda s: s == 12].index
total_anio = celdas.groupby("anio")["visitantes"].transform("sum")
celdas["participacion"] = np.where(
    celdas["anio"].isin(anios_completos) & (total_anio > 0),
    celdas["visitantes"] / total_anio * 100, np.nan,
)


def texto_celda(anio, mes, visitantes, participacion):
    encabezado = f"<b>{MESES_ES[mes - 1]} {anio}</b>"
    if pd.isna(visitantes):
        return f"{encabezado}<br>Sin datos: la base llega a junio de 2026"
    texto = f"{encabezado}<br>{visitantes:,.0f} visitantes"
    if pd.notna(participacion):
        texto += f"<br>{participacion:.1f} % de los visitantes del año"
    return texto


celdas["texto"] = [
    texto_celda(fila.anio, fila.mes, fila.visitantes, fila.participacion)
    for fila in celdas.itertuples()
]
columna = "visitantes" if modo == "Visitantes" else "participacion"
tabla = celdas.pivot(index="anio", columns="mes", values=columna)

# sin clic en V5 (u oculta) se muestra el último año completo
anio_elegido = ultimo_anio_completo(datos)

st.divider()
columnas = columnas_visibles(len(visibles), proporciones=[1.1, 1])
izquierda, derecha = columnas[0], columnas[-1]

# =============================================================================
# V5. Mapa de calor año × mes
# =============================================================================
if "v5" in visibles:
    with izquierda:
        encabezado_visualizacion(
            5, "¿En qué meses se concentra la demanda?",
            "Cada celda es un mes: **más oscuro = más visitantes**. Cada fila es un año, así se ve "
            "si la temporada alta se repite.",
            "planificar personal, capacidad y promoción según la temporada, y anticipar la presión "
            "sobre los destinos en los meses más concurridos. **Haga clic en una celda** para ver "
            "ese año en detalle.",
        )

        fig5 = go.Figure()
        fig5.add_trace(go.Heatmap(
            x=MESES, y=tabla.index, z=tabla.values,
            colorscale=ESCALA_AZUL, xgap=2, ygap=2, hoverinfo="skip",
            # escala horizontal debajo del mapa: no le quita ancho en pantallas angostas
            colorbar=dict(
                orientation="h", x=0, xanchor="left", y=-0.02, yanchor="top", len=1,
                title=dict(text="Visitantes" if modo == "Visitantes" else "% del año", side="top"),
                tickformat="~s" if modo == "Visitantes" else ".0f",
                ticksuffix="" if modo == "Visitantes" else " %",
                thickness=10, outlinewidth=0,
            ),
        ))
        # capa transparente que recibe clics y tooltips (ver nota al inicio del archivo)
        fig5.add_trace(go.Scatter(
            x=celdas["mes"], y=celdas["anio"], mode="markers",
            marker=dict(symbol="square-open", size=16, color="rgba(0,0,0,0)",
                        line=dict(width=2)),
            selected=dict(marker=dict(color=TINTA)),
            unselected=dict(marker=dict(color="rgba(0,0,0,0)")),
            text=celdas["texto"], hovertemplate="%{text}<extra></extra>",
            showlegend=False,
        ))
        fig5.update_layout(
            height=600, clickmode="event+select", dragmode=False, hoverdistance=-1,
            # rangos fijos: sin ellos la capa de puntos agrega filas vacías (2008, 2027)
            xaxis=dict(tickmode="array", tickvals=MESES, ticktext=MESES_ES, side="top",
                       range=[0.5, 12.5],
                       showgrid=False, ticks="", linecolor="rgba(0,0,0,0)"),
            yaxis=dict(range=[max(anios) + 0.5, min(anios) - 0.5], tickmode="linear",
                       dtick=1, showgrid=False, ticks="", linecolor="rgba(0,0,0,0)"),
            margin=dict(t=40, r=10),
        )
        evento5 = mostrar_grafica(fig5, key="v5_mapa", on_select="rerun", selection_mode="points")

        indices = evento5.selection.point_indices if evento5 else []
        celda_elegida = celdas.iloc[indices[0]] if indices else None
        if celda_elegida is not None:
            anio_elegido = int(celda_elegida["anio"])
            st.success(f"Año seleccionado: **{anio_elegido}**. Doble clic en el mapa para quitar la selección.",
                       icon=":material/calendar_month:")
        else:
            st.caption(f":material/touch_app: Sin selección: se muestra {anio_elegido}, el último año completo.")
        st.caption("2020 y 2021 corresponden a la pandemia; en esos años el patrón de los meses es atípico.")

# =============================================================================
# V6. Perfil mensual del año elegido frente a una referencia
# =============================================================================
if "v6" in visibles:
    with derecha:
        if "v5" not in visibles:
            # sin el mapa no hay clic: el año se elige aquí
            anio_elegido = int(st.selectbox(
                "Año", anios, index=anios.index(anio_elegido), key="anio_estacionalidad",
                help="Active la gráfica 5 para elegir el año con un clic en el mapa.",
            ))
        encabezado_visualizacion(
            6, f"¿Cómo se comportó {anio_elegido} frente a lo habitual?",
            f"{'Visitantes' if modo == 'Visitantes' else 'Porcentaje de visitantes del año'} de cada "
            f"mes de **{anio_elegido}** (azul) frente a una referencia (gris): un año típico antes "
            "de la pandemia o el año anterior.",
            "detectar meses que se alejaron de lo habitual, evaluar una temporada o fijar metas mensuales.",
        )
        comparar = st.segmented_control(
            "Comparar con", [f"Promedio {INICIO_REFERENCIA}–{FIN_REFERENCIA}", "Año anterior"],
            default=f"Promedio {INICIO_REFERENCIA}–{FIN_REFERENCIA}", key="comparar_estacionalidad",
            help=f"El promedio {INICIO_REFERENCIA}–{FIN_REFERENCIA} representa un año típico antes "
                 "de la pandemia; la franja gris muestra el mínimo y el máximo de esos años.",
        ) or f"Promedio {INICIO_REFERENCIA}–{FIN_REFERENCIA}"
        usa_promedio = comparar.startswith("Promedio")
        nombre_referencia = (f"promedio {INICIO_REFERENCIA}–{FIN_REFERENCIA}" if usa_promedio
                             else str(anio_elegido - 1))
        # "por encima del promedio…" / "por encima de 2024"
        de_referencia = ("del " if usa_promedio else "de ") + nombre_referencia
        a_referencia = ("al " if usa_promedio else "a ") + nombre_referencia
        unidad = "visitantes" if modo == "Visitantes" else "% del año"

        anio_serie = tabla.loc[anio_elegido]
        if usa_promedio:
            referencia_anios = tabla.loc[INICIO_REFERENCIA:FIN_REFERENCIA]
            referencia = referencia_anios.mean()
        else:
            referencia = tabla.loc[anio_elegido - 1] if anio_elegido - 1 in tabla.index else None

        if anio_serie.isna().all():
            st.info(
                f"{anio_elegido} no tiene los 12 meses en la base, por eso no se puede expresar como "
                "% del año. Cambie «Mostrar como» a «Visitantes» para verlo.",
                icon=":material/info:",
            )
        elif referencia is None or referencia.isna().all():
            st.info(
                f"No hay datos de {anio_elegido - 1} en la base para comparar. "
                f"Elija «Promedio {INICIO_REFERENCIA}–{FIN_REFERENCIA}» o seleccione otro año.",
                icon=":material/info:",
            )
        else:
            formato = ",.0f" if modo == "Visitantes" else ".1f"
            sufijo = "" if modo == "Visitantes" else " %"
            fig6 = go.Figure()
            if usa_promedio:
                fig6.add_trace(go.Scatter(
                    x=MESES_ES + MESES_ES[::-1],
                    y=list(referencia_anios.max()) + list(referencia_anios.min()[::-1]),
                    fill="toself", fillcolor="rgba(137,135,129,0.15)", line=dict(width=0),
                    hoverinfo="skip", name=f"Rango {INICIO_REFERENCIA}–{FIN_REFERENCIA}",
                ))
            fig6.add_trace(go.Scatter(
                x=MESES_ES, y=referencia, mode="lines", name=nombre_referencia.capitalize(),
                line=dict(color=GRIS_REFERENCIA, width=2, dash="dot"),
                hovertemplate=f"%{{y:{formato}}}{sufijo}<extra>{nombre_referencia.capitalize()}</extra>",
            ))
            fig6.add_trace(go.Scatter(
                x=MESES_ES, y=anio_serie, mode="lines+markers", name=str(anio_elegido),
                line=dict(color=AZUL_OBSERVADO, width=2.5),
                marker=dict(size=8, color=AZUL_OBSERVADO, line=dict(color="#fcfcfb", width=1)),
                hovertemplate=f"<b>%{{y:{formato}}}{sufijo}</b><extra>{anio_elegido}</extra>",
            ))
            fig6.update_layout(
                height=470, hovermode="x unified",
                xaxis=dict(title=None),
                yaxis=dict(title=unidad.capitalize(), rangemode="tozero",
                           tickformat="~s" if modo == "Visitantes" else ".0f",
                           ticksuffix=sufijo, gridcolor=CUADRICULA),
            )
            mostrar_grafica(fig6, key="v6_perfil")

            # -- hallazgos observados (sin atribuir causas) ------------------------
            comparables = anio_serie.dropna().index.intersection(referencia.dropna().index)
            if modo == "Visitantes":
                diferencia = (anio_serie[comparables] / referencia[comparables] - 1) * 100
                texto_diferencia = "{:+.0f} %"
            else:
                # en % del año se comparan proporciones: la diferencia va en puntos porcentuales
                diferencia = anio_serie[comparables] - referencia[comparables]
                texto_diferencia = "{:+.1f} puntos porcentuales"
            diferencia = diferencia[np.isfinite(diferencia)]
            mes_pico = int(anio_serie.idxmax())
            meses_arriba = int((diferencia > 0).sum())
            texto_pico = f"{anio_serie[mes_pico]:{formato}}{sufijo}"
            st.markdown("**Lo que muestran los datos**")
            lineas = [f"- El mes con más visitantes de {anio_elegido} fue **{MESES_ES[mes_pico - 1]}** "
                      f"({texto_pico})."]
            if len(diferencia):
                lineas.append(f"- {anio_elegido} estuvo por encima {de_referencia} en "
                              f"**{meses_arriba} de {len(diferencia)}** meses.")
                mes_mayor = int(diferencia.abs().idxmax())
                lineas.append(
                    f"- La mayor diferencia fue en **{MESES_ES[mes_mayor - 1]}**: "
                    f"{texto_diferencia.format(diferencia[mes_mayor])} frente {a_referencia}."
                )
            if len(anio_serie.dropna()) < 12:
                lineas.append(f"- {anio_elegido} está incompleto en la base (solo {len(anio_serie.dropna())} meses).")
            st.markdown("\n".join(lineas))
            st.caption(
                ":material/info: La gráfica muestra diferencias frente a lo habitual, no sus causas. "
                "Un mes distinto al promedio puede deberse a muchos factores que estos datos no registran."
            )
