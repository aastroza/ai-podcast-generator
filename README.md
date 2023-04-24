# Podcast Automation

Podcast Automation is a AI powered software that automatically generates podcast scripts and audio from text files. This tool leverages [Marvin](https://github.com/PrefectHQ/marvin) for text generation and [Play.ht API](https://docs.play.ht/reference/api-getting-started) for text-to-speech conversion. The generated audio clips are then merged using pydub to create the final podcast output.

## Features

- Generate podcast scripts and audio automatically.
- Customize podcast details, host, guest, topics, and output settings.
- Supports multiple voices from Play.ht API.
- Requires minimal setup and configuration.

## Installation

1. Clone this repository:

```
git clone https://github.com/aastroza/podcast-automation.git
```

2. Navigate to the project directory:

```
cd podcast-automation
```

3. Create a Python virtual environment:

```
python3 -m venv venv
```

4. Activate the virtual environment:

- For Linux/MacOS:

```
source venv/bin/activate
```

- For Windows:

```
venv\Scripts\activate.bat
```

5. Install the required packages:

```
pip install -r requirements.txt
```

## Usage

1. Create a YAML configuration file for your podcast (e.g., `podcast.YAML`).
2. Set up the environment variables by creating a `.env` file and adding the required API keys.
3. Run the script to generate the podcast:

```
python podcast.py --input examples/ai/podcast.YAML
```

The script will generate the podcast audio and save it in output folder specified in the YAML file.

## Configuration

The YAML configuration file contains information about the podcast, host, guest, topics, and output settings. Here's an example:

```yaml
# Podcast Interview Configuration
podcast:
  info:
    title: Artificial Intelligence for Natural Brains
    description: A podcast where we talk about the future of AI and how it will affect our lives
  host:
    name: Brandon Bert
    voice: en-US-BrandonNeural #A value from data/voices.json
  guest:
    name: Monica Gradient
    voice: en-US-MonicaNeural #A value from data/voices.json
  topics:
    main: Artificial Intelligence
    sub:
      - ChatGPT
      - Generative AI
      - AGI
      - AI Ethics
  output:
    duration: 5 #Episode length in minutes
    language: english
    audio: True #Set to False if you want to generate only the text script
    folder: examples/ai/
```

## Getting an API key
To obtain an **OpenAI API key**, follow these steps:

- Log in to your an [OpenAI account](https://platform.openai.com/) (sign up if you don't have one)
- Go to the "API Keys" page under your account settings.
- Click "Create new secret key." A new API key will be generated. Make sure to copy the key to your clipboard, as you will not be able to see it again.

To obtain a **Play.HT API access**, follow [these instructions](https://docs.play.ht/reference/api-authentication).

## Environment Variables

1. Rename `.env.example` fileto `.env` in the project directory:
2. Open the `.env` file and replace the placeholder values with your actual API keys:

```
OPENAI_API_KEY='your_openai_api_key'
PLAYHT_SECRET='your_playht_secret_key'
PLAYHT_USER_ID='your_playht_user_id'
```

Make sure to save the changes to the `.env` file.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for more information.