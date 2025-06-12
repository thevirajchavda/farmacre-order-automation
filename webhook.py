# import os
# from flask import Flask, request
# import logging
# import json
# import requests

# conversationHistory = ""
# message_body = ""
# app = Flask(__name__)
# @app.route('/webhook', methods=['GET', 'POST'])
# def webhook():
#     if request.method == 'GET':
#         # Verification
#         verify_token = "your_verify_token"
#         mode = request.args.get("hub.mode")
#         token = request.args.get("hub.verify_token")
#         challenge = request.args.get("hub.challenge")

#         if mode == "subscribe" and token == verify_token:
#             return challenge, 200
#         else:
#             return "Verification failed", 403

#     if request.method == 'POST':
#         global conversationHistory
#         data = request.get_json()
#         logging.basicConfig(level=logging.INFO)
#         logging.info("Received: %s", data)
#         # client = genai.Client(api_key="AIzaSyDD6et8LEH_gD-R64zt9X7Wnk_UCCVOXBw")
#         # answerFromAi = client.models.generate_content(model="gemini-2.0-flash",contents=,)
#         # Replace with your actual Gemini API key
#         GEMINI_API_KEY = "AIzaSyD9qG9S1nSipqpz5gPsorpoB890fUlEdS8"

#         url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
#         headers = {
#             'Content-Type': 'application/json'
#         }
#         if "messages" in data["entry"][0]["changes"][0]["value"]:
#             global message_body
#             message_body = data["entry"][0]["changes"][0]["value"]["messages"][0]["text"]["body"]
#             conversationHistory += "user: " + message_body
#         dataHaveToSend = {
#             "contents": [
#                 {
#                     "parts": [
#                         {
#                             "text": conversationHistory
#                         }
#                     ]
#                 }
#             ]
#         }
#         # Make the POST request
#         try:
#             answerFromAi = requests.post(url, headers=headers, data=json.dumps(dataHaveToSend))
#             answerFromAi.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
#             # Print the response
#             logging.info("ai answer :%s",answerFromAi.json()["candidates"][0]["content"]["parts"][0]["text"])
#             conversationHistory += "\nmodel: "+answerFromAi.json()["candidates"][0]["content"]["parts"][0]["text"]+"\n"

#         except requests.exceptions.RequestException as e:
#             logging.info("An error occurred: %s",str(e))

#         url = "https://graph.facebook.com/v23.0/700474829809739/messages"
#         headers = {
#             "Authorization": "Bearer EAA6iFxZC6E44BOx1fa3qNdY60ogEguIwsP9mOaZBYP2WednpI0W0S8YRZCW7lNCyHIOpATGsUMZAcRa7AsqR5zLrp3oKykJqPujaQ8IZCH630dyZCZAYE8WhUsSlHPZAcymJcX0hCfKXZC2VaBZBr18S8JQc0g9QWZCW8VnMobuOPxWGBHG6owSTRJWyKZCInjPU9laJv3urcNL0gqrlw9ItUYa5eMrHLVvlIE0ZD",
#             "Content-Type": "application/json"
#         }

#         dataHaveToSend = {
#             "messaging_product": "whatsapp",
#             "to": data["entry"][0]["changes"][0]["value"]["messages"][0]["from"],  # Receiver
#             "type": "text",
#             "text": {"body": answerFromAi.json()["candidates"][0]["content"]["parts"][0]["text"]}
#         }
#         r = requests.post(url, headers=headers, json=dataHaveToSend)
#         logging.info("Received2: %s", str(r.status_code)+str( r.text))
#         return "OK", 200

# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port)
import os
from flask import Flask, request
import logging
import json
import requests

conversationHistory = ""
app = Flask(__name__)

# Configure logging for better visibility
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

