import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import random
import difflib
from streamlit_webrtc import webrtc_streamer, AudioProcessorBase
import av
import numpy as np
import tempfile

# Configurar página
st.set_page_config(page_title="Pronunciación Inglés", page_icon="🗣️", layout="centered")

st.title("🗣️ Práctica de Pronunciación en Inglés con Micrófono")
st.markdown("Escucha la frase, repítela en voz alta y evalúa tu pronunciación.")

# Lista de frases
frases = [
    "Hello, how are you?",
    "I would like a cup of coffee.",
    "Can you help me, please?",
    "This is a beautiful day.",
    "I love learning English.",
    "Where is the nearest station?",
    "The weather is nice today.",
    "I have two brothers and one sister.",
    "What time is the meeting?",
    "I am going to the supermarket."
]

# Función para reproducir texto como audio
def reproducir_texto(texto, idioma="en"):
    try:
        tts = gTTS(text=texto, lang=idioma)
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ Error al generar audio: {str(e)}")
        return None

# AudioProcessor personalizado para grabar audio del navegador
class AudioProcessor(AudioProcessorBase):
    def __init__(self):
        self.buffer = []

    def recv(self, frame: av.AudioFrame) -> av.AudioFrame:
        pcm = frame.to_ndarray().flatten().astype(np.int16)
        self.buffer.append(pcm.tobytes())
        return frame

    def get_audio_bytes(self):
        return b"".join(self.buffer)

# Función para comparar palabra por palabra
def comparar_palabras(original, hablado):
    orig = original.lower().split()
    dicho = hablado.lower().split()
    resultado = []

    sm = difflib.SequenceMatcher(None, orig, dicho)
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == "equal":
            for i in range(i1, i2):
                resultado.append(("✅", orig[i]))
        else:
            for i in range(i1, i2):
                resultado.append(("❌", orig[i]))
    return resultado

# Mostrar frase
if "frase_actual" not in st.session_state:
    st.session_state.frase_actual = random.choice(frases)

st.markdown("## 📣 Frase para practicar:")
st.markdown(f"### \"{st.session_state.frase_actual}\"")

# Reproducir pronunciación correcta
audio_correcto = reproducir_texto(st.session_state.frase_actual)
if audio_correcto:
    st.markdown("🔊 Pronunciación correcta:")
    st.audio(audio_correcto, format="audio/mp3")

# Botón para cambiar frase
if st.button("🔄 Cambiar frase"):
    st.session_state.frase_actual = random.choice(frases)
    st.rerun()

# Micrófono del navegador con streamlit-webrtc
st.markdown("## 🎤 Graba tu voz (usa el micrófono)")
ctx = webrtc_streamer(
    key="mic",
    mode="SENDRECV",
    in_audio_enabled=True,
    out_audio_enabled=False,
    audio_processor_factory=AudioProcessor,
    media_stream_constraints={"audio": True, "video": False},
    async_processing=True,
)

# Botón para procesar audio grabado
if ctx.audio_processor and st.button("🧠 Evaluar pronunciación"):
    audio_bytes = ctx.audio_processor.get_audio_bytes()
    if audio_bytes:
        with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as f:
            f.write(audio_bytes)
            audio_path = f.name

        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_path) as source:
            audio = recognizer.record(source)
            try:
                texto_usuario = recognizer.recognize_google(audio, language="en-US")
                st.markdown(f"**🗣 Lo que dijiste:** \"{texto_usuario}\"")

                # Reproducir lo que el sistema entendió
                audio_usuario = reproducir_texto(texto_usuario)
                if audio_usuario:
                    st.markdown("🔁 Tu pronunciación (lo que se entendió):")
                    st.audio(audio_usuario, format="audio/mp3")

                # Comparar y evaluar
                st.markdown("🔍 **Evaluación palabra por palabra:**")
                resultado = comparar_palabras(st.session_state.frase_actual, texto_usuario)

                for estado, palabra in resultado:
                    color = "green" if estado == "✅" else "red"
                    st.markdown(f"<span style='color:{color}'>{estado} {palabra}</span>", unsafe_allow_html=True)

                # Porcentaje general
                aciertos = sum(1 for estado, _ in resultado if estado == "✅")
                total = len(resultado)
                porcentaje = round((aciertos / total) * 100, 2) if total > 0 else 0
                st.markdown(f"📊 **Coincidencia general:** {porcentaje}%")

                if porcentaje >= 85:
                    st.success("🎉 ¡Excelente pronunciación!")
                elif porcentaje >= 60:
                    st.warning("🟡 Aceptable, pero puedes mejorar.")
                else:
                    st.error("❌ Necesitas más práctica.")
            except sr.UnknownValueError:
                st.warning("⚠️ No se entendió lo que dijiste.")
            except Exception as e:
                st.error(f"❌ Error al procesar el audio: {str(e)}")
    else:
        st.warning("⏺️ Aún no se ha grabado audio.")
