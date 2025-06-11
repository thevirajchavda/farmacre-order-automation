import os
from flask import Flask, request
import logging
from google import genai

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
        client = genai.Client(api_key="AIzaSyDD6et8LEH_gD-R64zt9X7Wnk_UCCVOXBw")
        answerFromAi = client.models.generate_content(model="gemini-2.0-flash",contents=data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"],)
        url = "https://graph.facebook.com/v23.0/700474829809739/messages"
        headers = {
            "Authorization": "Bearer EAA6iFxZC6E44BO4IJaYRkA6mGpZBOIUSzA9FYoZB3C0ZBMN6mlrZCr7hIU9CKadsoJ4AJ8nuWN2hqHWYv100LLp5hPP1VCVFN7hVCqf1AsxrXQrjSCw4f8PAdEkNjeN6ZACFGFoxV47dBEfAToO2KZCHT2VVqaIdlCpDOWSthd0zZBWpyKakVcy9JhfR6DhExMiGYXqHfIeSYzlIZCIvK9AvllA3bFlRNtJrbHksZD",
            "Content-Type": "application/json"
        }
        dataHaveToSend = {
            "messaging_product": "whatsapp",
            "to": data["entry"][0]["changes"][0]["value"]["messages"][0]["from"],  # Receiver
            "type": "text",
            "text": {"body": answerFromAi}
        }
        r = requests.post(url, headers=headers, json=dataHaveToSend)
        logging.info("Received: %s", str(r.status_code)+str( r.text))
        return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port)
