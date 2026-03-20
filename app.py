import os
import uuid
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from fastapi.responses import FileResponse
from gtts import gTTS
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("API_KEY")
AUDIO_DIR = "audios"

os.makedirs(AUDIO_DIR, exist_ok=True)

app = FastAPI()

def eliminar_archivo(path: str):
    """Elimina un archivo después de enviarlo"""
    try:
        if os.path.exists(path):
            os.remove(path)
            print(f"Archivo eliminado: {path}")
    except Exception as e:
        print(f"Error eliminando {path}: {e}")

@app.post("/tts")
async def generar_tts(request: Request, background_tasks: BackgroundTasks):
    api_key = request.headers.get("x-api-key")
    if api_key != API_KEY:
        raise HTTPException(status_code=401, detail="No autorizado")

    body = await request.json()
    texto = body.get("text")

    if not texto:
        raise HTTPException(status_code=400, detail="Falta el campo 'text'")

    try:
        filename = f"{uuid.uuid4()}.mp3"
        filepath = os.path.join(AUDIO_DIR, filename)

        tts = gTTS(text=texto, lang='es')
        tts.save(filepath)

        # 🔥 Programar eliminación después de responder
        background_tasks.add_task(eliminar_archivo, filepath)

        return FileResponse(
            path=filepath,
            media_type="audio/mpeg",
            filename="audio.mp3"
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
