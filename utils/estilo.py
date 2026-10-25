"""
Paleta, tipografía y plantilla de Plotly del tablero.

El significado de cada color se mantiene en TODA la aplicación:
    - Azul      -> datos observados (lo que realmente ocurrió)
    - Verde     -> estimación del modelo Holt-Winters
    - Aqua      -> estimación del modelo SARIMA
    - Gris      -> referencia o contexto (modelo ingenuo, pandemia, elementos no seleccionados)

Azul, verde bosque y aqua se validaron para daltonismo (protanopía / deuteranopía /
tritanopía) en todos los pares. El verde es oscuro a propósito: se separa del aqua por
luminosidad y no se confunde con el verde claro de los avisos de estado.

Las magnitudes (mapa de calor) usan una sola escala de azules, de claro (poco) a oscuro (mucho).
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
VERDE_HW = "#006300"
AQUA_SARIMA = "#1baf7a"
GRIS_REFERENCIA = "#898781"
GRIS_CONTEXTO = "#f0efec"

# escala secuencial de un solo tono (azul = dato observado), de claro a oscuro
ESCALA_AZUL = [
    [0.00, "#cde2fb"],
    [0.25, "#86b6ef"],
    [0.50, "#3987e5"],
    [0.75, "#1c5cab"],
    [1.00, "#0d366b"],
]

COLORES_MODELO = {
    "Holt-Winters": VERDE_HW,
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
        colorway=[AZUL_OBSERVADO, VERDE_HW, AQUA_SARIMA],
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
                   tickfont=dict(color=TINTA_SECUNDARIA), ticklabelstandoff=6,
                   title=dict(font=dict(color=TINTA_SECUNDARIA))),
        barcornerradius=4,
        bargap=0.25,
    )
)
pio.templates.default = "observatorio"


def etiqueta_mes(fecha):
    """'2024-03-01' -> 'Mar 2024'."""
    return f"{MESES_ES[fecha.month - 1]} {fecha.year}"


def etiquetas_cortas(textos, maximo=26):
    """
    Acorta nombres largos para los ejes ("Reino Unido de Gran Bretaña e Irl…"), así la
    gráfica conserva espacio en pantallas angostas. El nombre completo debe ir en el tooltip.
    Si al acortar dos nombres quedan iguales, se dejan completos para no mezclar barras.
    """
    textos = [str(texto) for texto in textos]
    cortos = [t if len(t) <= maximo else t[:maximo - 1].rstrip() + "…" for t in textos]
    return cortos if len(set(cortos)) == len(set(textos)) else textos


def mostrar_grafica(fig, **kwargs):
    """Dibuja la figura con la plantilla propia (no la de Streamlit)."""
    # Streamlit pone su propio fondo y fuente cuando no vienen en el layout de la figura
    # (no mira la plantilla), por eso se copian aquí de forma explícita.
    fuente = fig.layout.font
    fig.update_layout(
        paper_bgcolor=fig.layout.paper_bgcolor or SUPERFICIE,
        plot_bgcolor=fig.layout.plot_bgcolor or SUPERFICIE,
        font=dict(family=fuente.family or FUENTE, size=fuente.size or 14,
                  color=fuente.color or TINTA_SECUNDARIA),
    )
    # que los nombres de los ejes nunca queden cortados, en cualquier ancho de pantalla
    fig.update_xaxes(automargin=True)
    fig.update_yaxes(automargin=True)
    config = {"displaylogo": False, "locale": "es", "responsive": True,
              "modeBarButtonsToRemove": ["lasso2d", "autoScale2d"]}
    return st.plotly_chart(fig, theme=None, width="stretch",
                           config=config, **kwargs)


def selector_graficas(opciones, key):
    """
    Deja que el usuario elija qué gráficas de la página ver (requisito 3.3).

    opciones: {id: etiqueta} en el orden de la página, p. ej. {"v1": "1. Evolución"}.
    Devuelve el conjunto de ids elegidos; la elección se recuerda al cambiar de página.
    Cada página debe seguir funcionando si se oculta una gráfica enlazada (usar un valor
    por defecto o un control alternativo en lugar de la selección de la gráfica oculta).
    """
    guardado = f"{key}__guardado"
    if key not in st.session_state:
        st.session_state[key] = st.session_state.get(guardado, list(opciones))
    elegidas = st.pills(
        "Gráficas a mostrar", list(opciones), format_func=opciones.get,
        selection_mode="multi", key=key,
        help="Active o desactive gráficas para enfocarse en lo que necesita. "
             "Las gráficas enlazadas siguen funcionando con las que queden visibles.",
    )
    st.session_state[guardado] = elegidas
    if not elegidas:
        st.info("Seleccione al menos una gráfica en «Gráficas a mostrar».",
                icon=":material/visibility_off:")
        st.stop()
    return set(elegidas)


def columnas_visibles(cantidad, gap="large", proporciones=None):
    """
    Columnas para gráficas lado a lado. Con una sola gráfica visible usa todo el ancho.
    En pantallas angostas Streamlit apila las columnas solo (diseño responsive).
    """
    if cantidad <= 1:
        return [st.container()]
    return st.columns(proporciones or cantidad, gap=gap)


def encabezado_visualizacion(numero, pregunta, descripcion, uso):
    """Encabezado estándar: pregunta de gestión, qué muestra y para qué sirve."""
    st.markdown(f"#### {numero}. {pregunta}")
    st.markdown(descripcion)
    st.caption(f":material/lightbulb: **Para qué le sirve:** {uso}")
