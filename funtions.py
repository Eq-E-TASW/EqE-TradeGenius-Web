from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from models import PredictionLog
from datetime import datetime
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import streamlit as st

# Función para calcular el rango de fechas
def get_date_range(amount: int, unit: str):
    today = datetime.today()
    
    if unit == "days":
        start_date = today - timedelta(days=amount)
    elif unit == "weeks":
        start_date = today - timedelta(weeks=amount)
    elif unit == "months":
        start_date = today - timedelta(days=30 * amount)
    elif unit == "years":
        start_date = today - timedelta(days=365 * amount)
    else:
        raise ValueError("Unidad de tiempo no válida. Use 'days', 'weeks', 'months', o 'years'.")
    
    return start_date.strftime('%Y-%m-%d'), today.strftime('%Y-%m-%d')

def create_prediction_log(db: Session, ticker: str, model_used: str, predicted_date: datetime, predicted_close_price: float):
    log_entry = PredictionLog(
        ticker=ticker,
        model_used=model_used,
        predicted_date=predicted_date,
        predicted_close_price=float(predicted_close_price)
    )
    db.add(log_entry)
    db.commit()
    db.refresh(log_entry)
    return log_entry

def plot_predictions(real_values, predicted_values, ticker, model_name):
    # Crear fechas para los valores reales (hacia atrás)
    end_date_real = pd.to_datetime('now')  # Fecha actual para los valores reales
    start_date_real = end_date_real - pd.Timedelta(days=len(real_values))  # Calcular la fecha de inicio para reales

    # Crear fechas para los valores predichos (hacia adelante)
    start_date_predicted = end_date_real  # Los predichos comienzan ahora
    end_date_predicted = start_date_predicted + pd.Timedelta(days=len(predicted_values))  # Calcular la fecha final para predicciones

    # Crear un DataFrame con los valores reales y predichos
    data_real = pd.DataFrame({
        'Fecha': pd.date_range(start=start_date_real, end=end_date_real, periods=len(real_values)),
        'Real': real_values
    })
    
    data_predicted = pd.DataFrame({
        'Fecha': pd.date_range(start=start_date_predicted, end=end_date_predicted, periods=len(predicted_values)),
        'Predicho': predicted_values
    })

    # Concatenar los DataFrames para visualización continua
    data = pd.concat([data_real, data_predicted], ignore_index=True)

    # Iniciar la figura
    plt.figure(figsize=(14, 7))
    
    # Usar Seaborn para crear la gráfica
    sns.lineplot(x='Fecha', y='Real', data=data_real, label='Valores Reales', color='blue')
    sns.lineplot(x='Fecha', y='Predicho', data=data_predicted, label='Valores Predichos', color='orange')

    plt.plot(
        [data_real['Fecha'].iloc[-1], data_predicted['Fecha'].iloc[0]],  # Fechas de conexión
        [data_real['Real'].iloc[-1], data_predicted['Predicho'].iloc[0]],  # Valores de conexión
        color='orange', linestyle='--'
    )

    # Agregar título y etiquetas
    #plt.title(f"Predicción de {ticker} usando {model_name}", fontsize=16)
    plt.xlabel('Fecha', fontsize=12)
    plt.ylabel('Precio de Cierre', fontsize=12)

    plt.gca().spines["top"].set_visible(False)
    plt.gca().spines["right"].set_visible(False) 
    
    # Mostrar leyenda
    plt.legend()
    
    st.pyplot(plt)
