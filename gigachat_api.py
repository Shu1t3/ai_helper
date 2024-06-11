import json
import uuid

import requests
from requests.auth import HTTPBasicAuth

from constant import CLIENT_ID, SECRET
from utils import get_file_id


def get_access_token() -> str:
    url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
    payload = {
        'scope': 'GIGACHAT_API_PERS'
    }
    headers = {
      'Content-Type': 'application/x-www-form-urlencoded',
      'Accept': 'application/json',
      'RqUID': str(uuid.uuid4())
    }

    result = requests.post(
        url,
        headers=headers,
        auth=HTTPBasicAuth(CLIENT_ID, SECRET),
        data=payload,
        verify='russian_trusted_root_ca.crt'
    )

    return result.json()['access_token']


def get_image(file_id: str, access_token: str):
    url = f"https://gigachat.devices.sberbank.ru/api/v1/files/{file_id}/content"

    payload={}
    headers = {
        'Accept': 'image/jpg',
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(
        url,
        headers=headers,
        data=payload,
        verify='russian_trusted_root_ca.crt'
    )

    return response.content


def send_prompt(msg: str, access_token: str):
    url = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    payload = json.dumps({
      "model": "GigaChat",
      "messages": [
        {
          "role": "user",
          "content": msg
        }
      ],
      "function_call": "auto"
    #   "temperature": 1,
    #   "top_p": 0.1,
    #   "n": 1,
    #   "stream": False,
    #   "max_tokens": 512,
    #   "repetition_penalty": 1
    })

    headers = {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
      'Authorization': f'Bearer {access_token}'
    }

    response = requests.post(
        url,
        headers=headers,
        data=payload,
        verify='russian_trusted_root_ca.crt'
    )

    return response.json()['choices'][0]['message']['content']


def send_prompt_and_get_response(msg: str, access_token: str):
    response = send_prompt(msg, access_token)
    data, is_image = get_file_id(response)

    if is_image:
        data = get_image(data, access_token)

    return data, is_image