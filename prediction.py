import streamlit as st
from utils.database import SessionLocal, get_db
from utils.models import HistoricalData
from utils.funtions import create_prediction_log
from datetime import datetime
import requests
from PIL import Image
from io import BytesIO

def app():
    st.title("📉 Predicción de Acciones")

    db = next(get_db())  

    ticker_options = ["Seleccionar..."] + [result[0] for result in db.query(HistoricalData.symbol).distinct().all()]
    
    # Input para el ticker
    ticker = st.selectbox("Selecciona el ticker para la predicción:", ticker_options)
    
    model_options = ["Seleccionar...","LSTM","SVM"]

    # Input para el modelo
    model_name = st.selectbox("Selecciona el modelo a utilizar:", model_options)

    # Construimos las URL 
    endpoint_url_post = (
        f"https://tradegeniusbackcloud-registry-194080380757.southamerica-west1.run.app/api/prediction/predict/?ticker={ticker}&model={model_name}"
    )
    endpoint_url_get = (
        f"https://tradegeniusbackcloud-registry-194080380757.southamerica-west1.run.app/api/prediction"
    )

    image = None

    # Botón para realizar la predicción
    if st.button("Realizar predicción"):
        try:
            # Solicitud a los endpoints
            response_post=requests.post(endpoint_url_post, headers={"accept": "application/json"})
            response_post.raise_for_status()  # Verifica si el POST fue exitoso

            # Valores obtenidos
            real_values = response_post.json()["real_values"]
            predicted_values = response_post.json()["predicted_values"]
            
            # Crear registro de la predicción en la base de datos
            predicted_date = datetime.now()
            predicted_price = predicted_values[-1]  # Último valor predicho
            create_prediction_log(db, ticker, model_name, predicted_date, predicted_price)

            predicted_close = float(predicted_values[0])  # Convertir a float explícitamente
            last_close = float(real_values[-1])  # Convertir a float explícitamente
            trend = predicted_close - last_close

            predicted_close = round(predicted_close, 2)
            trend = round(trend, 2)

            if "image_url" in response_post.json():
                image_filename = response_post.json()["image_url"]
                endpoint_url_get = f"{endpoint_url_get}{image_filename}"
                # GET para obtener la imagen
                response_get = requests.get(endpoint_url_get, headers={"accept": "application/json"})
                response_get.raise_for_status()

                # Mostrar la imagen
                image = Image.open(BytesIO(response_get.content))
               
        except requests.exceptions.RequestException as e:
            st.error(f"Error al obtener la gráfica: {e}")

    if image is not None:
        st.markdown("---")
        st.subheader('Predicción:')
        st.image(image)
        st.write(f"Precio del cierre predicho: {predicted_close}")
        if trend >= 0:
            st.markdown(f"Tendencia: <span style='color:green;'>{trend}</span>", unsafe_allow_html=True)
        else:
            st.markdown(f"Tendencia: <span style='color:red;'>{trend}</span>", unsafe_allow_html=True)