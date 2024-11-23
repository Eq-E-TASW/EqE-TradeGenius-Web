import streamlit as st
from streamlit_option_menu import option_menu
import requests  
import os
from dotenv import load_dotenv

# Configuración de la página
st.set_page_config(page_title="G7-SADVB", page_icon="📈")

import trading, chatbot, dashboard, prediction, sentiment

# Inicializar estado de sesión si no existe
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["id_token"] = None  # Token del usuario

# Cargar el archivo .env local
load_dotenv()

# Intentar obtener la clave API desde las variables de entorno locales
FIREBASE_API_KEY = os.getenv("FIREBASE_API_KEY")

# Si no está en las variables de entorno locales, verificar si está en los secretos de Streamlit
if not FIREBASE_API_KEY and "FIREBASE_API_KEY" in st.secrets:
    FIREBASE_API_KEY = st.secrets["FIREBASE_API_KEY"]

# Clase principal de la aplicación
class MultiApp:
    def __init__(self):
        self.apps = []

    def add_app(self, title, func):
        self.apps.append({"title": title, "function": func})

    def run(self):
        # Barra lateral con el menú
        with st.sidebar:
            app = option_menu(
                menu_title='TradeGenius',
                options=['Dashboard', 'Predicción', 'Trading', 'Sentimiento','Chatbot'],
                icons=['bar-chart-line', 'activity', 'arrow-left-right','emoji-smile','chat-text'],
                menu_icon="none",
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": "black"},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                    "menu-title": {"font-size": "2em","font-weight": "bold","color": "#7289da",
                                   "text-align": "center","margin-bottom": "10px","padding": "10px 0",
                                   }
                }
            )
            btnSalir = st.button("Salir", type="primary")
            if btnSalir:
                st.session_state["logged_in"] = False
                st.session_state["user_email"] = None
                st.session_state["id_token"] = None
                st.rerun()

        # Lógica para cada sección del menú
        if app == "Dashboard":
            dashboard.app()
        elif app == "Predicción":
            prediction.app()
        elif app == "Trading":
            trading.app()
        elif app == "Sentimiento":
            sentiment.app()
        elif app == "Chatbot":
            chatbot.app()

# Función para autenticar usuario con Firebase REST API
def authenticate_user(email, password):
    """
    Verifica si las credenciales del usuario son válidas mediante Firebase REST API.
    """
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={FIREBASE_API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            # Credenciales correctas
            return response.json()  
        else:
            # Error en las credenciales
            return {"error": response.json().get("error", {}).get("message", "Error desconocido")}
    except Exception as e:
        return {"error": str(e)}

# Función de login
def login():
    st.markdown(
        """
        <h1 style='text-align: center;'>
            Bienvenido a <span style="color: #7289da;">TradeGenius</span>
        </h1>
        """, 
        unsafe_allow_html=True
    )


    col1, col2 = st.columns([1.5, 2])  

    with col1:
        # Mostrar la imagen
        st.image("images/logoApp.png")

    with col2:
        st.subheader("Ingrese sus credenciales")
        email = st.text_input("Correo electrónico")
        password = st.text_input("Contraseña", type="password")
        login_button = st.button("Iniciar sesión")

        if login_button:
            auth_result = authenticate_user(email, password)
            if "idToken" in auth_result:
                st.session_state["logged_in"] = True
                st.session_state["user_email"] = auth_result["email"]
                st.session_state["id_token"] = auth_result["idToken"]
                st.rerun()
            else:
                st.error(f"Error al iniciar sesión: {auth_result.get('error')}")

if not st.session_state["logged_in"]:
    login()
else:
    app = MultiApp()
    app.run()
