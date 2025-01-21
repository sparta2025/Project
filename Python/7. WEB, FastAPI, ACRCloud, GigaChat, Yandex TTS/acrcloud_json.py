from fastapi import FastAPI
import json

app = FastAPI()  # Определяем приложение для FastAPI в модуле


@app.post("/extract_music_info_text/")
async def extract_music_info_text(response_json):
    """
    Извлекает ключевую информацию о песне из JSON-ответа и формирует текст для генерации аудиофайла.

    Parameters:
    - response_json (str): JSON-ответ от ACRCloud API в виде строки.

    Returns:
    - str: Текстовая информация о песне для последующей генерации аудиофайла.
    """
    try:
        # Парсим строку JSON в Python-объект
        data = json.loads(response_json)

        # Проверяем статус ответа
        if data.get("status", {}).get("code") != 0:
            raise ValueError("Ошибка в ответе API: Некорректный статус")

        # Извлекаем данные о музыке
        music_data = data.get("metadata", {}).get("music", [])[0]
        if not music_data:
            raise ValueError("Ошибка в ответе API: Данные о музыке отсутствуют")

        # Формируем текстовую информацию
        text_lines = [
            f"Исполнитель: {music_data.get('artists', [{}])[0].get('name', 'Не указано')}.",
            f"Название песни: {music_data.get('title', 'Не указано')}.",
            f"Альбом: {music_data.get('album', {}).get('name', 'Не указано')}.",
            f"Жанры: {', '.join(genre.get('name', '') for genre in music_data.get('genres', []))}.",
            f"Год выпуска: {music_data.get('release_date', 'Не указано')}.",
            f"Продолжительность: {round(music_data.get('duration_ms', 0) / 1000)} секунд.",
            "Это краткая информация о песне, найденной в базе данных."
        ]

        # Объединяем строки в итоговый текст
        return " ".join(text_lines)

    except json.JSONDecodeError:
        return "Ошибка: Некорректный JSON"
    except KeyError as e:
        return f"Ошибка: Отсутствует ключ {e}"
    except Exception as e:
        return f"Непредвиденная ошибка: {e}"
