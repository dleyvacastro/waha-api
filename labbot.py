import json
import asyncio

from flask import Flask
from flask import request
from pprint import pprint

from wahaAPI import safeSendMessage
import db_manager

app = Flask(__name__)

lab_data = json.load(open('support_data.json', 'r'))


@app.route("/")
def whatsapp_echo():
    return "WhatsApp Echo Bot is ready!"


@app.route("/bot", methods=["GET", "POST"])
async def whatsapp_webhook():
    data = request.get_json()
    # pprint(data)
    if request.method == "GET":
        return "WhatsApp Echo Bot is ready!"

    if data["event"] != "message":
        # We can't process other event yet
        return f"Unknown event {data['event']}"

    # Payload that we've got
    payload = data["payload"]
    # The text
    text = payload["body"]
    # Number in format 1231231231@c.us or @g.us for group
    chat_id = payload["from"]
    # Message ID - false_11111111111@c.us_AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA
    message_id = payload['id']
    # For groups - who sent the message
    participant = payload.get('participant')

    #db_manager.create_case(payload)

    await db_manager.manage_message(payload)


    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
