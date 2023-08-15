import json

import requests


class APIVoice:
    def __init__(self, token):
        self.token = token

    def get_list_voices(self):
        url = 'https://apihost.ru/api/v1/speaker'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json',
        }
        data = {
            'server': 3
        }

        response = requests.post(url, json=data, headers=headers)

        if response.status_code == 200:
            print(response.json())
        else:
            print(f"Error {response.status_code}: {response.text}")

    def send_text(self, text):
        data = {
            'data': [
                {
                    'lang': 'ru-RU',        # Язык голоса
                    'speaker': '34',        # Уникальный идентификатор
                    'emotion': 'neutral',   # Эмоции голоса
                    'text': str(text),      # Текст
                    'rate': '1.0',          # Скорость
                    'pitch': '1.0',         # Тон голоса
                    'type': 'mp3',          # Формат файла на выходе
                    'pause': '0'            # Длина паузы
                }
            ]
        }

        json_data = json.dumps(data)

        url = 'https://apihost.ru/api/v1/synthesize'
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        response = requests.post(url, data=json_data, headers=headers)
        response_data = response.json()

        return(response_data)

    def get_link_download(self, process):
        url = 'https://apihost.ru/api/v1/process'
        data = {
            'process': str(process)
        }
        headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

        json_data = json.dumps(data)

        response = requests.post(url, data=json_data, headers=headers)
        response_data = response.json()

        return response_data

    def download_file(self, url, save_path):
        response = requests.get(url)
        if response.status_code == 200:
            with open(save_path, 'wb') as f:
                f.write(response.content)
        return response.status_code
