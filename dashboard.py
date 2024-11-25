import streamlit as st
from utils.database import SessionLocal, get_db
from utils.models import HistoricalData
from utils.funtions import get_date_range
from datetime import datetime, timedelta
import pandas as pd
import requests
from PIL import Image
from io import BytesIO

def app():

    db = next(get_db())
    
    st.title("📊 Visualización de Precios")

    st.write("Tickers disponibles:")
    list_tickers= db.query(HistoricalData.symbol).distinct().all()
    
    # Convertir la lista de tuplas a una lista de cadenas
    tickers = [ticker[0] for ticker in list_tickers]

    # Convertir a DataFrame
    df_tickers = pd.DataFrame(tickers).T  # .T transpuesta para imprimir de forma horizontal

    # Imprimir el DataFrame
    st.dataframe(df_tickers, use_container_width=True, hide_index=True)

    # Solicitar al usuario los símbolos de valor a analizar, separados por coma
    ticker_txt = st.text_input("Ingrese los símbolos de valor a analizar (separados por coma)")

    tickers = []

    # Procesar la entrada cuando el usuario ingresa datos
    if ticker_txt:
        # Convertir la cadena de texto en una lista de símbolos, eliminando espacios extra
        tickers = [ticker.strip() for ticker in ticker_txt.split(',')]

    # Input para el número (cantidad)
    amount = st.number_input("Ingrese la cantidad de unidades de tiempo", min_value=1, value=1)

    # Input para la unidad (semanas, meses, años)
    unit = st.radio(
        "Seleccione la unidad de tiempo",
        options=["Semanas", "Meses", "Años"],
        index=2  # Selecciona por defecto "Años"
    )

    unit_dict = {
        "Semanas": "weeks",
        "Meses": "months",
        "Años": "years",
    }

    # Traducir la selección del usuario a inglés
    unit = unit_dict.get(unit, "Unknown")

    start_date, end_date = get_date_range(amount, unit)

    # Solicitar al usuario que seleccione el tipo de precio
    price_options = ["Apertura", "Más alto", "Más bajo", "Cierre"]
    price_type = st.selectbox("Selecciona el tipo de precio", price_options)

    precio_dict = {
        "Apertura": "open",
        "Más alto": "high",
        "Más bajo": "low",
        "Cierre": "close",
    }

    # Traducir la selección del usuario a inglés
    price_type = precio_dict.get(price_type, "Unknown")

    # Construir la URL con múltiples parámetros tickers
    tickers_params = '&'.join([f"tickers={ticker}" for ticker in tickers])
    endpoint_url1 = (
        f"https://tradegeniusbackcloud-registry-194080380757.southamerica-west1.run.app/api/data_ingestion/plot/"
        f"?{tickers_params}&amount=1&unit=years&price_type=open"
    )
    endpoint_url2 = (
        f"https://tradegeniusbackcloud-registry-194080380757.southamerica-west1.run.app/api/data_ingestion/plot_last_volume/"
        f"?{tickers_params}"
    )

    image1 = None
    image2 = None

    # Botón para generar la gráfica
    if st.button("Generar gráfica"):
        try:
            # Solicitud a los endpoints
            response1 = requests.get(endpoint_url1, headers={"accept": "application/json"})
            response1.raise_for_status()  # Lanza excepción si ocurre un error en la solicitud

            response2 = requests.get(endpoint_url2, headers={"accept": "application/json"})
            response2.raise_for_status()  # Lanza excepción si ocurre un error en la solicitud

            # Convertir la respuesta a imagen
            image1 = Image.open(BytesIO(response1.content))
            image2 = Image.open(BytesIO(response2.content))

        except requests.exceptions.RequestException as e:
            st.error(f"Error al obtener la gráfica: {e}")

    if len(tickers) == 0:
        st.warning("Por favor, ingrese al menos un símbolo de valor.")
        return
    
    # Mostrar la imagen en Streamlit
    if image1 is not None:
        st.markdown("---")
        
        if len(tickers) == 1:
            st.write(f"**Ticker:** {tickers[0]}")
        else:
            st.write(f"**Tickers:** {', '.join(tickers)}")

        st.write(f"Datos registrados desde {start_date} hasta {end_date}")
        st.subheader('Evolución Histórica de Precios')
        st.image(image1)

    # Mostrar la imagen en Streamlit
    if image2 is not None:
        st.subheader('Volumen Actual de Transacciones ')
        st.image(image2)

    
    



