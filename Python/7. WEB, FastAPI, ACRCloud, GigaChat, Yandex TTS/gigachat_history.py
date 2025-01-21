from fastapi import FastAPI
import requests
import uuid
import json

app = FastAPI()  # Определяем приложение для FastAPI в модуле


@app.post("/get_token/")
async def get_token(giga_chat_key, end_point_gigachat_token):
    """
    Получение токена с сервера по API с использованием UUID и базовой авторизации.

    Returns:
    - dict: JSON-ответ от сервера, содержащий токен или сообщение об ошибке.
    """
    # URL конечной точки API
    url = end_point_gigachat_token

    # Генерация UUID версии 4 (используется для уникального идентификатора запроса)
    generated_uuid = str(uuid.uuid4())  # Преобразуем UUID в строку для использования в заголовке

    # Данные запроса (форма URL-кодирования)
    payload = 'scope=GIGACHAT_API_PERS'  # Указываем область действия токена

    # Заголовки запроса
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded',  # Указываем тип данных для тела запроса
        'Accept': 'application/json',  # Ожидаем JSON-ответ
        'RqUID': generated_uuid,  # Уникальный идентификатор запроса
        'Authorization': f'Basic {giga_chat_key}'  # Базовая авторизация (логин:пароль закодированы в Base64)
    }

    try:
        # Отправка POST-запроса
        response = requests.request("POST", url, headers=headers, data=payload, verify='chain.pem')

        # Проверка статуса ответа
        response.raise_for_status()  # Генерирует исключение для кода ответа >= 400

        # Возвращаем JSON-ответ сервера
        # Извлечение значения access_token
        access_token = response.json().get('access_token')
        return access_token

    except requests.exceptions.RequestException as e:
        # Обработка ошибок HTTP
        return {"error": str(e)}


@app.post("/get_answer/")
async def get_answer(text, access_token):
    # URL конечной точки API GigaChat
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    # Формируем тело запроса
    payload = json.dumps({
        "model": "GigaChat",  # Указываем модель GigaChat (альтернативы: GigaChat-Pro и GigaChat-Plus)
        "messages": [
            {
                "role": "system",
                "content": "Ты знаток музыкальной истории и музыкальный критик."
            },
            {
                "role": "user",  # Роль сообщения (запрос от пользователя)
                "content": text  # Содержимое запроса (передаваемый текст)
            }
        ],
        "temperature": 1,  # Температура — уровень случайности ответов (1 = больше креативности)
        "top_p": 0.1,  # Топ-p — ограничение вероятности выбора слов (0.1 = больше предсказуемости)
        "n": 1,  # Количество генерируемых ответов
        "stream": False,  # Определяет, будет ли ответ возвращаться потоково
        "max_tokens": 512,  # Максимальное количество токенов в ответе
        "repetition_penalty": 1  # Наказание за повторения (1 = нет наказания)
    })

    # Формируем заголовки запроса
    headers = {
        'Content-Type': 'application/json',  # Формат данных в теле запроса
        'Accept': 'application/json',  # Формат ожидаемого ответа
        'Authorization': f'Bearer {access_token}'  # Токен доступа для авторизации
    }

    # Отправляем POST-запрос к API
    response = requests.request("POST", url, headers=headers, data=payload, verify='chain.pem')

    # Возвращаем ответ API в формате JSON
    # Извлечение содержимого ключа content
    content = response.json()['choices'][0]['message']['content']

    return content
