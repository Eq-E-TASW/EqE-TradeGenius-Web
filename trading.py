import streamlit as st
import pandas as pd
from sqlalchemy.orm import Session
from utils.database import SessionLocal, get_db
from utils.models import HistoricalData, UserAssets, TradingHistory
from sqlalchemy import desc
import time

def update_current_prices(db: Session):
    """Actualizar los precios actuales de los activos en UserAssets con el último precio de cierre."""
    user_assets = db.query(UserAssets).all()

    for asset in user_assets:
        latest_price_entry = db.query(HistoricalData).filter(
            HistoricalData.symbol == asset.symbol
        ).order_by(desc(HistoricalData.date)).first()

        if latest_price_entry:
            asset.current_price = latest_price_entry.close

    db.commit()

def execute_trade(db: Session, user_id: int, symbol: str, quantity: int):
    """Realizar una operación de compra o venta."""
    latest_price_entry = db.query(HistoricalData).filter(
        HistoricalData.symbol == symbol
    ).order_by(desc(HistoricalData.date)).first()

    if not latest_price_entry:
        return "Error: Símbolo no válido"

    buy_price = latest_price_entry.close

    asset = db.query(UserAssets).filter(
        UserAssets.user_id == user_id,
        UserAssets.symbol == symbol
    ).first()

    if not asset:
        if quantity < 0:
            return "Error: No tienes suficientes acciones para vender"
        asset = UserAssets(
            user_id=user_id,
            symbol=symbol,
            quantity=quantity,
            current_price=buy_price
        )
        db.add(asset)
    else:
        if quantity < 0 and abs(quantity) > asset.quantity:
            return "Error: No tienes suficientes acciones para vender"

        new_quantity = asset.quantity + quantity
        new_price = asset.current_price

        if quantity > 0:
            total_cost = (asset.quantity * asset.current_price) + (quantity * buy_price)
            new_price = total_cost / new_quantity

        asset.quantity = new_quantity
        asset.current_price = new_price

    trade_history = TradingHistory(
        user_id=user_id,
        symbol=symbol,
        quantity=quantity,
        buy_price=buy_price
    )
    db.add(trade_history)
    db.commit()

    return "Operación exitosa: Datos actualizados"

def app():

    db = next(get_db())  # Obtienes la sesión de la base de datos

    st.title("💹 Trading de Acciones")

    # Actualizar precios actuales
    update_current_prices(db)

    # Mostrar inventario del usuario
    user_id = 123  # Asignar un ID de usuario por defecto
    user_assets = db.query(UserAssets).filter(UserAssets.user_id == user_id).all()
    if user_assets:
        data = [
            {
                "Ticker": asset.symbol,
                "Cantidad": asset.quantity,
                "Precio Unitario": asset.current_price,
                "Precio Total": asset.quantity * asset.current_price
            }
            for asset in user_assets
        ]
        df = pd.DataFrame(data)
    else:
        df = pd.DataFrame(columns=["Ticker", "Cantidad", "Precio Unitario", "Precio Total"])

    df = df.loc[:, ~df.columns.str.match('^Unnamed')]

    st.write("#### Inventario Actual:")
    st.dataframe(df, use_container_width=True)

    # Seleccionar ticker
    ticker_options = ["Seleccionar..."] + [result[0] for result in db.query(UserAssets.symbol).filter(UserAssets.user_id == user_id).all()]
    ticker = st.selectbox("Selecciona el ticker para la operación:", ticker_options)

    # Seleccionar cantidad
    amount = st.number_input("Ingrese la cantidad", min_value=1, value=1)
    trade_options = ["Comprar", "Vender"]
    trade = st.selectbox("Selecciona la operación:", trade_options)

    if ticker != "Seleccionar...":
        st.write(f"Detalles de la operación: {trade} {amount} unidades de {ticker}.")
    else:
        st.write("Por favor, selecciona un ticker válido.")

    if "confirm" not in st.session_state:
        st.session_state.confirm = False

    confirm_button = st.button(f"{trade}")

    if confirm_button:
        if ticker == "Seleccionar...":
            st.warning("Por favor, selecciona un ticker antes de continuar.")
        else:
            st.session_state.confirm = True

    if st.session_state.confirm:
        col1, col2 = st.columns(2)
        with col1:
            cancel = st.button("Cancelar", key="cancel_button")
        with col2:
            confirm = st.button("Confirmar", key="final_confirm")

        if cancel:
            st.session_state.confirm = False
            st.warning("Operación cancelada.")
            time.sleep(1)
            st.rerun()

        if confirm:
            quantity = amount if trade == "Comprar" else -amount
            result = execute_trade(db, user_id, ticker, quantity)
            if "Error" in result:
                st.error(result)
            else:
                st.success(result)
            st.session_state.confirm = False
            time.sleep(1)
            st.rerun()