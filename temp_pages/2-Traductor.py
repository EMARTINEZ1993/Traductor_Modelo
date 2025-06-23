import streamlit as st
import speech_recognition as sr
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
from gtts import gTTS
from io import BytesIO

# Configurar la página
st.set_page_config(
    page_title="Traductor de Voz Español-Inglés",
    page_icon="🌍",
    layout="centered"
)

st.title("🎤 Traductor de Voz Español → Inglés")
st.markdown("Habla en español y el sistema lo traducirá automáticamente al inglés con audio.")

# ========== Cargar modelo de traducción ==========
@st.cache_resource
def cargar_modelo():
    model_name = "facebook/nllb-200-distilled-600M"
    tokenizer = AutoTokenizer.from_pretrained(model_name)
    model = AutoModelForSeq2SeqLM.from_pretrained(model_name)

    tokenizer.lang_code_to_id = {
        "spa_Latn": tokenizer.convert_tokens_to_ids("spa_Latn"),
        "eng_Latn": tokenizer.convert_tokens_to_ids("eng_Latn")
    }
    return tokenizer, model

# ========== Captura de voz ==========
def capturar_voz():
    r = sr.Recognizer()
    with sr.Microphone() as source:
        st.info("🎙️ Di algo en español... (Grabando 5 segundos)")
        try:
            audio = r.listen(source, timeout=5, phrase_time_limit=5)
            texto = r.recognize_google(audio, language="es-ES")
            return texto
        except sr.WaitTimeoutError:
            st.warning("⏱️ No se detectó voz a tiempo.")
        except sr.UnknownValueError:
            st.warning("⚠️ No se entendió lo que dijiste.")
        except Exception as e:
            st.error(f"❌ Error al procesar el audio: {str(e)}")
    return None

# ========== Traducción ==========
def traducir_texto(texto_es):
    if not texto_es:
        return None
    try:
        tokenizer, model = cargar_modelo()
        inputs = tokenizer(texto_es, return_tensors="pt", truncation=True)
        traduccion = model.generate(
            **inputs,
            forced_bos_token_id=tokenizer.lang_code_to_id["eng_Latn"]
        )
        return tokenizer.decode(traduccion[0], skip_special_tokens=True)
    except Exception as e:
        st.error(f"❌ Error en traducción: {str(e)}")
        return None

# ========== Texto a voz (en memoria) ==========
def texto_a_voz_stream(texto, idioma="en"):
    try:
        tts = gTTS(text=texto, lang=idioma)
        buffer = BytesIO()
        tts.write_to_fp(buffer)
        buffer.seek(0)
        return buffer
    except Exception as e:
        st.error(f"❌ Error al generar voz: {str(e)}")
        return None

# ========== Interfaz principal ==========
def main():
    st.markdown("---")
    if st.button("🎤 Presiona para hablar", type="primary"):
        with st.spinner("Escuchando..."):
            texto_es = capturar_voz()

        if texto_es:
            st.success(f"**🗣 Texto detectado (ES):** {texto_es}")

            with st.spinner("Traduciendo..."):
                texto_en = traducir_texto(texto_es)

            if texto_en:
                st.success(f"**🇺🇸 Traducción (EN):** {texto_en}")
                
                # Generar y mostrar el audio en el navegador
                audio_buffer = texto_a_voz_stream(texto_en)
                if audio_buffer:
                    st.audio(audio_buffer, format='audio/mp3')

                    if st.button("🔁 Repetir pronunciación"):
                        st.audio(audio_buffer, format='audio/mp3')

if __name__ == "__main__":
    main()
