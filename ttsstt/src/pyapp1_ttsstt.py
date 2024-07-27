from gevent import monkey  # type: ignore
monkey.patch_all()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from openai import OpenAI
import os
from dotenv import load_dotenv
from pathlib import Path

# Load environment variables from the .env file
dotenv_path = '/home/eaglesvn/Documents/dockerz/vuepy03/ttsstt/.env'
load_dotenv(dotenv_path)

# Initialize Flask application and configure settings
app1_mod_ttsstt = Flask(__name__)
app1_mod_ttsstt.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app1_mod_ttsstt, async_mode='gevent')

# Initialize OpenAI client using environment variable for API key
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url='https://api.openai.com/v1'
)

# Directory to save audio files
AUDIO_DIR = Path('./src/audio')
AUDIO_DIR.mkdir(parents=True, exist_ok=True)

# Subroutine: Extract and Convert Text to Speech
def extract_and_convert_to_tts(completion_response):
    """
    Extract text content from OpenAI completion response,
    convert the text to speech using OpenAI TTS API, and save the MP3 file.
    
    :param completion_response: Response object from OpenAI completion
    :return: Path to the saved MP3 file or None if failed
    """
    try:
        # Extract text from OpenAI completion response
        text = completion_response.choices[0].message.content
        print(f'Extracted text for TTS: {text}')
        
        # Prepare payload for TTS request
        tts_payload = {
            "input": {"text": text},
            "voice": {"language_code": "en-US", "name": "en-US-Wavenet-D"},
            "audio_config": {"audio_encoding": "MP3"}
        }
        
        # Send request to OpenAI TTS endpoint
        tts_response = client.text_to_speech.create(
            voice="en-US-Wavenet-D", 
            text=text,
            encoding="MP3"
        )
        
        if tts_response.status_code == 200:
            # Save the MP3 file
            audio_path = AUDIO_DIR / 'response.mp3'
            with open(audio_path, 'wb') as audio_file:
                audio_file.write(tts_response.content)
            print(f'MP3 saved to {audio_path}')
            return audio_path
        else:
            print(f"Failed to get TTS response: {tts_response.json()}")
            return None
    except Exception as e:
        print(f"An error occurred during TTS conversion: {e}")
        return None

# Route: Handle POST request to process STT data and generate response
@app1_mod_ttsstt.route('/app1/api/app1_endpoint_ttsstt', methods=['POST'])
def post_stt_data():
    """
    Handle POST requests to process STT data using OpenAI API,
    generate a response, and return the response.
    
    :return: JSON response with success message or error message
    """
    try:
        stt_data = request.json
        print(f'Received JSON data via HTTP POST: {stt_data}')

        # Forward the STT data to OpenAI API using the correct method
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=stt_data['messages']
        )

        # Print the response from OpenAI API
        print(response.choices[0].message.content)

        return jsonify(response.model_dump()), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

# Route: Simple test endpoint to check if the server is running
@app1_mod_ttsstt.route('/test', methods=['GET'])
def test_route():
    """
    Test route to confirm the server is running.
    
    :return: Simple text confirmation
    """
    return "Test route working", 200

# Route: List all registered routes in the Flask application
@app1_mod_ttsstt.route('/routes', methods=['GET'])
def list_routes():
    """
    List all routes registered in the Flask application.
    
    :return: JSON response with a list of routes
    """
    import urllib
    output = []
    for rule in app1_mod_ttsstt.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint}: {methods} {rule}")
        output.append(line)
    return jsonify(routes=output)

# Main entry point to run the Flask application
if __name__ == '__main__':
    socketio.run(app1_mod_ttsstt, debug=os.getenv('FLASK_DEBUG') == '1', host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'), port=5001)
