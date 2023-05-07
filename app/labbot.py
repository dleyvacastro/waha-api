import json

import pandas as pd
from flask import Flask
from flask import request
from flask import render_template
from pprint import pprint

import db_manager

app = Flask(__name__, template_folder='templates')

lab_data = json.load(open('support_data.json', 'r'))


@app.route("/")
def whatsapp_echo():
    # Load the data from the database
    df = db_manager.get_cases_df()

    # Define a function to apply background color to cells in the 'active' column
    def color_false(val):
        color = 'red' if val == False else 'green'
        return 'background-color: %s' % color

    # Apply the background color to the 'active' column
    df_styled = df.style.applymap(color_false, subset=pd.IndexSlice[:, ['active']])

    # Convert the styled DataFrame to an HTML table
    table_html = df_styled.to_html(classes='table')

    # Pass the table HTML and column names to the template
    return render_template('dashboard.html', tables=[table_html], titles=df.columns.values)


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

    # db_manager.create_case(payload)

    await db_manager.manage_message(payload)

    return "OK"


if __name__ == "__main__":
    app.run(debug=True, host="0.0.0.0")
