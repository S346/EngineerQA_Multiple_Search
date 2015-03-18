# -*- coding: utf-8 -*-

import json
import urllib2
import urllib
import gzip
import StringIO
from bottle import route, run, get, request
from bottle import TEMPLATE_PATH, jinja2_template as template

TEMPLATE_PATH.append("./views")


# Qiita検索
def qiita_search(word):
    qiita_api = 'http://qiita.com/api/v2/items?page=1&per_page=10&&query=' + \
        word
    titles = []
    urls = []
    try:
        r = urllib2.urlopen(qiita_api)
        qiita_jsons = json.loads(r.read())
        for qiita_json in qiita_jsons:
            titles.append(qiita_json['title'])
            urls.append(qiita_json['url'])
    finally:
        r.close()
    return urls, titles


# Stack Over Flow検索用関数
def sof_search(word):
    sof_api = 'https://api.stackexchange.com/2.2/search/advanced?pagesize=10&order=desc&sort=activity&title=' + \
        word + '&site=ja.stackoverflow'
    titles = []
    urls = []
    try:
        r = urllib2.urlopen(sof_api)
        sf = StringIO.StringIO(r.read())
        dec = gzip.GzipFile(fileobj=sf)
        sof_jsons = json.loads(dec.read())
        for sof_json in sof_jsons['items']:
            titles.append(sof_json['title'])
            urls.append(sof_json['link'])
    finally:
        r.close()
    return urls, titles


@route('/')
def Top(name='it'):
    return template('hello.j2', name=name)


@get('/search')
def search():
    # formの値を取得→utf-8に変換→クエリ用の値に変換
    word = urllib.quote_plus(request.query.search_word.encode('utf-8'))
    # urls, titles = qiita_search(word)
    urls, titles = sof_search(word)
    word_utf8 = urllib.unquote_plus(word).decode('utf-8')
    return template('result.j2', a=word_utf8, titles=titles, urls=urls)

run(host='localhost', port=8080, debug=True, reloader=True)
