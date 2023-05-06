import os

import requests
from time import sleep
import random
import asyncio
from dotenv import load_dotenv
load_dotenv()


async def send_safe_message(chat_id, message_id, participant, text, reply):
    send_seen(chat_id=chat_id, message_id=message_id, participant=participant)
    start_typing(chat_id=chat_id)
    await asyncio.sleep(random.randint(1, 3))
    stop_typing(chat_id=chat_id)
    if reply:
        reply_message(chat_id=chat_id, message_id=message_id, text=text)
    else:
        send_message(chat_id=chat_id, text=text)


def start_typing(chat_id):
    response = requests.post(
        f"{os.getenv('WAAPI_URL')}/api/startTyping",
        json={
            "session": "default",
            "chatId": chat_id,
        },
    )
    response.raise_for_status()


def stop_typing(chat_id):
    response = requests.post(
        f"{os.getenv('WAAPI_URL')}/api/stopTyping",
        json={
            "session": "default",
            "chatId": chat_id,
        },
    )
    response.raise_for_status()


def send_message(chat_id, text):
    """
    Send message to chat_id.
    :param chat_id: Phone number + "@c.us" suffix - 1231231231@c.us
    :param text: Message for the recipient
    """
    # Send a text back via WhatsApp HTTP API
    response = requests.post(
        f"{os.getenv('WAAPI_URL')}/api/sendText",
        json={
            "chatId": chat_id,
            "text": text,
            "session": "default",
        },
    )
    response.raise_for_status()


def reply_message(chat_id, message_id, text):
    response = requests.post(
        f"{os.getenv('WAAPI_URL')}/api/reply",
        json={
            "chatId": chat_id,
            "text": text,
            "reply_to": message_id,
            "session": "default",
        },
    )
    response.raise_for_status()


def send_seen(chat_id, message_id, participant):
    response = requests.post(
        f"{os.getenv('WAAPI_URL')}/api/sendSeen",
        json={
            "session": "default",
            "chatId": chat_id,
            "messageId": message_id,
            "participant": participant,
        },
    )
    response.raise_for_status()
