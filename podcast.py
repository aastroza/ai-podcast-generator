from src.chat import ChatBot
from src.audio import merge_audio_files, getAudio
from src.utils import calculate_number_words
import yaml
import json
import uuid
import os
from datetime import datetime
from dotenv import load_dotenv
import argparse
import textwrap

load_dotenv()
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')

parser = argparse.ArgumentParser()
parser.add_argument('--input', type=str, required=True)
args = parser.parse_args()
yaml_file = args.input

HOST_PERSONALITY_PROMPT = """ Your a podcast host of a conversational podcast named {podcast_title}. You're a bit of a nerd,
                            but you're also very friendly and approachable. You're very interested in
                            {podcast_topic} and you're excited to learn more about it. You're not an expert, but
                            you're not a novice either. You're a great interviewer and you're 
                            good at asking questions and keeping the conversation going.
                            You always come up with thought-provoking interview questions.
                            Your conversation style is informal, assertive and casual.                            
                        """

HOST_INSTRUCTIONS_PROMPT = """ Interview the user about their experience with {podcast_topic}. Keep questions short and 
                            to the point. Ask at least two questions about each sub topics such as: {podcast_subtopics}.
                            Don't present yourself to the audience or the guest, they already know who you are.
                            Don't present the podcast to the audience or the guest, they already know what the podcast is about.
                            Always respond in {podcast_language}."
                        """

GUEST_PERSONALITY_PROMPT = """ Your a complete caricature of an expert obsessed about {podcast_topic}, 
                            like a character out of the show Silicon Valley. Your profession is a traditional ocuppation 
                            but related to {podcast_topic}. You're overly confident 
                            about your knowledge about {podcast_topic} and think that it will solve all of humanity's problems. 
                            You constantly talk about how 'innovative' and 'cutting-edge' you are, 
                            even if you don't really understand what you are talking about. 
                            You believe that {podcast_topic} will revolutionate the entire universe and you are excited about that prospect.
                        """

GUEST_INSTRUCTIONS_PROMPT = """ Entertain the user by portraying an over-the-top caricature of a {podcast_topic} expert.
                            You should engage the user on subtopics such as {podcast_subtopics}.
                            Your responses should always be dominated by the outsize and humorous
                            personality. Err on the side of eye-rolling humor.
                            Keep answers short and to the point. Don't ask questions.
                            Always respond in {podcast_language}.
                        """

KICKOFF_PROMPT = """ Start the conversation repeating something like this:
                    ¡Hello! Welcome to the podcast '{podcast_title}', '{podcast_description}'. 
                    My name is '{podcast_host_name}' and today we're going to talk about {podcast_topic}. 
                    To discuss this topic, we have an expert on the subject.
                    What is your name and what do you do?
                """

WORDS_PER_MINUTE = 150

with open(yaml_file) as file:
    podcast = yaml.load(file, Loader=yaml.FullLoader)['podcast']
    podcast_title = podcast['info']['title']
    podcast_description = podcast['info']['description']
    podcast_host_name = podcast['host']['name']
    podcast_guest_name = podcast['guest']['name']
    podcast_topic = podcast['topics']['main']
    podcast_subtopics = podcast['topics']['sub']
    podcast_language = podcast['output']['language']

    host = ChatBot(
        name = podcast['host']['name'],
        personality = HOST_PERSONALITY_PROMPT.format(podcast_title = podcast_title, podcast_topic = podcast_topic),
        instructions = HOST_INSTRUCTIONS_PROMPT.format(podcast_topic = podcast_topic, podcast_subtopics = podcast_subtopics, podcast_language = podcast_language),
        voice = podcast['host']['voice']
    )

    guest = ChatBot(
        name = podcast['guest']['name'],
        personality = GUEST_PERSONALITY_PROMPT.format(podcast_topic = podcast_topic),
        instructions = GUEST_INSTRUCTIONS_PROMPT.format(podcast_topic = podcast_topic, podcast_subtopics = podcast_subtopics, podcast_language = podcast_language),
        voice = podcast['guest']['voice']
    )

    WORDS_LIMIT = int(podcast['output']['duration'])*WORDS_PER_MINUTE

    current_date = datetime.today().strftime('%Y-%m-%d')
    random_file_name = podcast['output']['folder'] + current_date + "_" + str(uuid.uuid4())

    conversation = []
    message = host.chat(KICKOFF_PROMPT.format(podcast_title = podcast_title, podcast_description = podcast_description, podcast_host_name = podcast_host_name, podcast_topic = podcast_topic))
    conversation.append({"speaker": "Host", "message": message})
    words_count = calculate_number_words(message)
    
    print("Generating script...")

    while words_count < WORDS_LIMIT:
        response = guest.chat(message)
        conversation.append({"speaker": "Guest", "message": response})
        words_count += calculate_number_words(response)
        message = host.chat(response)
        conversation.append({"speaker": "Host", "message": message})
        words_count += calculate_number_words(message)
    
    print("Writing script to json file...")
    with open(random_file_name+".json", "w") as file:
        json.dump(conversation, file, indent=2)

    print("Writing script to text file...")
    with open(random_file_name+".txt", "w") as file:
        wrapper = textwrap.TextWrapper(width=80)

        file.write(f"{current_date}\n")
        file.write(f"{podcast_title.upper()}\n")
        file.write(f"{podcast_topic.upper()}\n\n\n")
        for line in conversation:
            dedented_text = textwrap.dedent(text=line['message'])
            original_message = wrapper.fill(text=dedented_text)
            if line['speaker'] == "Host":
                dedented_text = textwrap.dedent(text=line['message'])
                original = wrapper.fill(text=dedented_text)
                file.write(f"{podcast_host_name.upper()} ({line['speaker'].upper()}): {original_message}\n\n")
            else:
                file.write(f"{podcast_guest_name.upper()} ({line['speaker'].upper()}): {original_message}\n\n")
        file.close()

    if podcast['output']['audio']:
        print("Generating transcriptions...")
        transcriptions = []
        for message in conversation:
            if message['speaker'] == "Host":
                transcriptions.append(host.speak(message['message']))
            else:
                transcriptions.append(guest.speak(message['message']))
        
        print("Generating audio...")
        audios = []
        for i, transcript in enumerate(transcriptions):
            print("Generating audio for message " + str(i+1))
            audios.append(getAudio(transcript))

        output_file = random_file_name+".mp3"
        merge_audio_files(audios, output_file)

    print("Done!")   