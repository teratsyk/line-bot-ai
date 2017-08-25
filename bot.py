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
DOCOMO_API_DIALOGUE = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue'
DOCOMO_HEADERS = {
    'Content-type': 'application/json'
}

def get_username():
    '''LINEユーザ名を取得'''
    return 'お前'

def get_context():
    '''ユーザごとのコンテキストをredis等から取得'''
    return ''

def set_context(context):
    '''ユーザごとのコンテキストをredis等に保存'''


def get_dialogue(text):
    '''入力されたテキストに対するレスポンスを生成する'''
    response_text = ''

    params = {
        "utt": text,
        "context": get_context(),
        "nickname": get_username(),
        "mode": "dialog",
        "t": "20"
    }
    r = requests.post(
        "{}?APIKEY={}".format(DOCOMO_API_DIALOGUE, os.environ['DOCOMO_API_KEY']),
        data=json.dumps(params),
        headers=DOCOMO_HEADERS
    )
    logging.debug(r)
    if r.status_code == 200:
        set_context(r.text.context)
        response_text = r.text.utt

    return response_text

def send_reply(body):
    '''
    リプライ返信を行う
    テキストが送られたら対話テキストを
    それ以外は顔文字を返す
    '''
    for event in body['events']:
        logging.debug(event)
        responses = []

        if event['type'] == 'message':
            message = event['message']
            text = ''

            if message['type'] == 'text':
                text = get_dialogue(message['text'])
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
app.debug = True

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
    port = int(os.environ.get('PORT', 5000))
    app.run(port=port)