import os
import sys

from flask import Flask, jsonify, request, abort, send_file
from dotenv import load_dotenv
from linebot import LineBotApi, WebhookParser
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

from fsm import TocMachine
from utils import send_text_message

load_dotenv()


machine = TocMachine(
    states=[
            "user", "main_table",
            "ptt", "pttbox", "pttlive", "ptthot",
            "highlights", "yt_search", "yt_output", "choose_team", "show_team_record", "search_player", "show_player_stats",
            "data", "show_stats_leader"
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
            "source": "main_table",
            "dest": "highlights",
            "conditions": "is_going_to_highlights",
        },
        {
            "trigger": "advance",
            "source": "main_table",
            "dest": "data",
            "conditions": "is_going_to_data",
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
            "trigger": "advance",
            "source": "highlights",
            "dest": "yt_search",
            "conditions": "is_going_to_yt_search",
        },
        {
            "trigger": "advance",
            "source": "yt_search",
            "dest": "yt_output",
            "conditions": "is_going_to_yt_output",
        },
        {
            "trigger": "advance",
            "source": "data",
            "dest": "choose_team",
            "conditions": "is_going_to_choose_team",
        },
        {
            "trigger": "advance",
            "source": "choose_team",
            "dest": "show_team_record",
            "conditions": "is_going_to_show_team_record",
        },
        {
            "trigger": "advance",
            "source": "data",
            "dest": "search_player",
            "conditions": "is_going_to_search_player",
        },
        {
            "trigger": "advance",
            "source": "search_player",
            "dest": "show_player_stats",
            "conditions": "is_going_to_show_player_stats",
        },
        {
            "trigger": "advance",
            "source": "data",
            "dest": "show_stats_leader",
            "conditions": "is_going_to_show_stats_leader",
        },
        {
            "trigger": "go_back", 
            "source": [
                        "ptt", "pttbox", "pttlive", "ptthot",
                        "highlights", "yt_search", "yt_output", "choose_team", "show_team_record", "search_player", "show_player_stats",
                        "data", "show_stats_leader"
                    ], 
            "dest": "main_table",
            },
    ],
    initial="user",
    auto_transitions=False,
    show_conditions=True,
)

final_states = [
    "pttbox", "pttlive", "ptthot",
    "yt_output", "show_team_record", "show_player_stats",
    "show_stats_leader"
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
        
        response = True
        for state in final_states:
            if machine.state==state:
                response = False

        if response:
            response = machine.advance(event)
        else:
            send_text_message(event.reply_token, "Initialization")
            machine.go_back()
       
        # line_bot_api.reply_message(
        #     event.reply_token, TextSendMessage(text=event.message.text)
        # )

    return "OK"


@app.route("/webhook", methods=["POST"])
def webhook_handler():
    signature = request.headers["X-Line-Signature"]
    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info(f"Request body: {body}")

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
        print(f"\nFSM STATE: {machine.state}")
        print(f"REQUEST BODY: \n{body}")

        response = machine.advance(event)
        if response == False:
            send_text_message(event.reply_token, "Not Entering any State")

    return "OK"


@app.route("/show-fsm", methods=["GET"])
def show_fsm():
    machine.get_graph().draw("fsm.png", prog="dot", format="png")
    return send_file("fsm.png", mimetype="image/png")


if __name__ == "__main__":
    port = os.environ.get("PORT", 8000)
    app.run(host="0.0.0.0", port=port, debug=True)
