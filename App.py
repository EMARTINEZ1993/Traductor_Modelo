import streamlit as st
import speech_recognition as sr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from gtts import gTTS
import os
import time

# Configuración de la página
st.set_page_config(
    page_title="Traductor de Voz Español-Inglés",
    page_icon="🌍",
    layout="centered"
)

# Título de la aplicación
st.title("🎤 Traductor de Voz Español → Inglés")
st.markdown("""
Habla en español y el sistema lo traducirá a inglés automáticamente.
""")
