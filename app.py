import os
import yaml
from dotenv import load_dotenv
from os.path import join, dirname
from decouple import config
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import pandas as pd
import random

app = Flask(__name__)

def get_configuration():
    # configuration files for accessing environment 
    dotenv_path = join(dirname(__file__), '.env')
    load_dotenv(dotenv_path)

    conf = {}
    conf["secret"] = os.getenv("LINE_CHANNEL_SECRET")
    conf["token"] = os.getenv("LINE_CHANNEL_ACCESS_TOKEN")

    return conf

with open("dataset.yaml", 'r') as f:
    dataset = yaml.load(f)
with open("utterance.yaml", 'r') as f:
    utterance = yaml.load(f)

conf = get_configuration()

line_bot_api = LineBotApi(conf['token'])
handler = WebhookHandler(conf['secret'])
books = pd.read_csv('books.csv')

def query_keywords(keywords, top=5):
    results = books[books['title'].str.contains(keywords, case=False)][:top]

def query_search(keywords):
    query = "Here the results list book by {} keywords".format(keywords)
    return query

def check_status(unique_id):
    query = "This is your unique id {}, but sorry I not integrated yet with database. \
        Wait for several days please :)".format(unique_id)
    return query

@app.route("/callback", methods=['POST'])
def callback():
    signature = request.headers['X-Line-Signature']

    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_text_message(event):
    phrase = str(event.message.text).lower()
    for key in dataset.keys():
        if phrase in dataset[key]:
            intent = key

    if intent == "greetings":
        send_text = utterance["utter_greetings"]
    elif " ".join(phrase.split(' ')[:2]) == "search book":
        send_text = [query_search(" ".join(phrase.split(' ')[2:]))]
    elif phrase.split(' ')[0] == "status":
        send_text = [check_status(phrase.split(' ')[1:])]
    else:
        send_text = ["Sorry now I just able to search book or check status"]

    for text in send_text:
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=text)
        )

if __name__ == "__main__":
    port = 5000
    # app.run(host='0.0.0.0', port=port, ssl_context=('server.crt', 'server.key'))
    app.run(host='0.0.0.0', port=port)
