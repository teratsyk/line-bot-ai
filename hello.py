import os
import requests
import json
import tensorflow as tf
import multiprocessing as mp

from flask import Flask
from flask import request


LINEBOT_API_EVENT ='https://trialbot-api.line.me/v1/events'
LINE_HEADERS = {
    'Content-type': 'application/json; charset=UTF-8',
    'X-Line-ChannelID':os.environ['CONTENT'], # Channel ID
    'X-Line-ChannelSecret':os.environ['CHANNEL'], # Channel secre
    'X-Line-Trusted-User-With-ACL':os.environ['MID'] # MID (of Channel)
}

def post_event(to, content):
    msg = {
        'to': [to],
        'toChannel': 1383378250, # Fixed  value
        'eventType': "138311608800106203", # Fixed value
        'content': content
    }
    print(msg)
    r = requests.post(LINEBOT_API_EVENT, LINE_HEADERS, json.dumps(msg))

def post_text(to, text):
    content = {
        'contentType':1,
        'toType':1,
        'text':text,
    }
    post_event(to, content)

app = Flask(__name__)

@app.route("/callback", methods=['POST'])
def callback():
    msgs = request.json['result']
    for msg in msgs:
        text = msg['content']['text']
        print(text)
        post_text(msg['content']['from'],text)
        return ''

@app.route('/')
def hello_world():
    core_num = mp.cpu_count()
    config = tf.ConfigProto(
        inter_op_parallelism_threads=core_num,
        intra_op_parallelism_threads=core_num )
    sess = tf.Session(config=config)

    hello = tf.constant('hello, tensorflow!')
    return sess.run(hello)

if __name__ == '__main__':
    app.run()