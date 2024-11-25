import streamlit as st
import requests
import pandas as pd

# Base URL del API
API_BASE_URL = "http://127.0.0.1:8000"  

def get_news_analysis(query, max_results):
    """
    Función para realizar la solicitud al endpoint FastAPI.
    """
    try:
        # Formar la URL del endpoint
        url = f"{API_BASE_URL}/analyze-news"
        # Enviar la solicitud GET con parámetros
        response = requests.get(url, params={"query": query, "max_results": max_results})
        response.raise_for_status()  # Levantar excepciones si la respuesta no es exitosa
        return response.json()  # Devolver el JSON de la respuesta
    except requests.exceptions.RequestException as e:
        st.error(f"Error en la solicitud al API: {str(e)}")
        return None

def app():
    st.title("📰 Análisis de Sentimientos en Noticias")
    
    # Input del usuario para el tema y el número de noticias
    search_query = st.text_input(
        "¿Sobre qué tema quieres analizar noticias?", 
        placeholder="Ej: Bolsa de Valores de Lima"
    )
    max_results = st.number_input(
        "¿Cuántas noticias deseas analizar?",
        min_value=1, max_value=20, value=5, step=1
    )
    
    if st.button("Analizar Noticias"):
        if search_query:
            with st.spinner("Realizando análisis..."):
                # Llamar al API
                results = get_news_analysis(query=search_query, max_results=max_results)
                
                if results and 'analisis' in results:
                    analysis = results['analisis']
                    
                    if analysis:
                        # Crear DataFrame para visualización
                        data = [
                            {
                                'Titular': item['titular'],
                                'Sentimiento': item['sentimiento'],
                                'Puntaje': item['puntaje'],
                                'Explicación': item['explicacion']
                            }
                            for item in analysis
                        ]
                        
                        df = pd.DataFrame(data)
                        
                        # Visualizar resultados
                        st.subheader("Resultados del Análisis")
                        
                        # Mostrar gráfico de sentimientos
                        sentiment_counts = df['Sentimiento'].value_counts()
                        st.bar_chart(sentiment_counts)
                        
                        # Mostrar tabla de resultados
                        st.dataframe(
                            df.style.background_gradient(
                                subset=['Puntaje'],
                                cmap='RdYlGn',
                                vmin=-1,
                                vmax=1
                            ),
                            hide_index=True
                        )
                        
                        # Calcular y mostrar estadísticas
                        avg_sentiment = df['Puntaje'].mean()
                        st.metric(
                            label="Sentimiento Promedio",
                            value=f"{avg_sentiment:.2f}",
                            delta=f"{'Positivo' if avg_sentiment > 0 else 'Negativo' if avg_sentiment < 0 else 'Neutral'}"
                        )
                    else:
                        st.warning("No se encontraron titulares analizados.")
                else:
                    st.warning("No se pudo realizar el análisis.")
        else:
            st.warning("Por favor, ingresa un tema para buscar.")

