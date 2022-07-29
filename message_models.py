first_number_txt = (
    "You chose the `{}` Option,\n Please inform the first number: "
)
second_number_txt = "Please Inform the second number:"
value_number_error_txt = "Please send a valid number!"
answer_txt = (
    "Your answer is : `{}`\n Do would you like to do another operation? `y` to"
    " yes or any other key to finish"
)
op_finished_txt = "Operation finished, thank you very much!"


options_blocks = [
    {
        "type": "section",
        "text": {
            "type": "mrkdwn",
            "text": "Choose the desired option:",
        },
    },
    {
        "type": "actions",
        "block_id": "chosen_action",
        "elements": [
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Addition"},
                "value": "add",
                "action_id": "btn-add",
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Subtraction",
                },
                "value": "sub",
                "action_id": "btn-sub",
            },
            {
                "type": "button",
                "text": {
                    "type": "plain_text",
                    "text": "Multiplication",
                },
                "value": "mul",
                "action_id": "btn-mul",
            },
            {
                "type": "button",
                "text": {"type": "plain_text", "text": "Division"},
                "value": "div",
                "action_id": "btn-div",
            },
        ],
    },
]


def text_message_blocks(msg: str) -> list:
    return [
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": msg,
            },
        },
    ]
