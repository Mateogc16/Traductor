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
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=UnifrakturCook&family=Cinzel+Decorative&display=swap');

    html, body, [class*="css"] {
        background-color: #1e1b1b;
        color: #d4af37;
        font-family: 'Cinzel Decorative', serif;
    }

    h1, h2, h3, h4 {
        font-family: 'UnifrakturCook', cursive;
        color: #d4af37;
        text-shadow: 1px 1px 2px #000;
    }

    .stButton > button {
        background-color: #7b1e1e;
        color: #f0e6d2;
        border: 1px solid #a83232;
        border-radius: 10px;
        padding: 0.75em 1em;
        font-weight: bold;
        font-family: 'Cinzel Decorative', serif;
    }

    .stButton > button:hover {
        background-color: #a83232;
        color: #fff;
    }

    .stSidebar {
        background-color: #2e2a2a;
    }

    .css-1offfwp {
        background-color: #2a2525;
        border: 2px solid #444;
        border-radius: 12px;
        padding: 1em;
    }

    </style>
""", unsafe_allow_html=True)

st.title("\ud83d\udcdc El Grimorio de las Lenguas")
st.subheader("Habla, forastero... y los antiguos hechiceros traducir\u00e1n tus palabras.")

image = Image.open('OIG7.jpg')
st.image(image, width=300)

with st.sidebar:
    st.subheader("\ud83d\udd2e Traductor Arcano")
    st.write("Presiona el bot\u00f3n encantado y, tras la se\u00f1al m\u00e1gica, conjura tu voz. Luego elige los lenguajes del hechizo de traducci\u00f3n.")

st.write("\ud83d\udd61 Invoca tu voz al \u00e9ter. Pulsa el bot\u00f3n encantado para comenzar.")

stt_button = Button(label="\u272a Escuchar el conjuro  \ud83c\udfa4", width=300, height=50)

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
        if ( value != "") {
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
    debounce_time=0)

if result:
    if "GET_TEXT" in result:
        st.write("\ud83d\udcac Palabras capturadas:")
        st.write(result.get("GET_TEXT"))
    try:
        os.mkdir("temp")
    except:
        pass

    st.title("\ud83d\udd0a Hechizo de Voz")
    translator = Translator()
    
    text = str(result.get("GET_TEXT"))
    in_lang = st.selectbox("Lengua de origen", ("Ingl\u00e9s", "Espa\u00f1ol", "Bengali", "Coreano", "Mandar\u00edn", "Japon\u00e9s"))
    input_language = {
        "Ingl\u00e9s": "en",
        "Espa\u00f1ol": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandar\u00edn": "zh-cn",
        "Japon\u00e9s": "ja",
    }[in_lang]

    out_lang = st.selectbox("Lengua de destino", ("Ingl\u00e9s", "Espa\u00f1ol", "Bengali", "Coreano", "Mandar\u00edn", "Japon\u00e9s"))
    output_language = {
        "Ingl\u00e9s": "en",
        "Espa\u00f1ol": "es",
        "Bengali": "bn",
        "Coreano": "ko",
        "Mandar\u00edn": "zh-cn",
        "Japon\u00e9s": "ja",
    }[out_lang]

    english_accent = st.selectbox("Acento del conjuro", ("Defecto", "Espa\u00f1ol", "Reino Unido", "Estados Unidos", "Canada", "Australia", "Irlanda", "Sud\u00e1frica"))
    tld = {
        "Defecto": "com",
        "Espa\u00f1ol": "com.mx",
        "Reino Unido": "co.uk",
        "Estados Unidos": "com",
        "Canada": "ca",
        "Australia": "com.au",
        "Irlanda": "ie",
        "Sud\u00e1frica": "co.za"
    }[english_accent]

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

    display_output_text = st.checkbox("\ud83d\udcd6 Revelar el texto traducido")

    if st.button("\u2694\ufe0f Invocar traducci\u00f3n"):
        result, output_text = text_to_speech(input_language, output_language, text, tld)
        audio_file = open(f"temp/{result}.mp3", "rb")
        audio_bytes = audio_file.read()
        st.markdown(f"## \ud83d\udd0a Hechizo pronunciado:")
        st.audio(audio_bytes, format="audio/mp3", start_time=0)

        if display_output_text:
            st.markdown("## \ud83d\udcda Escritura traducida:")
            st.write(f" {output_text}")

    def remove_files(n):
        mp3_files = glob.glob("temp/*mp3")
        if len(mp3_files) != 0:
            now = time.time()
            n_days = n * 86400
            for f in mp3_files:
                if os.stat(f).st_mtime < now - n_days:
                    os.remove(f)
                    print("Deleted ", f)

    remove_files(7)

    


