from fastapi import FastAPI, UploadFile, Form, File, Request, HTTPException
from fastapi import WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import os
import shutil
import uuid

from acrcloud_com import app as acrcloud_com_app, identify_audio
from acrcloud_json import app as acrcloud_json_app, extract_music_info_text
from gigachat_history import app as gigachat_history_app, get_token, get_answer
from yandex_text_to_speech import app as yandex_app, synthesize_text_to_speech, get_iam_token

app = FastAPI()

# Подключение маршрутов из других модулей
app.mount("/acrcloud", acrcloud_com_app)
app.mount("/acrcloud_json", acrcloud_json_app)
app.mount("/gigachat", gigachat_history_app)
app.mount("/yandex", yandex_app)

# Подготовка директорий
UPLOAD_DIR = "uploads"
OUTPUT_DIR = "output"
ARCHIVED_DIR = "archived_uploads"  # Новая директория для архивирования
os.makedirs(UPLOAD_DIR, exist_ok=True)
os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(ARCHIVED_DIR, exist_ok=True)

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

# Прогресс бар - отображение прогресса
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_message(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)


manager = ConnectionManager()

@app.websocket("/ws/progress")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            await websocket.receive_text()  # Ожидание данных от клиента
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/", response_class=HTMLResponse)
def index(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/")
async def upload_audio(file: UploadFile = File(...)):
    """Эндпоинт для загрузки файла."""
    original_file_path = os.path.join(UPLOAD_DIR, file.filename)
    archived_file_path = os.path.join(ARCHIVED_DIR, file.filename)

    # Сохранение файла в UPLOAD_DIR
    with open(original_file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Копирование файла в ARCHIVED_DIR для архивирования
    shutil.copyfile(original_file_path, archived_file_path)

    return {
        "message": "Файл загружен",
        "file_path": archived_file_path,
        "play_url": f"/play_archived/{file.filename}",
    }


@app.get("/play_archived/{filename}")
async def play_archived_audio(filename: str):
    """Эндпоинт для проигрывания архивированного файла."""
    file_path = os.path.join(ARCHIVED_DIR, filename)

    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename,
    )


@app.post("/process_audio/")
async def process_audio(
    file: UploadFile = File(...),
    acr_access_key: str = Form("Token access ACRCloud"),
    acr_access_secret: str = Form("Token secret ACRCloud"),
    end_point_acrcloud: str = Form("https://identify-eu-west-1.acrcloud.com/v1/identify"),
    oauth_token: str = Form("Token Yandex Cloud"),
    folder_id: str = Form("Yandex folder ID"),
    end_point_yandex_iam_token: str = Form("https://iam.api.cloud.yandex.net/iam/v1/tokens"),
    end_point_yandex_text_to_speech: str = Form("https://tts.api.cloud.yandex.net/speech/v1/tts:synthesize"),
    auth_token: str = Form("Token access GigaChat"),
    end_point_gigachat_token: str = Form("https://ngw.devices.sberbank.ru:9443/api/v2/oauth"),
):
    """Эндпоинт для обработки аудио."""
    file_path = f"temp_{file.filename}"
    temp_file_path = os.path.join(UPLOAD_DIR, f"temp_{file.filename}")
    output_filename = f"outfile_{uuid.uuid4().hex}.wav"
    result_file_path = os.path.join(OUTPUT_DIR, output_filename)

    try:
        # Сохранение временного файла
        with open(temp_file_path, "wb") as buffer:
            buffer.write(await file.read())

        if not os.path.exists(temp_file_path):
            raise HTTPException(status_code=400, detail="Ошибка загрузки файла.")

        # Анализ аудио
        await manager.send_message("Анализ аудио...")
        text = await identify_audio(temp_file_path, acr_access_key, acr_access_secret, end_point_acrcloud)
        
        await manager.send_message("Обработка текста...")
        text_result = await extract_music_info_text(text)

        # Получение токена и истории
        await manager.send_message("Получение токена...")
        access_token = await get_token(auth_token, end_point_gigachat_token)
        
        await manager.send_message("Получение истории...")
        request_text = f"Можешь написать историю создания песни, основываясь на следующих данных: {text_result}."       
        short_history = await get_answer(request_text, access_token)

        # Формирование текста для озвучивания
        full_text = f"{text_result}\n{short_history}"

        # IAM токен
        await manager.send_message("Получение IAM токена...")
        iam_token = await get_iam_token(oauth_token, end_point_yandex_iam_token)

        # Синтез текста в речь
        await manager.send_message("Синтез речи...")
        await synthesize_text_to_speech(
            iam_token, folder_id, full_text, result_file_path, end_point_yandex_text_to_speech
        )

        await manager.send_message("Завершено.")
        return {
            "message": "Аудио успешно обработано.",
            "full_text": full_text,
            "output_file": output_filename,
        }

    except Exception as e:
        await manager.send_message(f"Ошибка: {str(e)}")
        raise HTTPException(status_code=500, detail="Произошла ошибка.")
        
    finally:
        # Удаление временного файла
        if os.path.exists(file_path):
            os.remove(file_path)

        # Удаление файла из /uploads
        original_path = os.path.join(UPLOAD_DIR, file.filename)
        if os.path.exists(original_path):
            os.remove(original_path)
            
        # Удаление файла из /uploads
        if os.path.exists(file.filename):
            os.remove(file.filename)


@app.get("/play_output/{filename}")
async def play_output_audio(filename: str):
    """Эндпоинт для проигрывания итогового файла."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")
    return FileResponse(
        file_path,
        media_type="audio/mpeg",
        filename=filename,
    )


@app.get("/download/", response_class=FileResponse)
async def download_file(file_path: str):
    """Эндпоинт для скачивания файла."""
    if file_path.startswith(ARCHIVED_DIR):
        full_file_path = os.path.join(ARCHIVED_DIR, os.path.basename(file_path))
    elif file_path.startswith(OUTPUT_DIR):
        full_file_path = os.path.join(OUTPUT_DIR, os.path.basename(file_path))
    else:
        raise HTTPException(status_code=400, detail="Некорректный путь к файлу.")

    if not os.path.exists(full_file_path):
        raise HTTPException(status_code=404, detail="Файл не найден")

    return FileResponse(
        full_file_path,
        media_type="application/octet-stream",
        filename=os.path.basename(full_file_path),
    )
