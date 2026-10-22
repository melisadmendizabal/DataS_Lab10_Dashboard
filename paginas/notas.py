import streamlit as st

st.title("Glosario y limitaciones")

st.subheader("Términos")
st.markdown(
    """
- **Turista:** visitante internacional que pernocta al menos una noche en el país.
- **Excursionista:** visitante que entra y sale el mismo día, sin pernoctar.
- **Viajero:** categoría de la base cuyo criterio cambió entre 2022 y 2023; por eso no se usa
  en las comparaciones de todo el período.
- **Región de residencia:** agrupación geográfica del país donde vive el visitante
  (no necesariamente su nacionalidad).
- **Modelo de pronóstico:** procedimiento que aprende el patrón de los datos pasados para
  estimar valores futuros.
- **Error promedio (MAE):** cuántos visitantes por mes se equivocó un modelo, en promedio.
- **Error que castiga fallos grandes (RMSE):** similar al anterior, pero da más peso a los meses
  con errores grandes.
- **Error promedio (%) (MAPE):** el error promedio expresado como porcentaje del valor real.
- **Incertidumbre (intervalo de 95 %):** rango en el que el modelo espera que esté el valor real
  con 95 % de probabilidad.
    """
)

st.subheader("Limitaciones")
st.markdown(
    """
- Los datos describen **ingresos registrados**; no indican gasto, duración de la estadía ni motivo del viaje.
- Las gráficas muestran **asociaciones en el tiempo**, no causas. Por ejemplo, una caída coincide con la
  pandemia, pero el tablero no mide el efecto de medidas específicas.
- Los modelos del Laboratorio 1 se entrenaron con datos hasta marzo de 2021 (en plena pandemia),
  por lo que sus estimaciones del período 2021–2026 son conservadoras.
- La serie comparable usa solo turistas y excursionistas; el cambio metodológico de 2023 puede afectar
  las comparaciones con años anteriores.
- 2026 contiene solo enero a junio: los totales de ese año son parciales.
    """
)

st.subheader("Significado de los colores")
st.markdown(
    """
| Color | Significado |
|---|---|
| Azul | Datos observados (lo que realmente ocurrió) |
| Naranja | Estimación del modelo Holt-Winters |
| Aqua | Estimación del modelo SARIMA |
| Gris | Referencia o contexto: modelo ingenuo, pandemia, elementos no seleccionados |
    """
)
