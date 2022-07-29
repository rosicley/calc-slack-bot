import message_models as Models
import steps
from operatons import do_operation, get_op_text


class SlackBot:
    def __init__(self, client):
        self.db: dict = {}
        self.current_channel = None
        self.client = client

    def send_message(
        self,
        message: str,
        channel: str,
        attachments: list = [],
    ):
        self.client.chat_postMessage(
            channel=channel,
            blocks=Models.text_message_blocks(message),
            attachments=attachments,
        )

    def send_options_message(self, channel_id: str):

        self.client.chat_postMessage(
            channel=channel_id,
            blocks=Models.options_blocks,
        )

    def finish_conversation(self, channel_id: str):
        self.db.pop(channel_id)
        self.send_message(
            channel=channel_id,
            message=Models.op_finished_txt,
        )

    def message_receved(self, payload):
        event = payload.get("event", {})
        channel_id = event.get("channel")
        text = event.get("text")

        channel_type = event.get("channel_type")

        if event.get("bot_id") or event.get("subtype") == "message_changed":
            return

        if channel_type == "im":
            if text == "test":
                self.test(channel_id)
                return
            if text == "options" or not self.db.get(channel_id):
                self.db[channel_id] = {"step": steps.OPTIONS}
                self.send_options_message(
                    channel_id=channel_id,
                )
            elif self.db.get(channel_id):
                if self.db[channel_id]["step"] == steps.OPTIONS:
                    return
                elif self.db[channel_id]["step"] == steps.WAIT_N1:
                    try:
                        num = float(text)
                        self.db[channel_id]["n1"] = num
                        self.db[channel_id]["step"] = steps.WAIT_N2
                        self.send_message(
                            channel=channel_id,
                            message=Models.second_number_txt,
                        )
                    except ValueError:
                        self.send_message(
                            channel=channel_id,
                            message=Models.value_number_error_txt,
                        )
                elif self.db[channel_id]["step"] == steps.WAIT_N2:
                    try:
                        num = float(text)
                        self.db[channel_id]["n2"] = num
                        res = do_operation(self.db[channel_id])
                        self.db[channel_id]["step"] = steps.FINISH

                        self.send_message(
                            channel=channel_id,
                            message=Models.answer_txt.format(res),
                        )
                    except ValueError:
                        self.send_message(
                            channel=channel_id,
                            message=Models.value_number_error_txt,
                        )
                elif self.db[channel_id]["step"] == steps.FINISH:
                    if text == "y":
                        self.send_options_message(
                            channel_id=channel_id,
                        )

                    else:
                        self.finish_conversation(channel_id=channel_id)
                elif self.db[channel_id]["step"] == "kill":
                    self.finish_conversation(channel_id=channel_id)

    def button_pressed(self, payload):

        block_id = payload["actions"][0]["block_id"]
        if block_id == "chosen_action":
            self.button_chosen_operation(payload)

    def button_chosen_operation(self, payload):

        channel_id = payload.get("channel").get("id")
        original_message = payload.get("message")
        ts = original_message.get("ts")
        actions = payload.get("actions")
        value = actions[0].get("value")
        op_text = get_op_text(value)

        self.client.chat_update(
            channel=channel_id,
            ts=ts,
            blocks=Models.text_message_blocks(
                Models.first_number_txt.format(op_text)
            ),
            attachments=[],
        )

        self.db[channel_id] = {"step": "wait_n1", "op": value}
