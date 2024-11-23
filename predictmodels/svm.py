from datetime import datetime, timedelta
import requests
import pandas as pd
import numpy as np
import io
from sklearn.svm import SVR
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy.orm import Session
from utils.models import HistoricalData

# Función para verificar si los datos existen en la base de datos
def check_data_exists(db: Session, ticker: str, date: datetime):
    start_date = date - timedelta(days=365)  # 1 año hacia atrás
    return db.query(HistoricalData).filter(
        HistoricalData.symbol == ticker,
        HistoricalData.date >= start_date,
        HistoricalData.date <= date
    ).count() > 0

# Función para obtener datos históricos de un ticker desde el servicio externo
def get_historical_data(ticker):
    url = f"http://localhost:8001/historical-data/?ticker={ticker}&amount=1&unit=years&asset_type=stock"
    response = requests.get(url)
    data = pd.read_csv(io.StringIO(response.text))
    return data[['Open', 'High', 'Low', 'Close', 'Volume']]  # Usar múltiples columnas para el SVM

# Función para obtener datos históricos desde la base de datos
def get_historical_data_from_db(db: Session, ticker: str, current_date: datetime):
    one_year_ago = current_date - timedelta(days=365)
    return db.query(HistoricalData).filter(
        HistoricalData.symbol == ticker,
        HistoricalData.date >= one_year_ago
    ).all()

# Función para preparar los datos para SVM
def prepare_data(data, time_step=1):
    X, y = [], []
    for i in range(len(data) - time_step - 1):
        X.append(data[i:(i + time_step), 0])  # Usar solo 'Close'
        y.append(data[i + time_step, 0])      # El precio de cierre como objetivo
    return np.array(X).reshape(-1, time_step, 1), np.array(y)  # Redimensionar X para LSTM

# Función para entrenar el modelo SVM
def train_svm_model(data, time_step=10):
    # Normalizar los datos
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data.reshape(-1, 1))
    # Preparar los datos
    X, y = prepare_data(data_scaled, time_step)
    # Definir el modelo SVM
    model = SVR(kernel='rbf', C=100, gamma=0.1, epsilon=0.01)
    # Entrenar el modelo SVM
    model.fit(X.reshape(X.shape[0], -1), y)  # Ajustar la forma de X para el SVM

    return model, scaler

# Función para predecir valores futuros con SVM
def predict_with_svm(ticker: str, db: Session, time_step=15, forecast_days=10):
    current_date = datetime.now()

    # Verificar si los datos ya existen en la base de datos
    existing_data = get_historical_data_from_db(db, ticker, current_date)
    if existing_data:
        print(f"Usando datos existentes para el ticker '{ticker}' en la base de datos.")
        prices = np.array([data.close for data in existing_data])  # Solo 'Close'
    else:
        print(f"No se encontraron datos para el ticker '{ticker}' en la base de datos. Obteniendo datos del servicio.")
        data = get_historical_data(ticker)
        prices = data['Close'].values

    # Entrenar el modelo SVM
    model, scaler = train_svm_model(prices, time_step)

    # Preparar los últimos datos para predicción
    last_data = scaler.transform(prices[-time_step:].reshape(-1, 1))  # Escalar últimos datos
    last_data = last_data.reshape(1, -1)  # Redimensionar a (1, time_step) para SVR

    # Lista para almacenar los precios futuros predichos
    future_prices = []

    # Realizar predicciones para los próximos 'forecast_days' días
    for _ in range(forecast_days):
        # Hacer una predicción
        predicted_price_scaled = model.predict(last_data)  # No necesita tercera dimensión

        # Agregar el precio predicho (escalado) a la lista
        future_prices.append(predicted_price_scaled[0])  # Guardar el primer valor predicho

        # Actualizar last_data para incluir el nuevo precio predicho
        new_data_scaled = np.append(last_data[:, 1:], [[predicted_price_scaled[0]]], axis=1)
        last_data = new_data_scaled

    # Desnormalizar los precios futuros
    future_prices = scaler.inverse_transform(np.array(future_prices).reshape(-1, 1)).flatten()

    # Obtener los precios reales (últimos conocidos)
    real_values = prices

    return real_values, future_prices  # Retornar los valores reales y predichos
