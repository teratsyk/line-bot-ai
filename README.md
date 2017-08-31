# line-bot-ai

AIと会話したい

* ディープラーニングするのでtensorflowを使ってみる？
* ディープラーニングならpython？
* pythonならflaskが簡単そう
* 会話するならbotがいい
* お金かけたくないのでherokuで動かす

という感じで開始。  
下記のステップで作っていく。

1. まずはpythonでラインボット作成
2. docomoの会話APIで雑談できるように
3. tensorflowを使用して会話できるように

# 環境
* windows7（no NVIDIA GPU）
* Anaconda4.4.0
* Python3.5
    * `TensorFlow only supports version 3.5.x of Python on Windows.`
* tensorflow1.2.1 (CPU support only)
* flask

# インストール
* 公式: [Installing TensorFlow on Windows](https://www.tensorflow.org/install/install_windows)

### Anacondaインストール
* [インストーラ](https://repo.continuum.io/archive/Anaconda3-4.4.0-Windows-x86_64.exe)からインストールする

* Anaconda Navigatorを起動する

### Python3.5のインストール
* Anaconda4.4.0ではPython3.6がデフォルトなので別途3.5環境を用意する
  * [やり方は3種類ある](https://docs.continuum.io/anaconda/faq#how-do-i-get-the-latest-anaconda-with-python-3-5)が、最新のAnacondaに3.5環境を作成する
    * `We recommend that you download the latest version of Anaconda and then make a Python 3.5 environment.`

* Anacondaの左メニュー「Environments」を選択し、「Create」ボタンから新規環境を作成する
  * 環境名：任意（linebotとした）
  * pythonバージョン：3.5を選択

### tensorflowのインストール
* 作成したlinebot環境を選択し、リストの「installed」を「All」に変更し、右上の「Search Packages」に"tensorflow"を入力する
  * リストに"tensorflow"と"tensorflow-gpu"が表示されるので、"tensorflow"を選択し、下部のApplyをクリックする
  * 関連パッケージを含めたinstall候補が表示されるので、確認してApplyをクリック

### その他pythonライブラリのインストール
* 同様に `flask` , `requests` をインストール

### 確認
* 作成したlinebot環境のターミナルを開き（矢印をクリックし"open terminal"）、インストール確認
```
# pip freeze
backports.weakref==1.0rc1
bleach==1.5.0
click==6.7
Flask==0.12.2
html5lib==0.9999999
itsdangerous==0.24
Jinja2==2.9.6
Markdown==2.6.8
MarkupSafe==1.0
numpy==1.13.1
protobuf==3.2.0
six==1.10.0
tensorflow==1.2.1
Werkzeug==0.12.2
```
### Visual Studio CodeのPythonパス設定
* 「ファイル > 基本設定 > 設定」を開き、右上のリストを"ワークスペースの設定"に変更し下記を追記
  * `C:/Users/{ユーザ名}/AppData/Local/Continuum/Anaconda3/envs/linebot/python`

※予めプロジェクトフォルダを作り、フォルダごと開かないと"ワークスペースの設定"が選択できない？

### Hello Tensorflow on Heroku

* ソースコード

```
import tensorflow as tf
import multiprocessing as mp

from flask import Flask

app = Flask(__name__) 

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
```

* 起動

```
$ python hello.py
  * Running on http://127.0.0.1:5000/
```


* ブラウザで確認

# heroku設定

### アカウント作成
* アカウント作成
  *https://signup.heroku.com/

* heroku toolbeltインストール
  * https://devcenter.heroku.com/articles/heroku-cli#download-and-install

* herokuにログイン
```
$ heroku login
(登録したメールアドレス)
(password)
```

### heroku向け設定(on Local)

* gunicorn(WSGIサーバ)のインストール
  * AnacondaのGUIからは入れられないのでコマンドで実施
```
$ conda install -c anaconda gunicorn
```

※windowsの場合、condaでgunicornパッケージがインストールできないので、ローカルではpipで入れる

* Procfile作成
```
web: gunicorn hello:app --log-file -
```

* conda用のrequirements.txt作成
```
$ conda list -e > conda-requirements.txt
```
* conda-requirements.txtにgunicornを追加
```
gunicorn=19.1.0=py35_0
```

* runtime.txt作成
  * anaconda環境に合わせた
```(runtime.txt)
python-3.5.4
```

### herokuアプリ（インスタンス）作成
```
$ heroku create --buildpack https://github.com/kennethreitz/conda-buildpack.git
```

### herokuにデプロイ
```
$ git push heroku master
```

* パッケージがない、というエラーが何回か発生したので、都度requirementsから削除
  * 削除したパッケージ
    * libprotobuf=3.2.0=vc14_0
    * mkl=2017.0.3=0
    * setuptools=27.2.0=py35_1
    * six=1.10.0=py35_1
    * vs2015_runtime=14.0.25420=0
    * zlib=1.2.11=vc14_0

* それでも `enum34` と `tensorflow 1.2.1 py35_0` の依存パッケージ衝突が発生
  * `enum34` はbuildpackで入れられているような。。。
    * となるとconda-requiremetns.txtは使えないのでrequirements.txtを使ってみる。

```
$ pip freeze > requirements.txt
$ git commit -am "add requirements.txt"
$ heroku build packs:remove https://github.com/kennethreitz/conda-buildpack.git
$ git push heroku master
・・・
remote:        /app/tmp/buildpacks/779a8bbfbbe7e1b715476c0b23fc63a2103b3e4131eda
558669aba8fb5e6e05682419376144189b29beb5dee6d7626b4d3385edb0954bffea6c67d8cf622f
d51/bin/steps/pip-install: line 7: /app/.heroku/python/bin/pip: No such file or
directory
```

* pipのインストールでコケる
  * runtime.txtのpythonバージョンを `3.5.2` にする
```(runtime.txt)
python-3.5.4
```

* 再度push
```
$ git commit -am "change python version"
$ git push heroku master
```

### 動作確認
```
$ heroku open
```
ブラウザで表示されればOK

---

# docmo会話API
docomoが提供している[雑談対話API](https://dev.smt.docomo.ne.jp/?p=docs.api.page&api_name=dialogue&p_name=api_1)を使ってみる

* API利用アカウント作成
* API利用申請
* トークン取得

---
# herokuにRdis追加
* 手順省略
  * [Heroku Redis](https://devcenter.heroku.com/articles/heroku-redis)

# heroku環境変数
各種環境変数を設定する
```
$ heroku config:set {変数名}={パラメータ}
```
* CHANNEL_ACCESS_TOKEN = LINEで発行されたアクセストークン
* DOCOMO_API_KEY = DOCOMOの会話APIで使用するアクセストークン
* DOCOMO_API_CHARACTER = DOCOMO会話APIのキャラクタ[20: 関西弁キャラ, 30: 赤ちゃんキャラ、指定なし: デフォルトキャラ]

---

# tensorflowで会話学習

### 必要パッケージインストール
* mecab
    * https://sourceforge.net/projects/mecab/files/mecab-win32/0.98/mecab-0.98.exe/download
        * 辞書の文字コードは「UTF-8」を選択
        * PATHを通す
* pythonライブラリ
    * nkf
      * `pip install nkf`
        * うまく動かなかった・・・。未解決
    * mecab-python3
      * [ここ](https://pypi.python.org/pypi/mecab-python3/0.7)からDLしてビルド
        * いろいろあるので[サイト参考](http://own-search-and-study.xyz/2017/06/28/mecab%E3%82%92%E3%82%A4%E3%83%B3%E3%82%B9%E3%83%88%E3%83%BC%E3%83%AB%E3%81%97python%E3%81%8B%E3%82%89%E4%BD%BF%E3%81%86%E6%96%B9%E6%B3%95%E3%81%BE%E3%81%A8%E3%82%81/)
          * 参考サイトと状況が異なり未解決。構築が面倒なので形態素解析はスキップ


### 学習用の会話データを作成
* [日本語自然会話書き起こしコーパス（旧名大会話コーパス）](https://nknet.ninjal.ac.jp/nuc/templates/nuc.html)を使用する
  * 下記コマンドで、会話データDLから教師データ作成まで実行する
```
$ python mksequence.py
```

**TODO: 形態素解析**

# 続く

[TensorFlowのseq2seqで対話を学習させる](http://tech.mof-mof.co.jp/blog/seq2seq.html)
