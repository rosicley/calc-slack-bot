import json
import os

import slack
from dotenv import load_dotenv
from flask import Flask, Response, request
from slackeventsapi import SlackEventAdapter

load_dotenv()

app = Flask(__name__)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])

slack_event_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app
)

# {
#   "channel_id": {data...}
# }
db: dict = {}


def send_message(
    message: str,
    channel: str,
    attachments: list = [],
):
    client.chat_postMessage(
        channel=channel,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message,
                },
            }
        ],
        attachments=attachments,
    )


def send_options_message(channel_id: str):
    message = "Choose the desired option"
    attachments = [
        {
            "fallback": "You are unable to choose",
            "callback_id": "cb_chosen_action",
            "color": "#3AA3E3",
            "attachment_type": "default",
            "actions": [
                {
                    "name": "operation",
                    "text": {"text": "Addition"},
                    "type": "button",
                    "value": "add",
                },
                {
                    "name": "operation",
                    "text": {"text": "Subtraction"},
                    "type": "button",
                    "value": "sub",
                },
                {
                    "name": "operation",
                    "text": {"text": "Multiplication"},
                    "type": "button",
                    "value": "mul",
                },
                {
                    "name": "operation",
                    "text": {"text": "Division"},
                    "type": "button",
                    "value": "div",
                },
            ],
        }
    ]

    send_message(
        message=message,
        attachments=attachments,
        channel=channel_id,
    )


def do_operation(channel: dict):
    res = ""
    op = channel["op"]
    n1 = channel["n1"]
    n2 = channel["n2"]
    if op == "add":
        res = n1 + n2
    elif op == "sub":
        res = n1 - n2
    elif op == "mul":
        res = n1 * n2
    elif op == "div":
        try:
            res = n1 / n2
        except ZeroDivisionError:
            res = "NaN"

    return str(res)


@slack_event_adapter.on("message")
def message(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    bot_id = client.api_call("auth.test")["user_id"]

    channel_type = event.get("channel_type")
    print(db)
    if event.get("bot_id") or event.get("subtype") == "message_changed":
        return

    if channel_type == "im":
        if text == "options" or not db.get(channel_id):
            db[channel_id] = {"step": "options"}
            send_options_message(
                channel_id=channel_id,
            )
        elif db.get(channel_id):
            if db[channel_id]["step"] == "options":
                return
            elif db[channel_id]["step"] == "wait_n1":
                try:
                    num = float(text)
                    db[channel_id]["n1"] = num
                    db[channel_id]["step"] = "wait_n2"
                    send_message(
                        channel=channel_id,
                        message="Please Inform the second number:",
                    )
                except ValueError:
                    send_message(
                        channel=channel_id,
                        message="Please send a valid number!",
                    )
            elif db[channel_id]["step"] == "wait_n2":
                try:
                    num = float(text)
                    db[channel_id]["n2"] = num
                    res = do_operation(db[channel_id])
                    db[channel_id]["step"] = "finish"

                    send_message(
                        channel=channel_id,
                        message=(
                            f"Your answer is : `{res}`\n Do would you like to"
                            " do another operation? `y` to yes or any other"
                            " key to finish"
                        ),
                    )
                except ValueError:
                    send_message(
                        channel=channel_id,
                        message="Please send a valid number!",
                    )
            elif db[channel_id]["step"] == "finish":
                if text == "y":
                    send_options_message(
                        channel_id=channel_id,
                    )

                else:
                    db.pop(channel_id)
                    send_message(
                        channel=channel_id,
                        message="Operation finished, thank you very much!",
                    )


@app.route("/slack/buttons", methods=["POST"])
def button_test():
    data = json.loads(request.form.get("payload"))
    channel_id = data.get("channel").get("id")
    original_message = data.get("original_message")
    ts = original_message.get("ts")

    actions = data.get("actions")
    value = actions[0].get("value")
    if value == "add":
        txt = "Addition"
    elif value == "sub":
        txt = "Subtraction"
    elif value == "mul":
        txt = "Multiplication"
    elif value == "div":
        txt = "Division"

    message = (
        f"You chose the `{txt}` Option,\n Please inform the first number: "
    )

    client.chat_update(
        channel=channel_id,
        ts=ts,
        blocks=[
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": message,
                },
            }
        ],
        attachments=[],
    )

    db[channel_id] = {"step": "wait_n1", "op": value}

    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
