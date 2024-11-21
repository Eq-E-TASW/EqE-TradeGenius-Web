import streamlit as st
from sqlalchemy.orm import Session
from database import SessionLocal, get_db
from models import HistoricalData
from funtions import get_date_range
from sqlalchemy import desc, func, and_
import matplotlib.pyplot as plt
from datetime import datetime, timedelta

def app():
    
    # Mostrar encabezados
    st.subheader("👋 Bienvenid@")
    st.markdown("---")
    st.title("📊 Visualización de Precios")

    # Solicitar al usuario los símbolos de valor a analizar, separados por coma
    ticker_txt = st.text_input("Ingrese los símbolos de valor a analizar (separados por coma)")

    tickers = []

    # Procesar la entrada cuando el usuario ingresa datos
    if ticker_txt:
        # Convertir la cadena de texto en una lista de símbolos, eliminando espacios extra
        tickers = [ticker.strip() for ticker in ticker_txt.split(',')]

    # Input para el número (cantidad)
    amount = st.number_input("Ingrese la cantidad", min_value=1, value=1)

    # Input para la unidad (semanas, meses, años)
    unit = st.radio(
        "Seleccione la unidad de tiempo",
        options=["Semanas", "Meses", "Años"],
        index=2  # Selecciona por defecto "Años"
    )

    unit_dict = {
        "Semanas": "weeks",
        "Meses": "months",
        "Años": "years",
    }

    # Traducir la selección del usuario a inglés
    unit = unit_dict.get(unit, "Unknown")

    start_date, end_date = get_date_range(amount, unit)

    # Solicitar al usuario que seleccione el tipo de precio
    price_options = ["Apertura", "Más alto", "Más bajo", "Cierre"]
    price_type = st.selectbox("Selecciona el tipo de precio que deseas analizar:", price_options)

    precio_dict = {
        "Apertura": "open",
        "Más alto": "high",
        "Más bajo": "low",
        "Cierre": "close",
    }

    # Traducir la selección del usuario a inglés
    price_type = precio_dict.get(price_type, "Unknown")
    
    st.markdown("---")
    st.subheader('Evolución Histórica de Precios')

    def show_historical_data():
        db = next(get_db())  # Obtienes la sesión de la base de datos
        
        data_found = False

        # Crear el gráfico
        plt.figure(figsize=(10, 6))
        
        # Si solo hay un ticker, usar sombreado
        if len(tickers) == 1:
            ticker = tickers[0]
            
            # Consultar los datos de la base de datos para el único ticker
            data = db.query(HistoricalData.date, getattr(HistoricalData, price_type)).filter(
                and_(
                    HistoricalData.symbol == ticker,
                    HistoricalData.date >= start_date,
                    HistoricalData.date <= end_date
                )
            ).order_by(HistoricalData.date).all()
            
            data_found = True

            # Extraer datos de fechas y precios
            dates = [entry.date for entry in data]
            prices = [getattr(entry, price_type) for entry in data]
            min_valor = min(prices)

            # Obtener el último valor y el valor pico
            last_value = prices[-1]
            peak_value = max(prices)  # o min(prices) si prefieres el valor mínimo
        
            last_date = dates[-1]
            peak_date = dates[prices.index(peak_value)]  # Obtener la fecha del valor pico
        
            # Trazar la línea para el único ticker con sombreado
            plt.plot(dates, prices, color="blue", label=ticker)
            plt.fill_between(dates, prices, min_valor, color="lightblue", alpha=0.4)
            
            # Agregar anotaciones con flechas
            # Ajustar la posición del texto dependiendo de la unidad
            if unit == "years" and amount == 1: 
                xytext_last = (last_date, last_value + 6)
                if (abs((peak_date - last_date).days) <= 2):
                    xytext_peak = (peak_date - timedelta(days=30), peak_value + 6)
                else:
                    xytext_peak = (peak_date, peak_value + 6)
            elif unit == "months" and amount == 6:
                xytext_last = (last_date, last_value + 6)
                if (abs((peak_date - last_date).days) <= 2):
                    xytext_peak = (peak_date - timedelta(days=15), peak_value + 6)
                else:
                    xytext_peak = (peak_date, peak_value + 6)
            elif unit == "months" and amount == 1:
                xytext_last = (last_date, last_value + 2)
                if (abs((peak_date - last_date).days) <= 1):
                    xytext_peak = (peak_date - timedelta(days=2), peak_value + 2)
                else:
                    xytext_peak = (peak_date, peak_value + 2)
            elif unit == "weeks" and amount == 1:
                xytext_last = (last_date, last_value + 0.5)
                if (abs((peak_date - last_date).days) == 0):
                    xytext_peak = (peak_date - timedelta(hours=12), peak_value + 0.5)
                else:
                    xytext_peak = (peak_date, peak_value + 0.5)
            else:
                xytext_last = (last_date, last_value + 6)
                xytext_peak = (peak_date, peak_value + 6)


            # Anotación para el último valor
            plt.annotate(
                f'{last_value:.1f}', 
                xy=(last_date, last_value), 
                xytext=xytext_last,  # Ajusta la posición del texto
                fontsize=11, 
                color='red', 
                ha='center', 
                va='center', 
                fontweight='semibold',
                arrowprops=dict(facecolor='red', arrowstyle='->')
            )

            # Anotación para el valor pico
            plt.annotate(
                f'{peak_value:.1f}', 
                xy=(peak_date, peak_value), 
                xytext=xytext_peak,  # Ajusta la posición del texto
                fontsize=11, 
                color='black', 
                ha='center', 
                va='bottom', 
                fontweight='semibold',
                arrowprops=dict(facecolor='black', arrowstyle='->')
            )
        
        else:
            colors = ["blue", "green", "red", "orange", "purple"]
            for idx, ticker in enumerate(tickers):
                # Consultar los datos de la base de datos para cada ticker
                data = db.query(HistoricalData.date, getattr(HistoricalData, price_type)).filter(
                    and_(
                        HistoricalData.symbol == ticker,
                        HistoricalData.date >= start_date,
                        HistoricalData.date <= end_date
                    )
                ).order_by(HistoricalData.date).all()
                
                if not data:
                    continue  # Si no hay datos para el ticker, saltarlo
                
                data_found = True

                # Extraer datos de fechas y precios
                dates = [entry.date for entry in data]
                prices = [getattr(entry, price_type) for entry in data]

                # Obtener el último valor y el valor pico
                last_value = prices[-1]
                peak_value = max(prices)  
        
                last_date = dates[-1]
                peak_date = dates[prices.index(peak_value)]  # Obtener la fecha del valor pico

                # Trazar la línea para cada ticker sin sombreado
                plt.plot(dates, prices, color=colors[idx % len(colors)], label=ticker)
                plt.fill_between(dates, prices, color=colors[idx % len(colors)], alpha=0.1)

                # Agregar una leyenda
                plt.legend(title="Tickers", bbox_to_anchor=(0.5, 1.01), loc='lower center', ncol=len(tickers))

                # Agregar anotaciones con flechas
                # Ajustar la posición del texto dependiendo de la unidad
                if unit == "years" and amount == 1: 
                    xytext_last = (last_date, last_value + 20)
                    if (abs((peak_date - last_date).days) <= 20):
                        xytext_peak = (peak_date - timedelta(days=30), peak_value + 6)
                    else:
                        xytext_peak = (peak_date, peak_value + 10)
                elif unit == "months" and amount == 6:
                    xytext_last = (last_date, last_value + 20)
                    if (abs((peak_date - last_date).days) <= 3):
                        xytext_peak = (peak_date - timedelta(days=15), peak_value + 6)
                    else:
                        xytext_peak = (peak_date, peak_value + 10)
                elif unit == "months" and amount == 1:
                    xytext_last = (last_date, last_value + 20)
                    if (abs((peak_date - last_date).days) <= 1):
                        xytext_peak = (peak_date - timedelta(days=2), peak_value + 6)
                    else:
                        xytext_peak = (peak_date, peak_value + 10)
                elif unit == "weeks" and amount == 1:
                    xytext_last = (last_date, last_value + 20)
                    if (abs((peak_date - last_date).days) == 0):
                        xytext_peak = (peak_date - timedelta(hours=12), peak_value + 6)
                    else:
                        xytext_peak = (peak_date, peak_value + 0.5)
                else:
                    xytext_last = (last_date, last_value + 6)
                    xytext_peak = (peak_date, peak_value + 6)


                # Anotación para el último valor
                plt.annotate(
                    f'{last_value:.1f}', 
                    xy=(last_date, last_value), 
                    xytext=xytext_last,  # Ajusta la posición del texto
                    fontsize=11, 
                    color='red', 
                    ha='center', 
                    va='center', 
                    fontweight='semibold',
                    arrowprops=dict(facecolor='red', arrowstyle='->')
                )

                # Anotación para el valor pico
                plt.annotate(
                    f'{peak_value:.1f}', 
                    xy=(peak_date, peak_value), 
                    xytext=xytext_peak,  # Ajusta la posición del texto
                    fontsize=11, 
                    color='black', 
                    ha='center', 
                    va='bottom', 
                    fontweight='semibold',
                    arrowprops=dict(facecolor='black', arrowstyle='->')
                )

        if not data_found:
            st.warning("No se encontraron datos para los criterios seleccionados.")
            return 
        
        if len(tickers) == 1:
            st.write(f"**Ticker:** {tickers[0]}")
        else:
            st.write(f"**Tickers:** {', '.join(tickers)}")
    
        st.write(f"Datos registrados desde {start_date} hasta {end_date}")

        # Configurar el gráfico
        plt.ylabel(f"Precio ({price_type.capitalize()})")
        plt.gca().spines["top"].set_visible(False)
        plt.gca().spines["right"].set_visible(False) 
        st.pyplot(plt)
    
    with st.spinner("Generando gráfico, por favor espera..."):
        show_historical_data()

    st.subheader('Volumen Actual de Transacciones ')

    def plot_last_volume():

        db = next(get_db())  # Obtienes la sesión de la base de datos
        
        data_found = False

        # Colores para los tickers
        colors = ["blue", "green", "red", "orange", "purple"]

        # Datos para graficar
        volumes = []
        dates = []

        for ticker in tickers:
            # Consultar el último registro de volumen para cada ticker
            result = db.query(HistoricalData.volume, HistoricalData.date).filter(
                HistoricalData.symbol == ticker
            ).order_by(HistoricalData.date.desc()).first()
            
            if result:
                data_found = True
                volumes.append(result.volume)
                dates.append(result.date.strftime("%Y-%m-%d"))
            else:
                volumes.append(0)  # Sin datos
                dates.append("N/A")


        if not data_found:
            st.warning("No se encontraron datos para los criterios seleccionados.")
            return
        
        # Crear el gráfico
        plt.figure(figsize=(10, 6))
        bars = plt.bar(tickers, volumes, color=colors, alpha=0.8)

        # Agregar etiquetas con las fechas en cada barra
        for bar, date in zip(bars, dates):
            height = bar.get_height()
            plt.text(bar.get_x() + bar.get_width() / 2, height + 1, date, ha="center", fontsize=10)

        # Configuración del gráfico
        plt.xlabel("Tickers")
        plt.ylabel("Volumen")
        plt.xticks(rotation=45)
        plt.gca().spines["top"].set_visible(False)
        plt.gca().spines["right"].set_visible(False) 

        # Mostrar en Streamlit
        st.pyplot(plt)

    with st.spinner("Generando gráfico, por favor espera..."):
        plot_last_volume()

    
    



