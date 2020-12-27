import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_image_message, send_text_message

load_dotenv()


machine = TocMachine(
    states=[
            "user", "main_table",
            "ptt", "pttbox", "pttlive", "ptthot",
            ],
    transitions=[
        {
            "trigger": "advance",
            "source": "user",
            "dest": "main_table",
            "conditions": "is_going_to_main_table",
        },
        {
            "trigger": "advance",
            "source": "main_table",
            "dest": "ptt",
            "conditions": "is_going_to_ptt",
        },
        {
            "trigger": "advance",
            "source": "ptt",
            "dest": "pttbox",
            "conditions": "is_going_to_pttbox",
        },
        {
            "trigger": "advance",
            "source": "ptt",
            "dest": "pttlive",
            "conditions": "is_going_to_pttlive",
        },
        {
            "trigger": "advance",
            "source": "ptt",
            "dest": "ptthot",
            "conditions": "is_going_to_ptthot",
        },
        {
            "trigger": "go_back", 
            "source": [
                        "main_table", "ptt", "pttbox", "pttlive", "ptthot",
                    ], 
            "dest": "user",
            },
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)


final_states = [
    "pttbox", "pttlive", "ptthot",
]

app = Flask(__name__, static_url_path="")


# get channel_secret and channel_access_token from your environment variable
channel_secret = os.getenv("LINE_CHANNEL_SECRET", None)
channel_access_token = os.getenv("LINE_CHANNEL_ACCESS_TOKEN", None)
if channel_secret is None:
    print("Specify LINE_CHANNEL_SECRET as environment variable.")
    sys.exit(1)
if channel_access_token is None:
    print("Specify LINE_CHANNEL_ACCESS_TOKEN as environment variable.")
    sys.exit(1)

line_bot_api = LineBotApi(channel_access_token)
parser = WebhookParser(channel_secret)


@app.route("/callback", methods=["POST"])
def callback():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # parse webhook body
    try:
        events = parser.parse(body, signature)
    except InvalidSignatureError:
        abort(400)


    # if event is MessageEvent and message is TextMessage, then echo text
    for event in events:
        if not isinstance(event, MessageEvent):
            continue
        if not isinstance(event.message, TextMessage):
            continue
        if not isinstance(event.message.text, str):
            continue
        if event.message.text.lower()=='fsm':
            machine.go_back()
            send_image_message(event.reply_token, 'https://github.com/anson0221/Line-Chat-Bot/blob/master/fsm.png?raw=true')
            continue
        
        response = False
        for state in final_states:
            if event.message.text==state:
                response = True
                break

        if response:
            machine.advance(event)
        else:
            machine.go_back()
            send_text_message(event.reply_token, "Please enter any string to show the main table.\n\nOr enter 'fsm' to show fsm.png")
            print(machine.state)
       
    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
