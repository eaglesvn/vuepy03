from pathlib import Path
import queue
import threading
from functools import reduce
from typing import Callable, Generator
import os
import openai
from dotenv import load_dotenv
from flask import Flask, request, jsonify

# Load environment variables from .env file
load_dotenv()

# Initialize Flask application
app1_mod_ttsstt = Flask(__name__)
app1_mod_ttsstt.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize OpenAI API client
OPENAI_CLIENT = openai.OpenAI()

# Global stop event
stop_event = threading.Event()

# Constants
DELIMITERS = [f"{d} " for d in (".", "?", "!")]
MINIMUM_PHRASE_LENGTH = 200
TTS_CHUNK_SIZE = 1024
DEFAULT_RESPONSE_MODEL = "gpt-4o-mini"
DEFAULT_TTS_MODEL = "tts-1"
DEFAULT_VOICE = "shimmer"

# Directory to save audio files
AUDIO_DIR = Path('/app1/src/audio')  # Ensure this matches the container path

# Ensure the audio directory exists
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Function to generate a new file name with a sequential suffix
def get_new_audio_filename():
    existing_files = list(AUDIO_DIR.glob('response_*.mp3'))
    if not existing_files:
        return AUDIO_DIR / 'response_001.mp3'
    else:
        existing_numbers = [int(f.stem.split('_')[1]) for f in existing_files]
        new_number = max(existing_numbers) + 1
        return AUDIO_DIR / f'response_{new_number:03}.mp3'

# Function to stream chat completion responses from OpenAI
def stream_delimited_completion(
    messages: list[dict],
    client: openai.OpenAI = OPENAI_CLIENT,
    model: str = DEFAULT_RESPONSE_MODEL,
    content_transformers: list[Callable[[str], str]] = [],
    phrase_transformers: list[Callable[[str], str]] = [],
    delimiters: list[str] = DELIMITERS,
) -> Generator[str, None, None]:
    def apply_transformers(s: str, transformers: list[Callable[[str], str]]) -> str:
        return reduce(lambda c, transformer: transformer(c), transformers, s)

    working_string = ""
    for chunk in client.chat.completions.create(
        messages=messages, model=model, stream=True
    ):
        if stop_event.is_set():
            yield None
            return

        content = chunk.choices[0].delta.content or ""
        if content:
            working_string += apply_transformers(content, content_transformers)
            while len(working_string) >= MINIMUM_PHRASE_LENGTH:
                delimiter_index = -1
                for delimiter in delimiters:
                    index = working_string.find(delimiter, MINIMUM_PHRASE_LENGTH)
                    if index != -1 and (
                        delimiter_index == -1 or index < delimiter_index
                    ):
                        delimiter_index = index

                if delimiter_index == -1:
                    break

                phrase, working_string = (
                    working_string[: delimiter_index + len(delimiter)],
                    working_string[delimiter_index + len(delimiter) :],
                )
                yield apply_transformers(phrase, phrase_transformers)

    if working_string.strip():
        yield working_string.strip()

    yield None

# Thread function to generate phrases and put them in the phrase queue
def phrase_generator(phrase_queue: queue.Queue, prompt: str):
    for phrase in stream_delimited_completion(
        messages=[{"role": "user", "content": prompt}],
        content_transformers=[lambda c: c.replace("\n", " ")],
        phrase_transformers=[lambda p: p.strip()],
    ):
        if phrase is None:
            phrase_queue.put(None)
            return
        phrase_queue.put(phrase)

# Thread function to convert phrases to speech and save them as audio files
def text_to_speech_processor(
    phrase_queue: queue.Queue,
    client: openai.OpenAI = OPENAI_CLIENT,
    model: str = DEFAULT_TTS_MODEL,
    voice: str = DEFAULT_VOICE,
):
    audio_path = get_new_audio_filename()
    try:
        with open(audio_path, 'wb') as audio_file:
            while not stop_event.is_set():
                phrase = phrase_queue.get()
                if phrase is None:
                    return

                try:
                    response = client.audio.speech.create(
                        model=model, voice=voice, input=phrase
                    )

                    # Write the response to a file
                    audio_file.write(response.content)

                    print(f"Streamed audio to file: {audio_path}")

                except Exception as e:
                    print(f"Error in text_to_speech_processor: {e}")
                    return

    except Exception as e:
        print(f"An error occurred during TTS conversion: {e}")

# Route to handle POST request to process STT data and generate response
@app1_mod_ttsstt.route('/app1/api/app1_endpoint_ttsstt', methods=['POST'])
def post_stt_data():
    try:
        # Receive formatted message as JSON from the client
        stt_data = request.json
        print(f'Received formatted JSON data via HTTP POST: {stt_data}')
        prompt = stt_data['messages'][1]['content']

        phrase_queue = queue.Queue()

        # Start threads for phrase generation and TTS processing
        phrase_generation_thread = threading.Thread(target=phrase_generator, args=(phrase_queue, prompt))
        tts_thread = threading.Thread(target=text_to_speech_processor, args=(phrase_queue,))

        phrase_generation_thread.start()
        tts_thread.start()

        phrase_generation_thread.join()
        print("## all phrases enqueued. phrase generation thread terminated.")
        tts_thread.join()
        print("## all tts complete and enqueued. tts thread terminated.")

        return jsonify({"message": "success"}), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

# Route to check if the server is running
@app1_mod_ttsstt.route('/test', methods=['GET'])
def test_route():
    return "Test route working", 200

# Main entry point to run the Flask application
if __name__ == '__main__':
    app1_mod_ttsstt.run(debug=os.getenv('FLASK_DEBUG') == '1', host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'), port=6961)
