import streamlit as st
import speech_recognition as sr
from gtts import gTTS
from io import BytesIO
import random
import difflib

# Configurar página
st.set_page_config(page_title="Pronunciación Inglés", page_icon="🗣️", layout="centered")

st.title("🗣️ Práctica de Pronunciación en Inglés")
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

# Función para capturar voz en inglés
def capturar_voz_en():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Repite la frase... (grabando 5 segundos)")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            texto = r.recognize_google(audio, language="en-US")
            return texto
        except sr.WaitTimeoutError:
            st.warning("⏱️ Tiempo agotado.")
        except sr.UnknownValueError:
            st.warning("⚠️ No se entendió lo que dijiste.")
        except Exception as e:
            st.error(f"❌ Error al procesar audio: {str(e)}")
    return None

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

# Botón para grabar voz y evaluar
if st.button("🎤 Repetir frase y evaluar"):
    with st.spinner("🎧 Escuchando..."):
        texto_usuario = capturar_voz_en()

    if texto_usuario:
        st.markdown(f"**🗣 Lo que dijiste:** \"{texto_usuario}\"")

        # Reproducir lo que el sistema entendió
        audio_usuario = reproducir_texto(texto_usuario)
        if audio_usuario:
            st.markdown("🔁 Tu pronunciación (lo que se entendió):")
            st.audio(audio_usuario, format="audio/mp3")

        # Comparación palabra por palabra
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

