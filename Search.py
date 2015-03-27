# -*- coding: utf-8 -*-

import json
import urllib2
import urllib
import gzip
import StringIO
from bs4 import BeautifulSoup
from bottle import route, run, get, request
from bottle import TEMPLATE_PATH, jinja2_template as template

TEMPLATE_PATH.append("./views")


# スクレイピング用（検索用URL, 質問表示用URL, 検索タグ, 検索値）
def scraping(s_url, q_url, tag, value):
    titles = []
    urls = []
    r = urllib2.urlopen(s_url)
    soup = BeautifulSoup(r.read())
    s = soup.find_all(tag, {"class": value})
    for x in s:
        titles.append(x.a['title'])
        urls.append(q_url + x.a['href'])
    r.close()
    return urls, titles


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


# Stack Over Flow検索
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


# teratail検索
def tera_search(word):
    s_url = 'https://teratail.com/questions/search?q=' + \
        word + '&search_type=and'
    q_url = 'https://teratail.com'
    return scraping(s_url, q_url, 'h2', 'ttlItem')


# QA@IT検索用
def qait_search(word):
    s_url = 'http://qa.atmarkit.co.jp/q/search?utf8=%E2%9C%93&q=' + \
        word + '&commit=%E6%A4%9C%E7%B4%A2'
    q_url = 'http://qa.atmarkit.co.jp'
    return scraping(s_url, q_url, 'article', 'question')


@route('/')
def Top():
    return template('hello.j2')


@get('/search')
def search():
    # formの値を取得→utf-8に変換→クエリ用の値に変換
    word = urllib.quote_plus(request.query.search_word.encode('utf-8'))
    ch = request.params.getlist('need')
    urls = []
    titles = []
    if "sof" in ch:
        url, title = sof_search(word)
        urls.append(url)
        titles.append(title)
    if "qiita" in ch:
        url, title = qiita_search(word)
        urls.append(url)
        titles.append(title)
    if "tera" in ch:
        url, title = tera_search(word)
        urls.append(url)
        titles.append(title)
    if "qait" in ch:
        url, title = qait_search(word)
        urls.append(url)
        titles.append(title)
    word_utf8 = urllib.unquote_plus(word).decode('utf-8')
    return template('result.j2', search_word=word_utf8,
                    titles=titles, urls=urls, ch=ch)

run(host='localhost', port=8080, debug=True, reloader=True)
