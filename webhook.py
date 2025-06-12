import os
from flask import Flask, request
import logging
import json
import requests

app = Flask(__name__)

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verification
        verify_token = "your_verify_token"
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            return challenge, 200
        else:
            return "Verification failed", 403

    if request.method == 'POST':
        data = request.get_json()
        logging.basicConfig(level=logging.INFO)
        logging.info("Received: %s", data)
        # client = genai.Client(api_key="AIzaSyDD6et8LEH_gD-R64zt9X7Wnk_UCCVOXBw")
        # answerFromAi = client.models.generate_content(model="gemini-2.0-flash",contents=,)
        # Replace with your actual Gemini API key
        GEMINI_API_KEY = "AIzaSyD9qG9S1nSipqpz5gPsorpoB890fUlEdS8"

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
        headers = {
            'Content-Type': 'application/json'
        }
        dataHaveToSend = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
                        }
                    ]
                }
            ]
        }

        # Make the POST request
        try:
            answerFromAi = requests.post(url, headers=headers, data=json.dumps(dataHaveToSend))
            answerFromAi.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
            # Print the response
            logging.info("ai answer :%s",answerFromAi.json()["candidates"][0]["content"]["parts"][0]["text"])

        except requests.exceptions.RequestException as e:
            logging.info("An error occurred: %s",str(e))

        url = "https://graph.facebook.com/v23.0/700474829809739/messages"
        headers = {
            "Authorization": "Bearer EAA6iFxZC6E44BO1ZAx15gxgbqwro3QptFfZAMHhG6bZAzfSKJ1WnDmBeiFRrLrIJ0MeRR7PLItFuZBjWyqWiqqKvP0O2DJAWe7XZAIeZAHZCHw5NuK7fKdAGW7ehLnql3Hd8Ls54tkhVzr4I6xZA7QwwOflvmCApjmMuPbfH8muZCAzQnOHwI7V3MyQ7qYFvYdYUkXmcQgXkkf7He4g08TlhKsp0mQBCuZBTMs4kCgZD",
            "Content-Type": "application/json"
        }
        dataHaveToSend = {
            "messaging_product": "whatsapp",
            "to": data["entry"][0]["changes"][0]["value"]["messages"][0]["from"],  # Receiver
            "type": "text",
            "text": {"body": answerFromAi.json()["candidates"][0]["content"]["parts"][0]["text"]}
        }
        r = requests.post(url, headers=headers, json=dataHaveToSend)
        logging.info("Received2: %s", str(r.status_code)+str( r.text))
        return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
