from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the .env file
dotenv_path = '/home/eaglesvn/Documents/dockerz/vuepy03/ttsstt/.env'
load_dotenv(dotenv_path)

# Initialize Flask application
app1_mod_ttsstt = Flask(__name__)
app1_mod_ttsstt.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize OpenAI client using environment variable for API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

# Directory to save audio files
AUDIO_DIR = Path('/home/eaglesvn/Documents/dockerz/vuepy03/ttsstt/src/audio')
AUDIO_DIR.mkdir(parents=True, exist_ok=True)  # Ensure the directory exists

def get_new_audio_filename():
    existing_files = list(AUDIO_DIR.glob('response_*.mp3'))
    if not existing_files:
        return AUDIO_DIR / 'response_001.mp3'
    else:
        existing_numbers = [int(f.stem.split('_')[1]) for f in existing_files]
        new_number = max(existing_numbers) + 1
        return AUDIO_DIR / f'response_{new_number:03}.mp3'

def extract_and_convert_to_tts(text):
    try:
        print(f'Extracted text for TTS: {text}')
        
        audio_path = get_new_audio_filename()
        print(f'Generated audio file path: {audio_path}')

        response = client.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )

        response.stream_to_file(audio_path)
        print(f'Streamed audio to file: {audio_path}')

        if audio_path.exists():
            print(f'MP3 successfully saved to {audio_path}')
            return audio_path
        else:
            print(f'Failed to save MP3 to {audio_path}')
            return None
        
    except Exception as e:
        print(f"An error occurred during TTS conversion: {e}")
        return None

@app1_mod_ttsstt.route('/app1/api/app1_endpoint_ttsstt', methods=['POST'])
def post_stt_data():
    try:
        # Receive formatted message as JSON from the client
        stt_data = request.json
        print(f'Received formatted JSON data via HTTP POST: {stt_data}')

        # Forward formatted message to OpenAI API to generate a completion
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=stt_data['messages']
        )

        # Extract the text response from OpenAI
        response_text = completion.choices[0].message.content 
        print(f'Response from OpenAI: {response_text}')

        # Convert the response text to speech and save it as an MP3 file
        if not response_text.strip():
            return jsonify({"error": "Received empty response from OpenAI API"}), 500

        audio_path = extract_and_convert_to_tts(response_text)
        
        if audio_path:
            return jsonify({"message": "success", "audio_path": str(audio_path)}), 200
        else:
            return jsonify({"error": "Failed to convert text to speech"}), 500

    except Exception as e:
        # Return error message if any exception occurs
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app1_mod_ttsstt.route('/test', methods=['GET'])
def test_route():
    return "Test route working", 200

if __name__ == '__main__':
    app1_mod_ttsstt.run(debug=os.getenv('FLASK_DEBUG') == '1', host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'), port=6961)
