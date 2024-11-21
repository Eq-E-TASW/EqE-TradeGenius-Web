import streamlit as st
from streamlit_option_menu import option_menu
import firebase_admin
from firebase_admin import credentials, auth
import requests  # Para interactuar con Firebase REST API
import trading, chatbot, home, prediction, sentiment

# Configuración de la página
#st.set_page_config(page_title="G7-SADVB", page_icon="📈")

# Configuración de Firebase
if not firebase_admin._apps:
    try:
        firebase_cred = credentials.Certificate("sistematradingapp-firebase-adminsdk-a30zu-c2dfc2f4b7.json")
        firebase_admin.initialize_app(firebase_cred)
    except Exception as e:
        st.error(f"Error al inicializar Firebase: {e}")

# Inicializar estado de sesión si no existe
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
    st.session_state["user_email"] = None
    st.session_state["id_token"] = None  # Token del usuario

# Firebase API Key (de tu consola de Firebase)
API_KEY = "AIzaSyAN5U_DQyn7ISRhSSNIWCF18znnAdoYXf0"

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
                menu_title='SADVB',
                options=['Inicio', 'Predicción', 'Trading', 'Sentimiento','Chatbot'],
                icons=['house-fill', 'activity', 'arrow-left-right','emoji-smile','chat-text-fill'],
                menu_icon='box-fill',
                default_index=0,
                styles={
                    "container": {"padding": "5!important", "background-color": "black"},
                    "icon": {"color": "white", "font-size": "23px"},
                    "nav-link": {"color": "white", "font-size": "20px", "--hover-color": "blue"},
                    "nav-link-selected": {"background-color": "#02ab21"},
                }
            )
            btnSalir = st.button("Salir", type="primary")
            if btnSalir:
                st.session_state["logged_in"] = False
                st.session_state["user_email"] = None
                st.session_state["id_token"] = None
                st.rerun()

        # Lógica para cada sección del menú
        if app == "Inicio":
            home.app()
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
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {
        "email": email,
        "password": password,
        "returnSecureToken": True
    }

    try:
        response = requests.post(url, json=payload)
        if response.status_code == 200:
            # Credenciales correctas
            return response.json()  # Contiene idToken, refreshToken, etc.
        else:
            # Error en las credenciales
            return {"error": response.json().get("error", {}).get("message", "Error desconocido")}
    except Exception as e:
        return {"error": str(e)}

# Función de login
def login():
    st.title('Bienvenido a SADVB 😎')
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
