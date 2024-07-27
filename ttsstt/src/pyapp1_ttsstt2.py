from gevent import monkey  # type: ignore
monkey.patch_all()

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
dotenv_path = '/home/eaglesvn/Documents/dockerz/vuepy03/ttsstt/.env'
load_dotenv(dotenv_path)

app1_mod_ttsstt = Flask(__name__)
app1_mod_ttsstt.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
socketio = SocketIO(app1_mod_ttsstt, async_mode='gevent')

# Initialize OpenAI client using environment variable for API key
client = OpenAI(
    api_key=os.getenv('OPENAI_API_KEY'),
    base_url='https://api.openai.com/v1/chat/completions'
)

@socketio.on('stt_data')
def handle_stt_data(stt_data):
    try:
        print(f'Received JSON data: {stt_data}')

        # Forward the STT data to OpenAI API using the correct method
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Use the specified model
            messages=stt_data['messages']  # assuming the JSON contains a 'messages' field
        )

        # Print the response from OpenAI API
        print(response.choices[0].message.content)

        # Emit the response back to the client
        emit('stt_response', response.model_dump())

    except Exception as e:
        print(f"An error occurred: {e}")
        emit('stt_response', {"error": str(e)})

# Define the endpoint as app1_endpoint_ttsstt
app1_endpoint_ttsstt = app1_mod_ttsstt

@app1_mod_ttsstt.route('/app1/api/app1_endpoint_ttsstt', methods=['POST'])
def post_stt_data():
    try:
        stt_data = request.json
        print(f'Received JSON data via HTTP POST: {stt_data}')

        # Forward the STT data to OpenAI API using the correct method
        response = client.chat.completions.create(
            model="gpt-4-turbo",  # Use the specified model
            messages=stt_data['messages']  # assuming the JSON contains a 'messages' field
        )

        # Print the response from OpenAI API
        print(response.choices[0].message.content)

        return jsonify(response.model_dump()), 200

    except Exception as e:
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    socketio.run(app1_mod_ttsstt, debug=os.getenv('FLASK_DEBUG') == '1', host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'), port=5001)
