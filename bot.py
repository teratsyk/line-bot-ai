import os
import requests
import json
import tensorflow as tf
import multiprocessing as mp

from flask import Flask
from flask import request

LINE_API_PROFILE = 'https://api.line.me/v2/profile'
LINE_API_REPLY ='https://api.line.me/v2/bot/message/reply'
LINE_HEADERS = {
    'Content-type': 'application/json',
    'Authorization': 'Bearer {}'.format(os.environ['CHANNEL_ACCESS_TOKEN'])
}
DOCOMO_API_DIALOGUE = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue'
DOCOMO_HEADERS = {
    'Content-type': 'application/json'
}
# 20: 関西弁キャラ, 30: 赤ちゃんキャラ、指定なし: デフォルトキャラ
DOCOMO_API_CHARACTER = '20'

def get_nickname(lineId):
    '''LINE情報を取得'''
    name = 'あなた'

    r = requests.get(LINE_API_PROFILE + '/' + lineId, headers=LINE_HEADERS)
    if r.status_code == 200:
        body = r.json()
        print(body)
        name = body["displayName"]

    return name

def get_context():
    '''ユーザごとのコンテキストをredis等から取得'''
    context = ''
    mode = 'dialog'
    return [context, mode]

def set_context(lineid, context, mode):
    '''ユーザごとのコンテキストをredis等に保存'''
    # ラインIDをキーとしてコンテキスト、モードの保存

def get_dialogue(text, lineId):
    '''入力されたテキストに対するレスポンスを生成する'''
    response_utt = ''
    context, mode = get_context()

    params = {
        "utt": text,
        "context": context,
        "nickname": get_nickname(lineId),
        "mode": mode,
        "t": DOCOMO_API_CHARACTER
    }
    r = requests.post(
        "{}?APIKEY={}".format(DOCOMO_API_DIALOGUE, os.environ['DOCOMO_API_KEY']),
        data=json.dumps(params),
        headers=DOCOMO_HEADERS
    )
    if r.status_code == 200:
        body = r.json()
        print(body)
        set_context(lineid, body["context"], body["mode"])
        response_utt = body["utt"]

    return response_utt

def send_reply(body):
    '''
    リプライ返信を行う
    テキストが送られたら対話テキストを
    それ以外は顔文字を返す
    '''
    for event in body['events']:
        responses = []

        if event['type'] == 'message':
            message = event['message']
            text = ''

            if message['type'] == 'text':
                text = get_dialogue(message['text'], event['source']['userId'])
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
    print(request.json)
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