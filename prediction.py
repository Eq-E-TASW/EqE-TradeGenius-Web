import streamlit as st
from sqlalchemy.orm import Session
from utils.database import SessionLocal, get_db
from utils.models import HistoricalData, PredictionLog
from utils.funtions import get_date_range, create_prediction_log, plot_predictions
from predictmodels import lstm, svm
from datetime import datetime
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd

def app():
    st.title("📉 Predicción de Acciones")

    db = next(get_db())  # Obtienes la sesión de la base de datos

    ticker_options = ["Seleccionar..."] + [result[0] for result in db.query(HistoricalData.symbol).distinct().all()]
    
    # Input para el ticker
    ticker = st.selectbox("Selecciona el ticker para la predicción:", ticker_options)
    
    model_options = ["Seleccionar...","LSTM","SVM"]

    # Input para el modelo
    model_name = st.selectbox("Selecciona el modelo a utilizar:", model_options)

    st.subheader('Predicción:')

    if ticker != "Seleccionar..." and model_name != "Seleccionar...":
        with st.spinner("Realizando predicciones, por favor espera..."):
            if model_name.lower() == "lstm":
                real_values, predicted_values = lstm.predict_with_lstm(ticker, db)
            elif model_name.lower() == "svm":
                real_values, predicted_values = svm.predict_with_svm(ticker, db)
            
            # Crear registro de la predicción en la base de datos
            predicted_date = datetime.now()
                
            predicted_price = predicted_values[-1]  # Último valor predicho
                
            create_prediction_log(db, ticker, model_name, predicted_date, predicted_price)
            plot_predictions(real_values, predicted_values, ticker, model_name)
            predicted_close = float(predicted_values[0])  # Convertir a float explícitamente
            last_close = float(real_values[-1])  # Convertir a float explícitamente
            trend = predicted_close - last_close

            predicted_close = round(predicted_close, 2)
            trend = round(trend, 2)

            st.write(f"Precio del cierre predicho: {predicted_close}")
            if trend >= 0:
                st.markdown(f"Tendencia: <span style='color:green;'>{trend}</span>", unsafe_allow_html=True)
            else:
                st.markdown(f"Tendencia: <span style='color:red;'>{trend}</span>", unsafe_allow_html=True)

    else:
        st.warning("Por favor, selecciona un ticker y un modelo para continuar.")


  
   
