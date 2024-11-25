import streamlit as st
import pandas as pd
from utils.database import SessionLocal, get_db
from utils.models import HistoricalData
import time
import requests

def app():

    db = next(get_db())  

    st.title("💹 Trading de Acciones")

    #Id de usuario único
    user_id=123

    endpoint_url_get = (
        f"https://tradegeniusbackcloud-registry-194080380757.southamerica-west1.run.app/api/trading/get_assets/{user_id}"
    )

    st.write("#### Inventario Actual:")
    try:
        response_get = requests.get(endpoint_url_get, headers={"accept": "application/json"})
        response_get.raise_for_status()

        data = response_get.json()["Assets"]
        df = pd.DataFrame(data)
        st.dataframe(df, use_container_width=True)

        # Imprimir el total
        st.markdown(
            f"""
            <div style="text-align: right; font-size: 20px;">
                <strong>Total:</strong> {response_get.json()['Total']:.2f}
            </div>
            """, 
            unsafe_allow_html=True
        )
    except requests.exceptions.RequestException as e:
        st.error(f"Error al obtener el inventario actual: {e}")

    # Seleccionar ticker
    ticker_options = ["Seleccionar..."] + [result[0] for result in db.query(HistoricalData.symbol).distinct().all()]
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
            symbol = ticker

             # Crear la operacion
            operation = {
                "user_id": user_id,       
                "symbol": symbol,
                "quantity": quantity
            }

            endpoint_url_post = (
                f"https://tradegeniusbackcloud-registry-194080380757.southamerica-west1.run.app/api/trading/trade"
            )

            try:
                # Hacer la solicitud POST con el body y los headers
                response_post = requests.post(
                    endpoint_url_post, 
                    headers={"accept": "application/json", "Content-Type": "application/json"},
                    json=operation  # Enviar el payload en el cuerpo
                )
                response_post.raise_for_status()  # Levanta una excepción si hay error en la respuesta
                
                # Manejar la respuesta del servidor
                response_data = response_post.json()
                success_message = response_data.get("message", "")
                error_detail = response_data.get("detail", "")

                # Mostrar mensajes según el contenido de la respuesta
                if success_message:
                    st.success(success_message)  # Mensaje de éxito
                elif error_detail:
                    st.error(error_detail)  # Mensaje de error

            except requests.exceptions.RequestException as e:
                # Manejar errores en la solicitud
                st.error(f"Error en la solicitud: {e}")

            st.session_state.confirm = False
            time.sleep(1)
            st.rerun()



