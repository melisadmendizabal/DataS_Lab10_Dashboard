"""
Paleta, tipografía y plantilla de Plotly del tablero.

El significado de cada color se mantiene en TODA la aplicación:
    - Azul      -> datos observados (lo que realmente ocurrió)
    - Naranja   -> estimación del modelo Holt-Winters
    - Aqua      -> estimación del modelo SARIMA
    - Gris      -> referencia o contexto (modelo ingenuo, pandemia, elementos no seleccionados)

Azul, naranja y aqua son los tres primeros slots de una paleta categórica validada
para daltonismo (protanopía / deuteranopía) en todos los pares.
"""

import plotly.graph_objects as go
import plotly.io as pio
import streamlit as st

# -- superficies y tinta -------------------------------------------------------
SUPERFICIE = "#fcfcfb"
PLANO = "#f9f9f7"
TINTA = "#0b0b0b"
TINTA_SECUNDARIA = "#52514e"
TINTA_TENUE = "#898781"
CUADRICULA = "#e1e0d9"
EJE = "#c3c2b7"

# -- colores con significado ---------------------------------------------------
AZUL_OBSERVADO = "#2a78d6"
NARANJA_HW = "#eb6834"
AQUA_SARIMA = "#1baf7a"
GRIS_REFERENCIA = "#898781"
GRIS_CONTEXTO = "#f0efec"

COLORES_MODELO = {
    "Holt-Winters": NARANJA_HW,
    "SARIMA": AQUA_SARIMA,
    "Ingenuo estacional": GRIS_REFERENCIA,
}
ESTILO_LINEA_MODELO = {
    "Holt-Winters": "solid",
    "SARIMA": "dash",
    "Ingenuo estacional": "dot",
}

FUENTE = '"Source Sans Pro", system-ui, -apple-system, "Segoe UI", sans-serif'

MESES_ES = ["Ene", "Feb", "Mar", "Abr", "May", "Jun",
            "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]

pio.templates["observatorio"] = go.layout.Template(
    layout=dict(
        font=dict(family=FUENTE, size=14, color=TINTA_SECUNDARIA),
        paper_bgcolor=SUPERFICIE,
        plot_bgcolor=SUPERFICIE,
        colorway=[AZUL_OBSERVADO, NARANJA_HW, AQUA_SARIMA],
        separators=".,",
        margin=dict(l=10, r=20, t=30, b=10),
        hoverlabel=dict(bgcolor="#ffffff", bordercolor=EJE,
                        font=dict(family=FUENTE, size=13, color=TINTA)),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, x=0,
                    font=dict(color=TINTA_SECUNDARIA)),
        xaxis=dict(showgrid=False, linecolor=EJE, ticks="outside",
                   tickcolor=EJE, tickfont=dict(color=TINTA_SECUNDARIA),
                   title=dict(font=dict(color=TINTA_SECUNDARIA))),
        yaxis=dict(gridcolor=CUADRICULA, zeroline=False, linecolor=EJE,
                   tickfont=dict(color=TINTA_SECUNDARIA),
                   title=dict(font=dict(color=TINTA_SECUNDARIA))),
        barcornerradius=4,
        bargap=0.25,
    )
)
pio.templates.default = "observatorio"


def etiqueta_mes(fecha):
    """'2024-03-01' -> 'Mar 2024'."""
    return f"{MESES_ES[fecha.month - 1]} {fecha.year}"


def mostrar_grafica(fig, **kwargs):
    """Dibuja la figura con la plantilla propia (no la de Streamlit)."""
    config = {"displaylogo": False, "locale": "es",
              "modeBarButtonsToRemove": ["lasso2d", "autoScale2d"]}
    return st.plotly_chart(fig, theme=None, width="stretch",
                           config=config, **kwargs)


def encabezado_visualizacion(numero, pregunta, descripcion, uso):
    """Encabezado estándar: pregunta de gestión, qué muestra y para qué sirve."""
    st.markdown(f"#### {numero}. {pregunta}")
    st.markdown(descripcion)
    st.caption(f":material/lightbulb: **Para qué le sirve:** {uso}")
