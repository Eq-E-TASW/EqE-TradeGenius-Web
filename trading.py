import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from models import HistoricalData
import time

def app():

    db = next(get_db())  # Obtienes la sesión de la base de datos

    st.title("💹 Trading de Acciones")

    data = {
    "Ticker": ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"],
    "Cantidad": [10, 15, 8, 20, 5],
    "Precio Unitario": [175.6, 330.2, 135.4, 144.3, 220.5],  # Precios unitarios aproximados
    "Precio Total": [1756.0, 4953.0, 1083.2, 2886.0, 1102.5]  # Calculado: cantidad * p.unitario
    }

    df = pd.DataFrame(data) 
    st.write("#### Inventario Actual:")
    st.write(df)

    ticker_options = ["Seleccionar..."] + [result[0] for result in db.query(HistoricalData.symbol).distinct().all()]

    # Input para el ticker
    ticker = st.selectbox("Selecciona el ticker para la predicción:", ticker_options)

    # Input para el número (cantidad)
    amount = st.number_input("Ingrese la cantidad", min_value=1, value=1)
     
    trade_options = ["Comprar","Vender"]

    # Input para la operacion
    trade = st.selectbox("Selecciona la operación:", trade_options)

    if ticker != "Seleccionar...":
        st.write(f"Detalles de la operación: {trade} {amount} unidades de {ticker}.")
    else:
        st.write("Por favor, selecciona un ticker válido.")
        
    # Variable para confirmar la operación
    if "confirm" not in st.session_state:
        st.session_state.confirm = False

    # Botón principal para iniciar la operación
    confirm_button = st.button(f"{trade}")

    st.write("¿Estás seguro?")

    # Verificar si el usuario hace clic en el botón principal
    if confirm_button:
        if ticker=="Seleccionar...":
            st.warning("Por favor, selecciona un ticker antes de continuar.")
        else:
            st.session_state.confirm = True

    # Mostrar detalles de la operación si `st.session_state.confirm` es True
    if st.session_state.confirm:
        # Crear 2 columnas para colocar los botones en una fila horizontal
        col1, col2 = st.columns(2)

        with col1:
            cancel = st.button("Cancelar", key="cancel_button")
        
        with col2:
            confirm = st.button("Confirmar", key="final_confirm")

        if cancel:
            st.session_state.confirm = False
            st.warning("Operación cancelada.")
            time.sleep(1)  # Pausa de 1 segundos antes de recargar
            st.rerun()  # Recargar la página
    
        if confirm:
            st.success("¡Operación realizada con éxito!")
            # Reiniciar el estado de confirmación después de completar la operación
            st.session_state.confirm = False
            time.sleep(1)  # Pausa de 1 segundos antes de recargar
            st.rerun()  # Recargar la página