@app.route('/webhook', methods=['GET', 'POST'])
def webhook():
    if request.method == 'GET':
        # Verification for webhook setup
        verify_token = "your_verify_token" # IMPORTANT: Replace with your actual verify token
        mode = request.args.get("hub.mode")
        token = request.args.get("hub.verify_token")
        challenge = request.args.get("hub.challenge")

        if mode == "subscribe" and token == verify_token:
            logging.info("Webhook verification successful.")
            return challenge, 200
        else:
            logging.warning("Webhook verification failed.")
            return "Verification failed", 403

    if request.method == 'POST':
        global conversationHistory
        data = request.get_json()
        logging.info("Received incoming webhook data: %s", json.dumps(data, indent=2))

        # Replace with your actual Gemini API key
        GEMINI_API_KEY = "AIzaSyD9qG9S1nSipqpz5gPsorpoB890fUlEdS8" # IMPORTANT: Keep this secure and do not expose in production

        # Extract relevant information only if it's a message event
        # This is where the KeyError was happening, so we add a check.
        if "entry" in data and len(data["entry"]) > 0 and \
           "changes" in data["entry"][0] and len(data["entry"][0]["changes"]) > 0 and \
           "value" in data["entry"][0]["changes"][0] and \
           "messages" in data["entry"][0]["changes"][0]["value"] and \
           len(data["entry"][0]["changes"][0]["value"]["messages"]) > 0:

            message_data = data["entry"][0]["changes"][0]["value"]["messages"][0]
            from_number = message_data["from"] # Sender's phone number
            message_type = message_data["type"]

            if message_type == "text":
                message_body = message_data["text"]["body"]
                logging.info("Received text message from %s: %s", from_number, message_body)

                # Update conversation history
                conversationHistory += "user: " + message_body + "\n"

                # Prepare payload for Gemini API
                gemini_api_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
                gemini_headers = {
                    'Content-Type': 'application/json'
                }
                gemini_payload = {
                    "contents": [
                        {
                            "parts": [
                                {
                                    "text": conversationHistory
                                }
                            ]
                        }
                    ]
                }

                # Make the POST request to Gemini API
                ai_response_text = "Sorry, I couldn't generate a response."
                try:
                    gemini_response = requests.post(gemini_api_url, headers=gemini_headers, data=json.dumps(gemini_payload))
                    gemini_response.raise_for_status()  # Raise an exception for HTTP errors (4xx or 5xx)
                    
                    # Parse the Gemini API response
                    gemini_result = gemini_response.json()
                    if "candidates" in gemini_result and len(gemini_result["candidates"]) > 0 and \
                       "content" in gemini_result["candidates"][0] and \
                       "parts" in gemini_result["candidates"][0]["content"] and \
                       len(gemini_result["candidates"][0]["content"]["parts"]) > 0:
                        ai_response_text = gemini_result["candidates"][0]["content"]["parts"][0]["text"]
                        logging.info("AI generated response: %s", ai_response_text)
                        conversationHistory += "model: " + ai_response_text + "\n"
                    else:
                        logging.warning("Gemini API response missing expected structure: %s", gemini_result)

                except requests.exceptions.RequestException as e:
                    logging.error("Error calling Gemini API: %s", str(e))
                except json.JSONDecodeError as e:
                    logging.error("Error decoding Gemini API response JSON: %s", str(e))
                
                # Send the AI response back to WhatsApp
                whatsapp_api_url = "https://graph.facebook.com/v23.0/700474829809739/messages" # IMPORTANT: Replace with your actual WhatsApp Business Account ID if different
                whatsapp_headers = {
                    "Authorization": "Bearer EAA6iFxZC6E44BOx1fa3qNdY60ogEguIwsP9mOaZBYP2WednpI0W0S8YRZCW7lNCyHIOpATGsUMZAcRa7AsqR5zLrp3oKykJqPujaQ8IZCH630dyZCZAYE8WhUsSlHPZAcymJcX0hCfKXZC2VaBZBr18S8JQc0g9QWZCW8VnMobuOPxWGBHG6owSTRJWyZZCInjPU9laJv3urcNL0gqrlw9ItUYa5eMrHLVvlIE0ZD", # IMPORTANT: Replace with your actual permanent access token
                    "Content-Type": "application/json"
                }

                whatsapp_payload = {
                    "messaging_product": "whatsapp",
                    "to": from_number,  # Receiver's phone number
                    "type": "text",
                    "text": {"body": ai_response_text}
                }

                try:
                    whatsapp_response = requests.post(whatsapp_api_url, headers=whatsapp_headers, json=whatsapp_payload)
                    whatsapp_response.raise_for_status() # Raise an exception for HTTP errors
                    logging.info("WhatsApp message sent. Status: %s, Response: %s", whatsapp_response.status_code, whatsapp_response.text)
                except requests.exceptions.RequestException as e:
                    logging.error("Error sending message to WhatsApp: %s", str(e))
                except json.JSONDecodeError as e:
                    logging.error("Error decoding WhatsApp API response JSON: %s", str(e))
            else:
                logging.info("Received non-text message type: %s. Not processing.", message_type)
        else:
            logging.info("Received a webhook event without a 'messages' key or a recognized structure. Skipping processing.")

        return "OK", 200

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    logging.info(f"Starting Flask app on port {port}")
    app.run(host="0.0.0.0", port=port)
