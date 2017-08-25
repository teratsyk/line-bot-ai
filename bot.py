import os
import requests
import json
import redis
import tensorflow as tf
import multiprocessing as mp

from flask import Flask
from flask import request

REDIS_URL = os.environ.get('REDIS_URL') # herokuによって登録済み
LINE_API_PROFILE = 'https://api.line.me/v2/bot/profile'
LINE_API_REPLY ='https://api.line.me/v2/bot/message/reply'
LINE_HEADERS = {
    'Content-type': 'application/json',
    'Authorization': 'Bearer {}'.format(os.environ.get('CHANNEL_ACCESS_TOKEN'))
}
DOCOMO_API_KEY = os.environ.get('DOCOMO_API_KEY')
DOCOMO_API_DIALOGUE = 'https://api.apigw.smt.docomo.ne.jp/dialogue/v1/dialogue'
DOCOMO_HEADERS = {
    'Content-type': 'application/json'
}
# 20: 関西弁キャラ, 30: 赤ちゃんキャラ、指定なし: デフォルトキャラ
DOCOMO_API_CHARACTER = os.environ.get('DOCOMO_API_CHARACTER', '')

def get_nickname(lineId):
    '''LINE情報を取得'''
    name = 'あなた'

    if lineId:
        print(LINE_API_PROFILE + '/' + lineId)
        r = requests.get(LINE_API_PROFILE + '/' + lineId, headers=LINE_HEADERS)
        if r.status_code == 200:
            body = r.json()
            print(body)
            name = body["displayName"]
        else:
            print(r)

    return name

def set_context(lineId, context, mode):
    '''ユーザごとのコンテキストをredis等に保存'''
    # ラインIDをキーとしてコンテキスト、モードの保存
    r = redis.from_url(REDIS_URL)
    # expire: 180s
    r.setex(lineId, 180, json.dumps({'context': context, 'mode': mode}))

def get_context(lineId):
    '''ユーザごとのコンテキストをredis等から取得'''
    context = ''
    mode = 'dialog'

    r = redis.from_url(REDIS_URL)
    val = r.get(lineId)
    print(val)
    if val:
        data = json.loads(val.decode('utf-8'))
        context = data['context']
        mode = data['mode']

    return [context, mode]

def get_dialogue(text, lineId):
    '''入力されたテキストに対するレスポンスを生成する'''
    response_utt = ''
    context, mode = get_context(lineId)

    params = {
        "utt": text,
        "context": context,
        "nickname": get_nickname(lineId),
        "mode": mode,
        "t": DOCOMO_API_CHARACTER
    }
    r = requests.post(
        "{}?APIKEY={}".format(DOCOMO_API_DIALOGUE, DOCOMO_API_KEY),
        data=json.dumps(params),
        headers=DOCOMO_HEADERS
    )
    if r.status_code == 200:
        body = r.json()
        print(body)
        set_context(lineId, body["context"], body["mode"])
        response_utt = body["utt"]
    else:
        print(r)

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
            text = ''
            if event['message']['type'] == 'text':
                lineId = ''
                if event['source']['type'] == 'user':
                    lineId = event['source']['userId']
                text = get_dialogue(event['message']['text'], lineId)

            if not text:
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