# Import necessary modules and monkey patch for gevent
from gevent import monkey  # type: ignore
monkey.patch_all()

# Import Flask and other necessary libraries
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import openai
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
openai.api_key = os.getenv('OPENAI_API_KEY')

# Directory to save audio files
AUDIO_DIR = Path('/home/eaglesvn/Documents/dockerz/vuepy03/ttsstt/src/audio')

# --- Start of STT Data Handling Subroutine ---
# Route: Handle POST request to process STT data and generate response
@app1_mod_ttsstt.route('/app1/api/app1_endpoint_ttsstt', methods=['POST'])
def post_stt_data():
    """
    Handle POST requests to process STT data using OpenAI API,
    generate a response, convert it to speech, and return the response.
    
    :return: JSON response with success message or error message
    """
    try:
        # Receive STT data as JSON from the client
        stt_data = request.json
        print(f'Received JSON data via HTTP POST: {stt_data}')

        # Forward the STT data to OpenAI API to generate a completion
        client = openai.OpenAI()
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=stt_data['messages'],
            stream=True,
        )

        response_text = ""  # Initialize the response text
        for chunk in stream:
            # Check if 'choices' is in the chunk to avoid KeyError
            if 'choices' in chunk:
                delta = chunk['choices'][0].get('delta', {})
                # Check if 'content' is in delta to avoid KeyError
                if 'content' in delta:
                    response_text += delta['content']  # Accumulate the content
                    print(delta['content'], end="")  # Print the content for debugging

        # Convert the response text to speech and save it as an MP3 file
        audio_path = extract_and_convert_to_tts(response_text)
        
        if audio_path:
            # Return success message with the path to the saved audio file
            return jsonify({"message": "success", "audio_path": str(audio_path)}), 200
        else:
            # Return error message if TTS conversion failed
            return jsonify({"error": "Failed to convert text to speech"}), 500

    except Exception as e:
        # Return error message if any exception occurs
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500
# --- End of STT Data Handling Subroutine ---

# --- Start of Text-to-Speech Subroutine ---
# Subroutine: Extract and Convert Text to Speech
def extract_and_convert_to_tts(text):
    """
    Extract text content from OpenAI completion response,
    convert the text to speech using OpenAI TTS API, and save the MP3 file.
    
    :param text: Text to convert to speech
    :return: Path to the saved MP3 file or None if failed
    """
    try:
        print(f'Extracted text for TTS: {text}')
        
        # Define the path for the output audio file
        audio_path = AUDIO_DIR / 'response.mp3'

        # Send request to OpenAI TTS endpoint
        response = openai.audio.speech.create(
            model="tts-1",
            voice="shimmer",
            input=text
        )

        # Save the MP3 file using the streaming response method
        with open(audio_path, 'wb') as file:
            for chunk in response:
                file.write(chunk)

        print(f'MP3 saved to {audio_path}')
        return audio_path
        
    except Exception as e:
        # Print and return error message if any exception occurs during TTS conversion
        print(f"An error occurred during TTS conversion: {e}")
        return None
# --- End of Text-to-Speech Subroutine ---

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
