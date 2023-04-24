from pydub import AudioSegment
import io
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
    """
    Converts a given text to audio using the specified voice through the Play.ht API.

    Args:
        text (str): The text to be converted to audio.
        voice (str): The voice identifier to be used for the audio conversion.

    Returns:
        str: The transcription ID of the converted audio.

    Raises:
        Exception: If the API request fails or an error occurs during the conversion process.

    Usage:
        text = "Hello, this is a sample text."
        voice = "en-US-JennyNeural"
        transcription_id = convertText2Audio(text, voice)
    """

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
    """
    Retrieves the audio URL for a given transcription ID from the Play.ht API.

    Args:
        transcription_id (str): The transcription ID for the desired audio file.

    Returns:
        str: The URL of the converted audio file.

    Raises:
        Exception: If the API request fails or an error occurs during the retrieval process.

    Notes:
        This function will continuously poll the API until the audio file is marked as converted.
        Please ensure that appropriate rate limiting measures are taken to avoid excessive requests.
    """

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

def download_audio(url):
    """
    Downloads an audio file from the given URL using an HTTP GET request.

    Args:
        url (str): The URL of the audio file to be downloaded.

    Returns:
        bytes: The binary content of the audio file if the download is successful, otherwise None.

    Raises:
        Exception: If an error occurs during the download process.

    Usage:
        audio_url = "https://example.com/sample_audio.mp3"
        audio_content = download_audio(audio_url)

    Notes:
        If the download fails, the function will print an error message and return None.
    """
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        print(f"Failed to download {url}")
        return None

def merge_audio_files(urls, output_file):
    """
    Merges multiple audio files from a list of URLs and saves the merged file to the specified output file.

    Args:
        urls (List[str]): A list of URLs of the audio files to be merged.
        output_file (str): The path to save the merged audio file.

    Raises:
        Exception: If an error occurs during the merging or exporting process.

    Usage:
        audio_urls = ["https://example.com/audio1.mp3", "https://example.com/audio2.mp3"]
        output_file = "merged_audio.mp3"
        merge_audio_files(audio_urls, output_file)

    Notes:
        This function uses the pydub library to merge the audio files.
        If an audio file cannot be downloaded, the function will print an error message and skip the file.
        The merged audio file will be saved in the MP3 format with a bitrate of 48k.
    """
    merged_audio = AudioSegment.empty()
    
    for url in urls:
        audio_data = download_audio(url)
        if audio_data is not None:
            audio = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
            merged_audio += audio
        else:
            print(f"Skipping {url}")
    
    merged_audio.export(output_file, format="mp3", bitrate="48k")
    print(f"Merged audio saved to {output_file}")