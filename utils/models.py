from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint, Text
from utils.database import Base  

# Clase que representa los registros de las predicciones realizadas
class PredictionLog(Base):
    __tablename__ = "prediction_log"

    id = Column(Integer, primary_key=True, index=True)
    prediction_time = Column(DateTime, default=datetime.utcnow, index=True)
    ticker = Column(String, index=True)
    model_used = Column(String, index=True)
    predicted_date = Column(DateTime, index=True)
    predicted_close_price = Column(Float)

    def __repr__(self):
        return f"<PredictionLog(ticker={self.ticker}, model={self.model_used}, date={self.predicted_date}, price={self.predicted_close_price})>"

# Clase que representa los datos históricos de los activos financieros
class HistoricalData(Base):
    __tablename__ = "historical_data"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String, index=True)
    open = Column(Float)
    high = Column(Float)
    low = Column(Float)
    close = Column(Float)
    volume = Column(Float)
    date = Column(DateTime, index=True)

    # Evita que el mismo símbolo con la misma fecha se repita
    __table_args__ = (UniqueConstraint('symbol', 'date', name='_symbol_date_uc'),)

#  Clase que representa los activos financieros que posee cada usuario en el sistema
class UserAssets(Base):
    __tablename__ = 'user_assets'

    user_id = Column(Integer, primary_key=True)
    symbol = Column(String, primary_key=True)  
    quantity = Column(Integer, nullable=False)
    current_price = Column(Float, nullable=False)

    def __repr__(self):
        return f"<UserAssets(user_id={self.user_id}, symbol='{self.symbol}', quantity={self.quantity}, current_price={self.current_price})>"

# Clase que representa el historial de transacciones realizadas por los usuarios
class TradingHistory(Base):
    __tablename__ = 'trading_history'

    id = Column(Integer, primary_key=True, autoincrement=True)  # Identificador único para cada transacción
    user_id = Column(Integer, nullable=False)
    symbol = Column(String, nullable=False)
    quantity = Column(Integer, nullable=False)  # Positivo para compras, negativo para ventas
    buy_price = Column(Float, nullable=False)
    date = Column(DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f"<TradingHistory(id={self.id}, user_id={self.user_id}, symbol='{self.symbol}', quantity={self.quantity}, buy_price={self.buy_price}, date={self.date})>"