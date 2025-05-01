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

# Estilo medieval oscuro
page_bg_img = """
<style>
body {
background-color: #0d0d0d;
color: #e0dccc;
font-family: 'Palatino Linotype', 'Book Antiqua', Palatino, serif;
}
h1, h2, h3 {
color: #c9aa71;
text-shadow: 2px 2px 2px black;
}
.css-18ni7ap {
background-color: #1a1a1a !important;
border: 1px solid #555 !important;
}
.stButton>button {
background-color: #5c3b19;
color: #f0e6d2;
border-radius: 12px;
border: 1px solid #a67c52;
}
.stSelectbox, .stTextInput {
background-color: #1f1f1f !important;
color: #e0dccc !important;
}
</style>
"""

st.markdown(page_bg_img, unsafe_allow_html=True)

st.title("El Grimorio de las Lenguas")
st.subheader("Invoca el hechizo de la traducción hablada...")

image = Image.open('Mago bacano.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("Panel de Hechicería")
    st.write(
        "Presiona el botón, habla la frase mágica y selecciona la lengua a la que deseas traducir."
    )

st.write("Presiona el botón encantado y pronuncia tu conjuro:")

stt_button = Button(label="Iniciar encantamiento de escucha", width=300, height=50)

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
    st.write("📖 Palabras mágicas capturadas:")
    st.write(result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except:
        pass

    st.header("Traduciendo los conjuros...")

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

    display_output_text = st.checkbox("Mostrar el conjuro traducido")

    if st.button("Reproducir traducción"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown("🔊 Traducción sonora:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("📜 Traducción escrita:")
            st.write(output_text)

    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)

    remove_files(7)

