import os
import requests
import json
import logging
import tensorflow as tf
import multiprocessing as mp

from flask import Flask
from flask import request

LINE_API_REPLY ='https://api.line.me/v2/bot/message/reply'
LINE_HEADERS = {
    'Content-type': 'application/json',
    'Authorization': 'Bearer {}'.format(os.environ['CHANNEL_ACCESS_TOKEN'])
}

def send_reply(body):
    for event in body['events']:
        logging.debug(event)
        responses = []

        if event['type'] == 'message':
            message = event['message']
            text = ''

            if message['type'] == 'text':
                text = message['text']
            else:
                text = '(´・ω・`)'

            responses.append({'type': 'text', 'text': text})

        # 返信する
        reply = {
            'replyToken': event['replyToken'],
            'messages': responses
        }
        requests.post(LINE_API_REPLY, data=json.dumps(reply), headers=LINE_HEADERS)

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