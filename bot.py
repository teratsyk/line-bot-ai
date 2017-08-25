import os
import requests
import json
import tensorflow as tf
import multiprocessing as mp

from flask import Flask
from flask import request

LINE_API_REPLY ='https://api.line.me/v2/bot/message/reply'
LINE_HEADERS = {
    'Content-type': 'application/json; charset=UTF-8',
    'Authorization': 'Bearer {}'.format(os.environ['CHANNEL_ACCESS_TOKEN'])
}

def send_reply(body):
    for event in body['events']:
        responses = []

        if event['type'] == 'message':
            message = event['message']
            text = ''

            if message['type'] == 'text':
                # そのままオウム返し
                text = message['text']
            else:
                # テキスト以外のメッセージにはてへぺろしておく
                text = 'てへぺろ'

            responses.append({'type': 'text', 'text': text})

        # 返信する
        reply = {
            'replyToken': event['replyToken'],
            'messages': responses
        }
        requests.post(LINE_API_REPLY, json.dumps(reply), LINE_HEADERS)

app = Flask(__name__)

@app.route("/webhook", methods=['POST'])
def webhook():
    send_reply(request.json)
    return '', 200, {}

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