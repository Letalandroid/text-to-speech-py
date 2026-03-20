import os
import uuid
import threading
import time
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import FileResponse
from gtts import gTTS
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Configuración desde .env
API_KEY = os.getenv("API_KEY")
AUDIO_DIR = "audios"
MAX_FILE_AGE = int(os.getenv("MAX_FILE_AGE", 60))

# Validación básica
if not API_KEY:
    raise ValueError("API_KEY no está definida en el .env")

# Crear carpeta si no existe
os.makedirs(AUDIO_DIR, exist_ok=True)

app = FastAPI()

def limpiar_audios():
    ahora = time.time()
    for archivo in os.listdir(AUDIO_DIR):
        ruta = os.path.join(AUDIO_DIR, archivo)
        try:
            if os.path.isfile(ruta):
                edad = ahora - os.path.getmtime(ruta)
                if edad > MAX_FILE_AGE:
                    os.remove(ruta)
        except Exception as e:
            print(f"Error eliminando {ruta}: {e}")

def lanzar_limpieza():
    hilo = threading.Thread(target=limpiar_audios, daemon=True)
    hilo.start()

@app.post("/tts")
async def generar_tts(request: Request):
    # 🔐 Seguridad por API Key desde .env
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="No autorizado")

    body = await request.json()
    texto = body.get("text")

    if not texto:
        raise HTTPException(status_code=400, detail="Falta el campo 'text'")

    if len(texto) > 1000:  # 🔒 protección básica
        raise HTTPException(status_code=413, detail="Texto demasiado largo")

    try:
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        tts = gTTS(text=texto, lang='es')
        tts.save(filepath)

        lanzar_limpieza()

        return FileResponse(
            path=filepath,
            media_type="audio/mpeg",
            filename="audio.mp3"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
