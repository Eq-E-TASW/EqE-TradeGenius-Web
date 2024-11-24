import streamlit as st
from openai import OpenAI
import time
import os
from dotenv import load_dotenv

# Cargar el archivo .env en local
load_dotenv()

# Intentar obtener la clave API desde las variables de entorno locales
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# Si no está en las variables de entorno locales, verificar si está en los secretos de Streamlit
if not OPENAI_API_KEY and "OPENAI_API_KEY" in st.secrets:
    OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]

# Configurar el cliente de OpenAI
client = OpenAI(api_key=OPENAI_API_KEY)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .stTextInput {
        position: fixed;
        bottom: 3rem;
        background-color: white;
        padding: 10px;
        z-index: 100;
    }
    .stButton {
        position: fixed;
        bottom: 1rem;
        z-index: 100;
    }
    .message-container {
        margin-bottom: 5rem;
        padding-bottom: 3rem;
        overflow-y: auto;
        max-height: calc(100vh - 200px);
    }
    div[data-testid="stVerticalBlock"] {
        padding-bottom: 5rem;
    }
    </style>
""", unsafe_allow_html=True)

def initialize_session_state():
    """Initialize session state variables"""
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {"sender": "Bot", "message": "¡Hola! Soy Finn, tu asistente chatbot en temas financieros. ¿En qué puedo ayudarte hoy?"}
        ]
    if 'input' not in st.session_state:
        st.session_state.input = ""

def send_message(user_input):
    if not user_input.strip():
        return
    
    try:
        # Agregar mensaje del usuario
        st.session_state.messages.append({"sender": "User", "message": user_input})
        
        # Crear el historial de mensajes para la API
        api_messages = [{"role": "system", "content": "Eres Finn, un asistente amigable que ayuda con información financiera y general."}]
        for msg in st.session_state.messages[:-1]:
            role = "user" if msg["sender"] == "User" else "assistant"
            api_messages.append({"role": role, "content": msg["message"]})
        api_messages.append({"role": "user", "content": user_input})
        
        # Obtener respuesta de OpenAI usando la nueva API
        response = client.chat.completions.create(
            model="gpt-4-turbo-preview",
            messages=api_messages
        )
        
        bot_message = response.choices[0].message.content
        st.session_state.messages.append({"sender": "Bot", "message": bot_message})
        
    except Exception as e:
        error_message = f"Error: {str(e)}"
        st.session_state.messages.append({"sender": "Bot", "message": error_message})

def on_input_change():
    user_input = st.session_state.text_input
    if user_input:
        send_message(user_input)
        st.session_state.text_input = ""  # Clear the input
        time.sleep(0.1)  # Pequeña pausa para asegurar que los mensajes se actualicen

def app():
    initialize_session_state()
    
    st.title("🤖💬 Finn - El Gurú del Business")
    
    # Contenedor para los mensajes
    chat_container = st.container()
    
    # Mostrar mensajes
    with chat_container:
        st.markdown('<div class="message-container">', unsafe_allow_html=True)
        for msg in st.session_state.messages:
            if msg["sender"] == "User":
                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: flex-end;'>
                        <div style='background-color: #2b313e; color: white; padding: 12px 20px; 
                        border-radius: 15px; max-width: 70%; margin: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>
                            {msg['message']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f"""
                    <div style='display: flex; justify-content: flex-start;'>
                        <div style='background-color: #f0f2f6; color: black; padding: 12px 20px; 
                        border-radius: 15px; max-width: 70%; margin: 5px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1);'>
                            {msg['message']}
                        </div>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Área de entrada
    st.text_input(
        "",
        placeholder="Escribe tu mensaje aquí...",
        key="text_input",
        on_change=on_input_change
    )

