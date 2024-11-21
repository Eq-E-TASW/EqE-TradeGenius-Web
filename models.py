from datetime import datetime
from sqlalchemy import Column, Integer, String, Float, DateTime, UniqueConstraint
from database import Base  

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

