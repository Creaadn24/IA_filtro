from flask import Flask, request, render_template, send_file
from rembg import remove
from PIL import Image
import os
import datetime

app = Flask(__name__)

# Crear la carpeta 'updates' si no existe
if not os.path.exists('updates'):
    os.makedirs('updates')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/procesar_imagenes', methods=['POST'])
def procesar_imagenes():
    persona = request.files['persona']
    fondo = request.files['fondo']

    input_path = "persona.png"
    output_path = "persona_sin_fondo.png"
    fondo_path = "fondo.png"

    # Generar un nombre único para la imagen resultado
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    resultado_path = os.path.join('updates', f'imagen_final_{timestamp}.png')

    persona.save(input_path)
    fondo.save(fondo_path)

    try:
        # 1. Remover el fondo
        input_image = Image.open(input_path)
        output_image = remove(input_image)
        output_image.save(output_path, format="PNG")

        # 2. Abrir las imágenes y convertirlas a RGBA
        persona_sin_fondo = Image.open(output_path).convert("RGBA")
        fondo = Image.open(fondo_path).convert("RGBA")

        # 3. Redimensionar la persona para que sea un poco más grande
        ancho_original, alto_original = persona_sin_fondo.size
        nuevo_ancho = int(ancho_original * 0.15)  # Ajuste del tamaño al 15% del original
        nuevo_alto = int(alto_original * 0.15)
        persona_sin_fondo = persona_sin_fondo.resize((nuevo_ancho, nuevo_alto))

        # 4. Calcular la posición para colocar la persona en la esquina inferior derecha
        posicion = (fondo.width - persona_sin_fondo.width, fondo.height - persona_sin_fondo.height)

        # 5. Pegar la persona sobre el fondo
        fondo.paste(persona_sin_fondo, posicion, persona_sin_fondo)

        # 6. Guardar la imagen final en la carpeta 'updates' con un nombre único
        fondo.save(resultado_path, format="PNG")

        # Eliminar las imágenes temporales
        os.remove(input_path)
        os.remove(output_path)
        os.remove(fondo_path)

        return send_file(resultado_path, mimetype='image/png')

    except FileNotFoundError:
        return "Error: No se encontró alguna de las imágenes. Revisa las rutas."
    except Exception as e:
        return f"Ocurrió un error: {e}"

if __name__ == '__main__':
    app.run(debug=True)
