from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from utils.models import PredictionLog
from datetime import datetime

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

# Función para registrar la operación en la base de datos
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

