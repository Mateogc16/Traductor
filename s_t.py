import os
import streamlit as st
from bokeh.models.widgets import Button
from bokeh.models import CustomJS
from streamlit_bokeh_events import streamlit_bokeh_events
from PIL import Image
import time
import glob

from gtts import gTTS
from googletrans import Translator

# Estética mágica: tonos azul y morado
magic_theme = """
<style>
body {
    background-color: #0b032d;
    color: #d0caff;
    font-family: 'Georgia', serif;
}

h1, h2, h3 {
    color: #cba6f7;
    text-shadow: 0 0 5px #b892ff, 0 0 10px #8f43f8;
}

.stButton>button {
    background: linear-gradient(145deg, #6a00ff, #9c4dff);
    border: 1px solid #d6b3ff;
    color: #ffffff;
    border-radius: 10px;
    padding: 0.6em 1.2em;
    font-weight: bold;
    box-shadow: 0 0 10px #a463ff;
}

.stSelectbox, .stTextInput, .stTextArea {
    background-color: #150034 !important;
    color: #e0dfff !important;
    border: 1px solid #4b0082 !important;
}

.sidebar .sidebar-content {
    background-color: #120a3b;
    color: #dcd6f7;
}

.css-18ni7ap {
    background-color: #120a3b !important;
    border: 1px solid #4b0082 !important;
}

hr {
    border-top: 1px solid #8854d0;
}
</style>
"""

st.markdown(magic_theme, unsafe_allow_html=True)

st.title("El Grimorio de las Lenguas: Conjuros Bífidos")
st.subheader("Invoca tu voz al éter y traduce los hechizos antiguos.")

# Imagen principal temática
image = Image.open('Mago bacano.jpg')  # Puedes cambiar por tu ilustración de hechicería
st.image(image, width=300)

with st.sidebar:
    st.subheader("📜 Cámara de Hechicería")
    st.write(
        "Pulsa el sello mágico, habla tu conjuro y elige los idiomas del grimorio."
    )

st.write("🪄 Presiona el sello encantado y pronuncia tu hechizo:")

stt_button = Button(label="Iniciar encantamiento de escucha 🔮", width=300, height=50)

stt_button.js_on_event("button_click", CustomJS(code="""
    var recognition = new webkitSpeechRecognition();
    recognition.continuous = true;
    recognition.interimResults = true;

    recognition.onresult = function (e) {
        var value = "";
        for (var i = e.resultIndex; i < e.results.length; ++i) {
            if (e.results[i].isFinal) {
                value += e.results[i][0].transcript;
            }
        }
        if (value != "") {
            document.dispatchEvent(new CustomEvent("GET_TEXT", {detail: value}));
        }
    }
    recognition.start();
"""))

result = streamlit_bokeh_events(
    stt_button,
    events="GET_TEXT",
    key="listen",
    refresh_on_update=False,
    override_height=75,
    debounce_time=0
)

if result and "GET_TEXT" in result:
    st.write("📖 Palabras capturadas:")
    st.write(result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except FileExistsError:
        pass

    st.header("🔮 Traduciendo tu conjuro...")

    translator = Translator()
    text = str(result.get("GET_TEXT"))

    in_lang = st.selectbox("Lengua de origen", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))
    out_lang = st.selectbox("Lengua de destino", ("Inglés", "Español", "Bengali", "Coreano", "Mandarín", "Japonés"))

    lang_map = {
        "Inglés": "en",
        "Español": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandarín": "zh-cn",
        "Japonés": "ja"
    }

    input_language = lang_map[in_lang]
    output_language = lang_map[out_lang]

    english_accent = st.selectbox(
        "Acento del conjuro",
        ["Defecto", "Español", "Reino Unido", "Estados Unidos", "Canadá", "Australia", "Irlanda", "Sudáfrica"]
    )

    tld_map = {
        "Defecto": "com",
        "Español": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canadá": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sudáfrica": "co.za"
    }

    tld = tld_map[english_accent]

    def text_to_speech(input_language, output_language, text, tld):
        translation = translator.translate(text, src=input_language, dest=output_language)
        trans_text = translation.text
        tts = gTTS(trans_text, lang=output_language, tld=tld, slow=False)
        try:
            my_file_name = text[0:20]
        except:
            my_file_name = "audio"
        tts.save(f"temp/{my_file_name}.mp3")
        return my_file_name, trans_text

    display_output_text = st.checkbox("Mostrar texto traducido 📝")

    if st.button("Reproducir conjuro 🔊"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("### 🔊 Traducción sonora:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("### 📜 Traducción escrita:")
            st.write(output_text)

    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        now = time.time()
        n_days = n * 86400
        for f in mp3_files:
            if os.stat(f).st_mtime < now - n_days:
                os.remove(f)

    remove_files(7)

