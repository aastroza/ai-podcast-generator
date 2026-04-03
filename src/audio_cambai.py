import io
import os
import sys

from pydub import AudioSegment

module_path = os.path.abspath(os.path.join('..'))
if module_path not in sys.path:
    sys.path.append(module_path)

from dotenv import load_dotenv

load_dotenv()

CAMBAI_API_KEY = os.getenv("CAMBAI_API_KEY")
CAMBAI_SPEECH_MODEL = os.getenv("CAMBAI_SPEECH_MODEL", "mars-flash")
CAMBAI_LANGUAGE = os.getenv("CAMBAI_LANGUAGE", "en-us")


def _get_client():
    from camb.client import CambAI
    return CambAI(api_key=CAMBAI_API_KEY)


def convertText2Audio_cambai(text, voice_id):
    """
    Converts text to audio using CAMB AI streaming TTS.

    Args:
        text (str): The text to convert.
        voice_id (int or str): The CAMB AI voice ID.

    Returns:
        bytes: The audio content as MP3 bytes.
    """
    from camb.types import StreamTtsOutputConfiguration

    client = _get_client()
    stream = client.text_to_speech.tts(
        text=text,
        language=CAMBAI_LANGUAGE,
        voice_id=int(voice_id),
        speech_model=CAMBAI_SPEECH_MODEL,
        output_configuration=StreamTtsOutputConfiguration(format="mp3"),
    )
    return b"".join(stream)


def merge_audio_segments(segments, output_file):
    """
    Merges multiple audio byte segments into a single MP3 file.

    Args:
        segments (list[bytes]): A list of audio byte segments.
        output_file (str): The path to save the merged audio file.
    """
    merged_audio = AudioSegment.empty()

    for audio_data in segments:
        if audio_data is not None:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
            merged_audio += audio

    merged_audio.export(output_file, format="mp3", bitrate="48k")
    print(f"Merged audio saved to {output_file}")
