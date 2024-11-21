from datetime import datetime, timedelta
import requests
import pandas as pd
import numpy as np
import io
from keras.models import Sequential
from keras.layers import LSTM, Dense, Dropout
from sklearn.preprocessing import MinMaxScaler
from sqlalchemy.orm import Session
from models import HistoricalData

# Función para verificar si los datos existen en la base de datos
def check_data_exists(db: Session, ticker: str, date: datetime):
    start_date = date - timedelta(days=90)  # 1 año hacia atrás
    return db.query(HistoricalData).filter(
        HistoricalData.symbol == ticker,
        HistoricalData.date >= start_date,
        HistoricalData.date <= date
    ).count() > 0

# Función para obtener datos históricos de un ticker
def get_historical_data(ticker):
    url = f"http://localhost:8001/historical-data/?ticker={ticker}&amount=3&unit=months&asset_type=stock"
    response = requests.get(url)
    data = pd.read_csv(io.StringIO(response.text))
    return data[['Date', 'Close']]  # Solo obtener 'Date' y 'Close'

# Función para preparar los datos para LSTM
def prepare_data(data, time_step=1):
    X, y = [], []
    for i in range(len(data) - time_step - 1):
        X.append(data[i:(i + time_step), 0])  # Usar solo 'Close'
        y.append(data[i + time_step, 0])      # El precio de cierre como objetivo
    return np.array(X).reshape(-1, time_step, 1), np.array(y)  # Redimensionar X para LSTM

# Función para definir y entrenar el modelo LSTM
def train_lstm_model(data, time_step=15):
    # Normalizar los datos
    scaler = MinMaxScaler(feature_range=(0, 1))
    data_scaled = scaler.fit_transform(data.reshape(-1, 1))

    # Preparar datos
    X, y = prepare_data(data_scaled, time_step)
    
    # Definir el modelo LSTM
    model = Sequential()
    model.add(LSTM(units=25, return_sequences=True, input_shape=(X.shape[1], X.shape[2])))
    model.add(Dropout(0.2))  # Añadir dropout para más variabilidad
    model.add(LSTM(units=25, return_sequences=True))
    model.add(Dropout(0.2))
    model.add(LSTM(units=25))
    model.add(Dropout(0.2))
    model.add(Dense(units=1))  # Salida para la predicción del siguiente valor de cierre

    # Compilar el modelo
    model.compile(optimizer='adam', loss='mean_squared_error')

    # Entrenar el modelo
    model.fit(X, y, epochs=50, batch_size=32)  # Aumentar las épocas para mejorar el aprendizaje

    return model, scaler

def get_historical_data_from_db(db: Session, ticker: str, current_date: datetime):
    one_month_ago = current_date - timedelta(days=90)
    return db.query(HistoricalData).filter(
        HistoricalData.symbol == ticker,
        HistoricalData.date >= one_month_ago
    ).all()

# Función para predecir valores futuros
def predict_with_lstm(ticker: str, db: Session, time_step=15, forecast_days=10):
    current_date = datetime.now()
    existing_data = get_historical_data_from_db(db, ticker, current_date)

    if existing_data:
        print(f"Usando datos existentes para el ticker '{ticker}' en la base de datos.")
        prices = np.array([data.close for data in existing_data])  # Solo 'Close'
    else:
        print(f"No se encontraron datos para el ticker '{ticker}' en la base de datos. Obteniendo datos del servicio.")
        data = get_historical_data(ticker)
        prices = data['Close'].values

    # Entrenar el modelo LSTM
    model, scaler = train_lstm_model(prices, time_step)
    
    # Preparar los últimos datos para la predicción
    last_data = scaler.transform(prices[-time_step:].reshape(-1, 1))
    last_data = last_data.reshape((1, time_step, 1))

    # Lista para almacenar los precios futuros predichos
    future_prices = []

    for _ in range(forecast_days):
        # Hacer una predicción
        future_price_scaled = model.predict(last_data)

        # Agregar el precio predicho a la lista
        future_prices.append(future_price_scaled[0, 0])  # Solo el valor de cierre

        future_price_scaled_reshaped = np.array(future_price_scaled[0, 0]).reshape((1, 1, 1))

        # Actualizar last_data para incluir el nuevo precio predicho
        last_data = np.append(last_data[:, 1:, :], future_price_scaled_reshaped, axis=1)

    # Desnormalizar los precios futuros
    future_prices = scaler.inverse_transform(np.array(future_prices).reshape(-1, 1)).flatten()

    # Obtener los precios reales (últimos conocidos)
    real_values = prices  # Últimos precios de cierre conocidos

    return real_values, future_prices  # Retornar los valores reales y los precios futuros predichos
