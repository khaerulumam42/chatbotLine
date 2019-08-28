import os
import yaml

from decouple import config
from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

with open("config.yml", 'r') as ymlfile:
    conf = yaml.load(ymlfile)

line_bot_api = LineBotApi(conf['line_channel']['token'])
handler = WebhookHandler(conf['line_channel']['secret'])


# def query_search(keyword):
#     query = """SELECT book_name, book_author from book WHERE \
#         book_name like '%{}%'""".format(keyword)
#     return query

# def check_status(unique_id):
#     query = """SELECT date_start, date_finish from rent WHERE \
#         unique_id={}""".format(unique_id)
#     return query

def query_search():
    query = "What book you wanna find?"
    return query

def check_status():
    query = "Sorry, I not integrated yet with database. \
        Wait for several days please :)"
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
    if str(event.message.text).lower == "search":
        send_text = query_search()
    elif str(event.message.text).lower == "check status":
        send_text = check_status()
    else:
        send_text = "Sorry now I just know about search or check status"

    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=send_text)
    )

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    # app.run(host='0.0.0.0', port=port, ssl_context=('server.crt', 'server.key'))
    app.run(host='0.0.0.0', port=port)
