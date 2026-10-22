import streamlit as st

st.title("Estacionalidad y vías de ingreso")
st.info(
    "Sección en construcción para la entrega final.",
    icon=":material/construction:",
)
st.markdown(
    """
Visualizaciones planificadas:

5. **¿En qué meses se concentra la demanda?** Mapa de calor año × mes (escala de azules).
   Al hacer clic en un año se detalla su perfil mensual en la gráfica 6.
6. **Perfil mensual del año seleccionado** frente al promedio histórico.
7. **¿Por dónde ingresan los visitantes?** Visitantes por vía (aérea, terrestre, marítima)
   en el tiempo, en paneles pequeños con la misma escala.
8. **¿Qué puestos fronterizos reciben más visitantes?** Barras de los principales puestos,
   enlazadas con la vía elegida en la gráfica 7.
    """
)
