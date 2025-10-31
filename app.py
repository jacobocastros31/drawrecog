import os
import base64
import streamlit as st
from openai import OpenAI
from PIL import Image
import numpy as np
from streamlit_drawable_canvas import st_canvas

# --- CONFIGURACIÓN DE LA PÁGINA ---
st.set_page_config(
    page_title="Tablero Inteligente",
    page_icon="🧠",
    layout="centered"
)

# --- TÍTULO PRINCIPAL ---
st.title("🧠 Tablero Inteligente")
st.write(
    "Dibuja un boceto y deja que la inteligencia artificial lo interprete. "
    "Esta aplicación demuestra la capacidad de las máquinas para **comprender dibujos hechos a mano**."
)

# --- SIDEBAR ---
with st.sidebar:
    st.header("ℹ️ Acerca de esta app")
    st.write(
        "Esta herramienta utiliza inteligencia artificial (modelo **GPT-4o**) para analizar y describir imágenes. "
        "Puedes dibujar directamente en el panel o subir una imagen si lo deseas."
    )
    stroke_width = st.slider("✏️ Ancho de línea", 1, 30, 5)
    stroke_color = st.color_picker("🎨 Color de trazo", "#000000")
    bg_color = st.color_picker("🖼️ Color de fondo", "#FFFFFF")

# --- CANVAS PARA DIBUJAR ---
st.subheader("🖌️ Dibuja tu boceto")
st.write("Usa el panel de abajo para crear tu dibujo y luego presiona **Analizar imagen** para ver la descripción generada.")

canvas_result = st_canvas(
    fill_color="rgba(255, 165, 0, 0.3)",
    stroke_width=stroke_width,
    stroke_color=stroke_color,
    background_color=bg_color,
    height=350,
    width=450,
    drawing_mode="freedraw",
    key="canvas",
)

# --- CLAVE API ---
st.divider()
st.markdown("### 🔑 Conexión con OpenAI")
ke = st.text_input("Ingresa tu clave de API de OpenAI:", type="password")

if ke:
    os.environ["OPENAI_API_KEY"] = ke
    client = OpenAI(api_key=ke)
else:
    client = None

# --- BOTÓN DE ANÁLISIS ---
analyze_button = st.button("🔍 Analizar imagen")

# --- FUNCIÓN PARA CODIFICAR LA IMAGEN ---
def encode_image_to_base64(image_path):
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode("utf-8")

# --- PROCESAMIENTO DE LA IMAGEN ---
if analyze_button:
    if client is None:
        st.warning("⚠️ Por favor, ingresa tu clave de API antes de continuar.")
    elif canvas_result.image_data is None:
        st.warning("⚠️ Dibuja algo en el panel antes de analizar.")
    else:
        with st.spinner("🧩 Analizando el dibujo..."):
            # Guardar la imagen del canvas
            input_image = Image.fromarray(np.array(canvas_result.image_data).astype("uint8"), "RGBA")
            image_path = "dibujo.png"
            input_image.save(image_path)

            # Codificar en base64
            base64_image = encode_image_to_base64(image_path)

            # Solicitud a la API
            try:
                prompt_text = "Describe brevemente en español lo que ves en la imagen."
                response = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=[
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt_text},
                                {"type": "image_url", "image_url": f"data:image/png;base64,{base64_image}"},
                            ],
                        }
                    ],
                    max_tokens=300
                )

                description = response.choices[0].message.content
                st.success("✅ Análisis completado")
                st.markdown("### 🧾 Descripción generada:")
                st.write(description)

            except Exception as e:
                st.error(f"Ocurrió un error al analizar la imagen: {e}")
