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
import utils_api
import re
import traceback
import json

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
# books = pd.read_csv('books.csv')


def query_keywords(keywords, top=5):
    book_found = []
    book_list = utils_api.homelisting()
    i = 0
    if book_list["status"] == "1":
        for book in book_list["listing"]:
            for keyword in keywords.split(' '):
                if keyword in book["book_name"] and i < top:
                    book_found.extend(book)
    return book_found

def query_search(keywords):
    query = "Here the results list book by {} keywords".format(keywords)
    return query

def check_status(unique_id):
    query = "This is your unique id {}, but sorry I not integrated yet with database. \
        Wait for several days please :)".format(unique_id[0])
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

@app.route("/", methods=['GET', 'POST'])
def check_event():
    try:
        reply_token = request.json["events"][0]["replyToken"]
        user_id = request.json["events"][0]["source"]["userId"]
        phrase = request.json["events"][0]["message"]["text"].lower()
        intent = None

        if "name" in phrase and "phone" in phrase:
            data_dict = {}
            for data in phrase.split(','):
                data = re.sub(r"\s+", "", data)
                splitted_data = data.split(':')
                data_dict[splitted_data[0]] = " ".join(splitted_data[1:])
            
            reg = utils_api.register_user(username=data_dict["name"],\
                email=data_dict["email"],
                password=data_dict["password"],
                phone=data_dict["phone"])
            if reg["status"] == "1":
                send_text = """Yeay, registration succes. Your username is {0}, and your email is {1}. Please login by type 'login'""".format(data_dict["name"], data_dict["email"])
            else:
                send_text = """Unfortunately registration failed because {0}, please try again""".format(reg["message"])
        elif "email" in phrase and "password" in phrase:
            data_dict = {}
            for data in phrase.split(','):
                data = re.sub(r"\s+", "", data)
                splitted_data = data.split(':')
                data_dict[splitted_data[0]] = " ".join(splitted_data[1:])
            
            login = utils_api.login_user(email=data_dict["email"],\
                password=data_dict["password"])
            if login["status"] == "1":
                send_text = "Yeay, you are logged in as {}".format(login["username"])
                conn = utils_api.create_connection()
                utils_api.insert_logged_in(conn, user_id, \
                    data_dict["email"],data_dict["password"])
            else:
                send_text = "Unfortunaetly log in failed because {}, please try again".format(login["message"].lower())
        else:
            for key in dataset.keys():
                if phrase in dataset[key]:
                    intent = key

            if intent == "greetings":
                send_text = """Hey here LibraryBot. You can register and login to your account simply by type 'register' or 'login'. Hope it helps :)"""
                # utters = utterance["utter_greetings"]
                # for utter in utters:
                #     send_text = send_text + utter
            elif " ".join(phrase.split(' ')[:2]) == "search book":
                send_text = query_search(" ".join(phrase.split(' ')[2:]))
            elif phrase.split(' ')[0] == "status":
                send_text = check_status(phrase.split(' ')[1:])
            elif intent == "register":
                send_text = """for register, please fill your name, email, password and phone number. Don't use your email password for register to us. example: name:Michael, email:michael@gmail.com, password:michael123, phone: 083276724652. Please fill with exact same format example in one chat"""
            elif intent == "login":
                conn = utils_api.create_connection()
                logged_in = utils_api.check_logged_in(conn, user_id)
                if logged_in != []:
                    send_text = "You already logged in as {0}, if it is not your account please logout {0} and then type 'register' or 'login' to me".format(logged_in["username"])
                else:
                    send_text = """please fill your email and password that has been registered. example: email:michael@gmail.com, password:michael123. Please fill with exact same format example in one chat"""
            else:
                send_text = "Sorry now I just able to find book, register and login"

        line_bot_api.reply_message(
            reply_token,
            TextSendMessage(text=send_text)
        )
        return 'OK'
    except:
        return 'FAIL'


if __name__ == "__main__":
    table = utils_api.create_db()
    if table:
        port = 5000
        app.run(host='0.0.0.0', port=port)
    else:
        print("Please create table database and restart program")
