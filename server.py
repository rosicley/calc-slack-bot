import json
import os

import slack
from dotenv import load_dotenv
from flask import Flask, Response, request
from slackeventsapi import SlackEventAdapter

from slack_bot import SlackBot

load_dotenv()

app = Flask(__name__)


slack_event_adapter = SlackEventAdapter(
    os.environ["SLACK_SIGNING_SECRET"], "/slack/events", app
)

slack_bot = SlackBot(client=slack.WebClient(token=os.environ["SLACK_TOKEN"]))


@slack_event_adapter.on("message")
def message_receved(payload):
    slack_bot.message_receved(payload)
    return Response(), 200


@app.route("/slack/buttons", methods=["POST"])
def button_pressed():
    payload = json.loads(request.form.get("payload"))
    slack_bot.button_pressed(payload)

    return Response(), 200


if __name__ == "__main__":
    app.run(debug=True)
