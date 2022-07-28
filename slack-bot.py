import json
import os

import slack
from dotenv import load_dotenv
from flask import Flask
from slackeventsapi import SlackEventAdapter

load_dotenv()

app = Flask(__name__)

client = slack.WebClient(token=os.environ["SLACK_TOKEN"])

slack_event_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app
)


def send_message(
    message: str, attachments: list = [], channel: str = "slack-bot"
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


@slack_event_adapter.on("message")
def message(payload):
    event = payload.get("event", {})
    channel_id = event.get("channel")
    user_id = event.get("user")
    text = event.get("text")

    bot_id = client.api_call("auth.test")["user_id"]
    channel_type = event.get("channel_type")

    if bot_id == user_id:
        return

    if channel_type != "im":
        send_message(message=text, channel=channel_id)
        print(json.dumps(payload))
        print(bot_id)
    else:
        message = "Would you like to play a game?"
        attachments = [
            {
                "text": "Choose a game to play",
                "fallback": "You are unable to choose a game",
                "callback_id": "wopr_game",
                "color": "#3AA3E3",
                "attachment_type": "default",
                "actions": [
                    {
                        "name": "game",
                        "text": "Chess",
                        "type": "button",
                        "value": "chess",
                    },
                    {
                        "name": "game",
                        "text": "Falken's Maze",
                        "type": "button",
                        "value": "maze",
                    },
                    {
                        "name": "game",
                        "text": "Thermonuclear War",
                        "style": "danger",
                        "type": "button",
                        "value": "war",
                        "confirm": {
                            "title": "Are you sure?",
                            "text": (
                                "Wouldn't you prefer a good game of chess?"
                            ),
                            "ok_text": "Yes",
                            "dismiss_text": "No",
                        },
                    },
                ],
            }
        ]
        send_message(
            message=message, attachments=attachments, channel=channel_id
        )


if __name__ == "__main__":
    app.run(debug=True)


# send_message(
# "```Hello Human!\nHello Human!!\nHello Human!!!```", channel="teste"
# )
