from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import streamlit as st
import os
from dotenv import load_dotenv

# Cargar el archivo .env local
load_dotenv()

# Intentar obtener la clave API desde las variables de entorno locales
SQLALCHEMY_DATABASE_URL = os.getenv("SQLALCHEMY_DATABASE_URL")

# Si no está en las variables de entorno locales, verificar si está en los secretos de Streamlit 
if not SQLALCHEMY_DATABASE_URL and "SQLALCHEMY_DATABASE_URL" in st.secrets:
    SQLALCHEMY_DATABASE_URL = st.secrets["SQLALCHEMY_DATABASE_URL"]

# Definir Base directamente en este archivo
Base = declarative_base()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
