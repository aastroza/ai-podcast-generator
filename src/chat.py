from marvin import Bot
from audio import convertText2Audio
import os
import sys
module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from dotenv import load_dotenv

load_dotenv()

class ChatBot:
    """
    A ChatBot class that allows for text-based chatting and conversion of text responses to audio.

    The ChatBot uses the Marvin chatbot library for generating text responses and the Play.ht API for converting text to audio.
    """
    
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