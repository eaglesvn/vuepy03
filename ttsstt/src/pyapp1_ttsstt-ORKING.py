from flask import Flask, request, jsonify
from openai import OpenAI
import os
from dotenv import load_dotenv

# Load environment variables from the .env file
dotenv_path = '/home/eaglesvn/Documents/dockerz/vuepy03/ttsstt/.env'
load_dotenv(dotenv_path)

# Initialize Flask application
app1_mod_ttsstt = Flask(__name__)
app1_mod_ttsstt.config['SECRET_KEY'] = os.getenv('SECRET_KEY')

# Initialize OpenAI 1.35client using environment variable for API key
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

@app1_mod_ttsstt.route('/app1/api/app1_endpoint_ttsstt', methods=['POST'])
def post_stt_data():
    try:
        # Receive formatted message as JSON from the client
        stt_data = request.json
        print(f'Received formatted JSON data via HTTP POST: {stt_data}')

        # Forward formatted message to OpenAI API 1.35 to generate a completion
        completion = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=stt_data['messages']
        )

        # Extract the text response from OpenAI 1.35
        # # completion.choices[0].message['content'] is deprecated
        response_text = completion.choices[0].message.content 
        print(f'Response from OpenAI: {response_text}')

        # Return the response from OpenAI 1.35
        return jsonify({"response": response_text}), 200

    except Exception as e:
        # Return error message if any exception occurs
        print(f"An error occurred: {e}")
        return jsonify({"error": str(e)}), 500

@app1_mod_ttsstt.route('/test', methods=['GET'])
def test_route():
    return "Test route working", 200

if __name__ == '__main__':
    app1_mod_ttsstt.run(debug=os.getenv('FLASK_DEBUG') == '1', host=os.getenv('FLASK_RUN_HOST', '0.0.0.0'), port=6961)
