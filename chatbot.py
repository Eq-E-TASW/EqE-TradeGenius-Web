import streamlit as st
import time
import requests

# URL base 
BASE_API_URL = "https://tradegeniusbackcloud-registry-194080380757.southamerica-west1.run.app/api/chatbot" 

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
    """Initialize session state variables."""
    if 'messages' not in st.session_state:
        # Obtener historial de mensajes desde la API
        try:
            response = requests.get(f"{BASE_API_URL}/messages")
            response.raise_for_status()
            messages = response.json().get("messages", [])
            st.session_state.messages = messages or [{"sender": "Bot", "message": "¡Hola! Soy Finn, tu asistente chatbot en temas financieros. ¿En qué puedo ayudarte hoy?"}]
        except Exception as e:
            st.session_state.messages = [{"sender": "Bot", "message": f"Error al cargar historial: {e}"}]
    if 'input' not in st.session_state:
        st.session_state.input = ""

def send_message(user_input):
    if not user_input.strip():
        return

    pass

    try:
        # Enviar mensaje a la API
        payload = {"message": user_input}
        response = requests.post(f"{BASE_API_URL}/send-message", json=payload)
        response.raise_for_status()

        # Obtener la respuesta del bot desde la API
        api_messages = response.json().get("messages", [])
        st.session_state.messages.extend(api_messages[-2:])  # Añadir el último mensaje enviado y recibido
    except Exception as e:
        error_message = f"Error: {str(e)}"
        st.session_state.messages.append({"sender": "Bot", "message": error_message})

def on_input_change():
    user_input = st.session_state.text_input
    if user_input:
        send_message(user_input)
        st.session_state.text_input = "" 
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

