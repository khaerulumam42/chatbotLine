# Line developer docs:
# https://developers.line.biz/en/docs/messaging-api/building-bot/
"""
import base64
import hashlib
import hmac

channel_secret = ... # Channel secret string
body = ... # Request body string
hash = hmac.new(channel_secret.encode('utf-8'),
    body.encode('utf-8'), hashlib.sha256).digest()
signature = base64.b64encode(hash)"""
# Compare X-Line-Signature request header and the signature

import yaml
from flask import Flask, request, abort

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

with open("config.yml", 'r') as ymlfile:
    config = yaml.load(ymlfile)

line_bot_api = LineBotApi(config["line_channel"]["id"])
handler = WebhookHandler(config["line_channel"]["secret"])


@app.route("/callback", methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run()