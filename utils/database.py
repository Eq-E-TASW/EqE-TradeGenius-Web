from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import streamlit as st

SQLALCHEMY_DATABASE_URL="postgresql://postgres:ge-sadvb@34.135.17.9:5432/ge-sadvb-db"

Base = declarative_base()

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Función para obtener la sesión con la base de datos remota
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
