import streamlit as st

from utils.datos import TIPOS_COMPARABLES, cargar_datos, ultimo_anio_completo

datos = cargar_datos()
comparables = datos[datos["tipo"].isin(TIPOS_COMPARABLES)]
anio = ultimo_anio_completo(datos)
por_anio = comparables.groupby("anio")["visitantes"].sum()

st.title("Observatorio de Turismo Sostenible · Guatemala")
st.markdown(
    "Este tablero resume **cuántos visitantes internacionales llegan a Guatemala, "
    "de dónde vienen y cuántos se esperan**, para apoyar decisiones de promoción, "
    "planificación de capacidad y gestión de destinos. No requiere conocimientos "
    "de estadística: cada gráfica indica qué muestra y para qué puede usarla."
)

st.subheader(f"Cifras clave de {anio}")
c1, c2, c3, c4 = st.columns(4)
variacion_anual = (por_anio[anio] / por_anio[anio - 1] - 1) * 100
variacion_2019 = (por_anio[anio] / por_anio[2019] - 1) * 100
paises = (
    comparables[comparables["anio"] == anio]
    .groupby("pais", observed=True)["visitantes"].sum()
    .sort_values(ascending=False)
)
participacion_top = paises.iloc[0] / paises.sum() * 100

c1.metric("Visitantes internacionales", f"{por_anio[anio]:,.0f}", border=True,
          help="Turistas (pernoctan) + excursionistas (no pernoctan).")
c2.metric(f"Cambio frente a {anio - 1}", f"{variacion_anual:+.1f} %", border=True)
c3.metric("Cambio frente a 2019 (prepandemia)", f"{variacion_2019:+.1f} %", border=True,
          help="Compárese con cautela: en 2023 hubo un cambio en la forma de clasificar a los viajeros.")
c4.metric("Principal mercado emisor", paises.index[0], border=True,
          help=f"{participacion_top:.0f} % de los visitantes de {anio}.")

st.divider()

izquierda, derecha = st.columns([3, 2], gap="large")
with izquierda:
    st.subheader("Preguntas que responde este tablero")
    st.markdown(
        """
1. **¿Se ha recuperado la llegada de visitantes después de la pandemia?**
   → *Llegadas y mercados*
2. **¿De qué regiones y países vienen los visitantes, y qué tan concentrados están?**
   → *Llegadas y mercados*
3. **¿En qué meses se concentra la demanda y por dónde ingresan los visitantes?**
   → *Estacionalidad y vías* (en construcción)
4. **¿Cuántos visitantes se esperan y qué tan confiables son esas estimaciones?**
   → *Pronósticos de modelos*
        """
    )
with derecha:
    st.subheader("Cómo usarlo")
    st.markdown(
        """
- Use el **menú lateral** para cambiar de sección.
- **Arrastre** sobre una gráfica de tiempo para elegir un período;
  las gráficas de abajo se actualizan con ese período.
- **Haga clic** en una barra para ver más detalle.
- **Doble clic** sobre una gráfica limpia la selección.
- Pase el cursor sobre cualquier elemento para ver el valor exacto.
        """
    )
    st.info(
        "**Colores con significado fijo:** azul = datos observados · "
        "naranja y aqua = estimaciones de modelos · gris = referencia o contexto.",
        icon=":material/palette:",
    )
