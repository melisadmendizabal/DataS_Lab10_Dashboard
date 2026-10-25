"""
Observatorio de Turismo Sostenible - Guatemala
Tablero interactivo (Laboratorio 10, CC3066 Data Science).

Ejecutar con:  streamlit run app.py
"""

import streamlit as st

import utils.estilo  # noqa: F401  (registra la plantilla de Plotly)

st.set_page_config(
    page_title="Observatorio de Turismo · Guatemala",
    page_icon=":material/travel_explore:",
    layout="wide",
)

paginas = {
    "Resumen": [
        st.Page("paginas/inicio.py", title="Inicio", icon=":material/home:", default=True),
    ],
    "Explorar": [
        st.Page("paginas/exploracion.py", title="Llegadas y mercados", icon=":material/public:"),
        st.Page("paginas/estacionalidad.py", title="Estacionalidad", icon=":material/calendar_month:"),
        st.Page("paginas/vias.py", title="Vías y fronteras", icon=":material/flight_land:"),
    ],
    "Estimar": [
        st.Page("paginas/pronosticos.py", title="Pronósticos de modelos", icon=":material/insights:"),
    ],
    "Ayuda": [
        st.Page("paginas/notas.py", title="Glosario y limitaciones", icon=":material/help:"),
    ],
}

navegacion = st.navigation(paginas)

with st.sidebar:
    st.caption(
        "Fuente: base de migración de ingresos de visitantes internacionales "
        "a Guatemala, enero 2009 – junio 2026 (la misma de los Laboratorios 1 y 2)."
    )

navegacion.run()
