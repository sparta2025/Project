# Необходимо инсталлировать фреймворк pip install pydub

from fastapi import FastAPI
from pydub import AudioSegment
import tempfile
import base64
import hashlib
import hmac
import os
import time
import requests

app = FastAPI()  # Определяем приложение для FastAPI в модуле


def cut_audio(file_path, duration_ms=20000):
    """
    Обрезает аудиофайл до указанной длительности (по умолчанию 20 секунд).

    Parameters:
    - file_path (str): Путь к исходному аудиофайлу.
    - duration_ms (int): Длительность в миллисекундах (по умолчанию 20 секунд).

    Returns:
    - str: Путь к временному файлу с обрезанным аудио.
    """
    audio = AudioSegment.from_file(file_path)
    trimmed_audio = audio[:duration_ms]

    # Создаем временный файл для обрезанного аудио
    temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
    trimmed_audio.export(temp_file.name, format="mp3")

    return temp_file.name


@app.post("/identify_audio/")
async def identify_audio(file_path, access_key, access_secret, requrl):
    """
    Определяет информацию о песне из аудиофайла с использованием ACRCloud API.
    Обрезает аудио до первых 20 секунд перед отправкой.

    Parameters:
    - file_path (str): Путь к аудиофайлу.
    - access_key (str): Ключ доступа к ACRCloud API.
    - access_secret (str): Секрет доступа к ACRCloud API.
    - requrl (str): URL для отправки запроса к API.

    Returns:
    - str: Результат обработки в формате JSON.
    """
    try:
        # Проверяем существование файла
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Файл {file_path} не найден.")

        # Обрезаем файл до первых 20 секунд
        trimmed_file_path = cut_audio(file_path, duration_ms=20000)

        # Определение необходимых параметров
        http_method = "POST"
        http_uri = "/v1/identify"
        data_type = "audio"  # Тип данных: аудио
        signature_version = "1"
        timestamp = time.time()

        # Формирование строки для подписи
        string_to_sign = (
            f"{http_method}\n{http_uri}\n{access_key}\n{data_type}\n"
            f"{signature_version}\n{int(timestamp)}"
        )

        # Генерация подписи
        sign = base64.b64encode(
            hmac.new(
                access_secret.encode('ascii'),
                string_to_sign.encode('ascii'),
                digestmod=hashlib.sha1
            ).digest()
        ).decode('ascii')

        # Определяем размер файла
        sample_bytes = os.path.getsize(trimmed_file_path)

        data = {
            'access_key': access_key,
            'sample_bytes': sample_bytes,
            'timestamp': str(int(timestamp)),
            'signature': sign,
            'data_type': data_type,
            "signature_version": signature_version
        }

        # Открытие файла в контекстном менеджере для безопасного использования
        with open(trimmed_file_path, 'rb') as file:
            files = [
                ('sample', (os.path.basename(trimmed_file_path), file, 'audio/mpeg'))
            ]
            response = requests.post(requrl, files=files, data=data)
            response.encoding = "utf-8"  # Устанавливаем кодировку ответа

        # Удаляем временный файл
        os.remove(trimmed_file_path)

        # Проверяем успешность запроса
        if response.status_code != 200:
            raise Exception(f"Ошибка запроса: {response.status_code}, {response.text}")

        # Возвращаем текстовый результат
        return response.text

    except FileNotFoundError as e:
        return f"Ошибка: {e}"
    except requests.RequestException as e:
        return f"Ошибка HTTP: {e}"
    except Exception as e:
        return f"Непредвиденная ошибка: {e}"
