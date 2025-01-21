from fastapi import FastAPI
import requests

app = FastAPI()  # Определяем приложение для FastAPI в модуле


@app.post("/get_iam_token/")
async def get_iam_token(oauth_token, end_point_yandex_iam_token):
    """
    Получает IAM-токен с использованием OAuth-токена.

    Parameters:
    - oauth_token (str): OAuth-токен для аутентификации.

    Returns:
    - dict: Ответ API в формате JSON.
    """
    url = end_point_yandex_iam_token
    payload = {"yandexPassportOauthToken": oauth_token}

    # Отправка POST-запроса
    response = requests.post(url, json=payload)

    # Проверка статуса и возврат результата
    if response.status_code == 200:
        # Получение значения ключа
        iam_token = response.json().get('iamToken')
        return iam_token
    else:
        response.raise_for_status()


@app.post("/synthesize_text_to_speech/")
async def synthesize_text_to_speech(iam_token, folder_id, text, output_filename, end_point_yandex_text_to_speech):
    """
    Синтезирует текст в речь с использованием Яндекс.Облако и сохраняет результат в файл.

    Parameters:
    - iam_token (str): IAM токен для аутентификации.
    - folder_id (str): Идентификатор каталога в Яндекс.Облаке.
    - text (str): Текст для синтеза.
    - output_filename (str): Имя выходного файла для сохранения аудиофайла.

    Returns:
    - str: Имя выходного файла с синтезированной речью.

    Raises:
    - Exception: Если запрос к API завершился с ошибкой.
    """
    # URL API для синтеза речи
    url = end_point_yandex_text_to_speech

    # Заголовки запроса с токеном авторизации
    headers = {
        'Authorization': f'Bearer {iam_token}',
    }

    # Параметры запроса для синтеза речи
    data = {
        'text': text,               # Текст для синтеза
        'lang': 'ru-RU',            # Язык синтеза (русский)
        'folderId': folder_id,      # ID каталога Яндекс.Облака
        'format': 'mp3',            # Формат выходного аудио
        'sampleRateHertz': 16000,   # Частота дискретизации аудио
    }

    # Отправка POST-запроса к API
    response = requests.post(url, headers=headers, data=data)

    # Проверка успешности запроса
    if response.status_code != 200:
        raise Exception(f'Ошибка синтеза речи: {response.status_code}, {response.text}')

    # Сохранение синтезированного аудио в файл
    with open(output_filename, 'wb') as file:
        file.write(response.content)

    # Возврат имени выходного файла
    return output_filename
