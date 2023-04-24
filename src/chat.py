from marvin import Bot
import requests
import json
import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from dotenv import load_dotenv

load_dotenv()

PLAYHT_SECRET = os.getenv("PLAYHT_SECRET")
PLAYHT_USER_ID = os.getenv("PLAYHT_USER_ID")

def convertText2Audio(text, voice):
    url = "https://play.ht/api/v1/convert"

    payload = {
        "content": [text],
        "voice": voice
    }
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "AUTHORIZATION": PLAYHT_SECRET,
        "X-USER-ID": PLAYHT_USER_ID
    }

    response = requests.post(url, json=payload, headers=headers)
    convert_data = json.loads(response.text)

    return convert_data['transcriptionId']

def getAudio(transciption_id):

    url = f"https://play.ht/api/v1/articleStatus?transcriptionId={transciption_id}"

    headers = {
        "accept": "application/json",
        "AUTHORIZATION": PLAYHT_SECRET,
        "X-USER-ID": PLAYHT_USER_ID
    }

    response = requests.get(url, headers=headers)
    audio_data = json.loads(response.text)

    while True:
        if audio_data['converted'] == True:
            return audio_data['audioUrl']

        else:
            print(f'Is audio ready? {audio_data["converted"]}')  
            response = requests.get(url, headers=headers)
            audio_data = json.loads(response.text)

class ChatBot:
    def __init__(self, voice=None, image=None, name=None, personality=None, instructions=None):
        self.bot = Bot(name = name, personality = personality, instructions = instructions)
        self.voice = voice
        self.image = image

    def chat(self, text):
        response = self.bot.say_sync(text).content
        return response

    def change_voice(self, new_voice):
        self.voice = new_voice

    def change_image(self, new_image):
        self.image = new_image

    def get_voice(self):
        return self.voice

    def get_image(self):
        return self.image

    def speak(self, text):
        transcription_id = convertText2Audio(text, self.voice)
        return transcription_id