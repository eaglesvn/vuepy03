from gevent import monkey  # type: ignore
monkey.patch_all()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import openai
import os
from dotenv import load_dotenv
from pathlib import Path

dotenv_path = '/home/eaglesvn/Documents/dockerz/vuepy03/ttsstt/.env'
load_dotenv(dotenv_path)

app1_mod_ttsstt = Flask(__name__)
app1_mod_ttsstt.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app1_mod_ttsstt, async_mode='gevent')

openai.api_key = os.getenv('OPENAI_API_KEY')

AUDIO_DIR = Path('/home/eaglesvn/Documents/dockerz/vuepy03/ttsstt/src/audio')

def get_new_audio_filename():
    existing_files = list(AUDIO_DIR.glob('response_*.mp3'))
    if not existing_files:
        return AUDIO_DIR / 'response_001.mp3'
    else:
        existing_numbers = [int(f.stem.split('_')[1]) for f in existing_files]
        new_number = max(existing_numbers) + 1
        return AUDIO_DIR / f'response_{new_number:03}.mp3'

@app1_mod_ttsstt.route('/app1/api/app1_endpoint_ttsstt', methods=['POST'])
def post_stt_data():
    try:
        stt_data = request.json
        print(f'Received JSON data via HTTP POST: {stt_data}')

        client = openai.OpenAI()
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=stt_data['messages'],
            stream=True,
        )

        response_text = ""
        for chunk in stream:
            print(f"Received chunk: {chunk}")
            if 'choices' in chunk:
                delta = chunk['choices'][0].get('delta', {})
                print(f"Delta: {delta}")
                if 'content' in delta and delta['content']:
                    response_text += delta['content']
                    print(f"Accumulated content: {response_text}")

        print(f"Formatted response: {response_text}")

        if not response_text.strip():
            return jsonify({"error": "Received empty response from OpenAI API"}), 500

        audio_path = extract_and_convert_to_tts(response_text)
        
        if audio_path:
            return jsonify({"message": "success", "audio_path": str(audio_path)}), 200
        else:
            return jsonify({"error": "Failed to convert text to speech"}), 500

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

def extract_and_convert_to_tts(text):
    try:
        print(f'Extracted text for TTS: {text}')
        
        audio_path = get_new_audio_filename()

        response = openai.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )

        with open(audio_path, 'wb') as file:
            for chunk in response.with_streaming_response():
                file.write(chunk)

        print(f'MP3 saved to {audio_path}')
        return audio_path
        
    except Exception as e:
        print(f"An error occurred during TTS conversion: {e}")
        return None

@app1_mod_ttsstt.route('/test', methods=['GET'])
def test_route():
    return "Test route working", 200

@app1_mod_ttsstt.route('/routes', methods=['GET'])
def list_routes():
    import urllib
    output = []
    for rule in app1_mod_ttsstt.url_map.iter_rules():
        methods = ','.join(rule.methods)
        line = urllib.parse.unquote(f"{rule.endpoint}: {methods} {rule}")
        output.append(line)
    return jsonify(routes=output)

if __name__ == '__main__':
    socketio.run(app1_mod_ttsstt, debug=os.getenv('FLASK_DEBUG') == '1', host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'), port=5001)
