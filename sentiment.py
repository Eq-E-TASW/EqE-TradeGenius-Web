import streamlit as st
import json
from tavily import TavilyClient
from openai import OpenAI
import pandas as pd
from datetime import datetime
import os
from dotenv import load_dotenv

# Cargar el archivo .env en local
load_dotenv()

# Intentar obtener la clave API desde las variables de entorno locales
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Si no está en las variables de entorno locales, verificar si está en los secretos de Streamlit
if not OPENAI_API_KEY and "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Intentar obtener la clave API desde las variables de entorno locales
TAVILY_API_KEY = os.getenv("TAVILY_API_KEY")

# Si no está en las variables de entorno locales, verificar si está en los secretos de Streamlit
if not TAVILY_API_KEY and "TAVILY_API_KEY" in st.secrets:
    TAVILY_API_KEY = st.secrets["TAVILY_API_KEY"]
    

def get_news_from_tavily(query, max_results=5):
    try:
        client = TavilyClient(api_key=TAVILY_API_KEY)
        search_results = client.search(
            query=query,
            search_depth="advanced",
            max_results=max_results
        )
        
        # Extraer títulos de los resultados
        headlines = []
        for result in search_results['results']:
            if 'title' in result:
                headlines.append(result['title'])
        
        return headlines
    except Exception as e:
        st.error(f"Error en la búsqueda de noticias: {str(e)}")
        return []

def analyze_sentiment(headlines):
    if not headlines:
        return {"analisis": []}
        
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    analysis_prompt = f"""Analiza el sentimiento de los siguientes titulares y clasifícalos como positivo, negativo o neutral. 
    Además, proporciona un puntaje de -1 (muy negativo) a 1 (muy positivo).
    
    Titulares: {headlines}
    
    Responde en formato JSON con la siguiente estructura:
    {{
        "analisis": [
            {{
                "titular": "texto del titular",
                "sentimiento": "positivo/negativo/neutral",
                "puntaje": float,
                "explicacion": "breve explicación del análisis"
            }}
        ]
    }}
    """
    
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=[{"role": "user", "content": analysis_prompt}],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Error en el análisis de sentimientos: {str(e)}")
        return {"analisis": []}

def app():
    st.title("📰 Análisis de Sentimientos en Noticias")
    
    # Input del usuario
    search_query = st.text_input("¿Sobre qué tema quieres analizar noticias?", 
                                placeholder="Ej: tecnología en Latinoamérica")
    
    if st.button("Analizar Noticias"):
        if search_query:
            try:
                with st.spinner("Realizando análisis..."):
                    # Obtener titulares con Tavily
                    headlines = get_news_from_tavily(search_query)
                    
                    if headlines:
                        st.write("Titulares encontrados:", headlines)
                        
                        # Analizar sentimientos con OpenAI
                        results = analyze_sentiment(headlines)
                        
                        if results and 'analisis' in results and results['analisis']:
                            # Crear DataFrame para visualización
                            data = []
                            for headline in results['analisis']:
                                data.append({
                                    'Titular': headline['titular'],
                                    'Sentimiento': headline['sentimiento'],
                                    'Puntaje': headline['puntaje'],
                                    'Explicación': headline['explicacion']
                                })
                            
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
                            st.warning("No se pudo realizar el análisis de sentimientos.")
                    else:
                        st.warning("No se encontraron titulares para analizar.")
                        
            except Exception as e:
                st.error(f"Error durante el análisis: {str(e)}")
        else:
            st.warning("Por favor, ingresa un tema para buscar.")

