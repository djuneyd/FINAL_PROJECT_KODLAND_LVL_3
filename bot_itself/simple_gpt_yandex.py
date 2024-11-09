import requests
from config import *

# yandex gpt bot
# documentation is accessible
# --> https://yandex.cloud/en/docs/foundation-models/concepts/yandexgpt/?utm_referrer=https%3A%2F%2Fwww.google.com%2F

def random_vacancy(text):
    prompt = {
        # settings of gpt
        # very useful for developer as possible to adjust gpt
        "modelUri": f"gpt://{server}/yandexgpt", # connecting to yandex gpt with id
        "completionOptions": {
            "stream": False,
            "temperature": 1, # accuracy of answer
            "maxTokens": "2000" # length of response
        },
        "messages": [
            {
                "role": "system", # system is better to use
                "text": 'You propose different vacancies providing all information about it. Provide the international salary. ONLY IN ENGLISH' # here we set the mindset of our gpt
                # for instance, we can even make him a translator so we dont have to create new projects
            },
            {
                "role": "user",
                "text": text
            }
        ]
    }
    
    
    url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion" # api link
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Api-Key {api_key}" # connecting to yandex gpt with key
    }
    
    response = requests.post(url, headers=headers, json=prompt) # getting response
    result = response.json().get('result')
    result['alternatives'][0]['message']['text'] = result['alternatives'][0]['message']['text'].replace('*', '')
    result['alternatives'][0]['message']['text'] = result['alternatives'][0]['message']['text'].replace('#', '')
    return result['alternatives'][0]['message']['text']