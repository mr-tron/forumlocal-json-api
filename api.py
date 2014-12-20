#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from bottle import route, run, request, response, default_app
import methods
from utils import *
from datetime import datetime


def normalize(answer):
    if isinstance(answer, dict):
        for i in answer:
            if type(answer[i]) == datetime:
                answer[i] = int(answer[i].timestamp())
    elif isinstance(answer, list):
        for i in answer:
            normalize(i)
    response.content_type = 'application/json'
    return str(answer)


@route('/user/nick/<nick>')
def get_user(nick):
    print(nick)
    try:
        user = methods.get_user_info(nick)
        return normalize(user)
    except Exception as err:
        return {'Error': err}


@route('/post/<post_id:int>')
def get_post(post_id):
    post = methods.get_post(post_id)
    return normalize(post)


@route('/post/<post_id:int>/reply', method='POST')
def reply_post(post_id):
    body = request.forms.get('body')
    cookies = {x: request.cookies.dict[x][0] for x in request.cookies.dict}
    t = methods.post_reply(post_id, body, cookies)
    return normalize({'Status': t})


@route('/post/<post_id:int>/vote/<rating:int>', method='POST')
def rating_post(post_id, rating):
    cookies = {x: request.cookies.dict[x][0] for x in request.cookies.dict}
    t = methods.vote_post(post_id, rating, cookies)
    return normalize({'Rating': t})


@route('/threadslist/<board>/<page:int>')
def get_threads(board, page=0):
    threads = methods.get_threads_list(board, page)
    return normalize(threads)



@route('/thread/<main:int>/<page:re:(all|[0-9]+)>')
def get_thread_page(main, page):
    posts = methods.get_thread(main, page)
    return normalize(posts)

if __name__ == '__main__':
    run(host='localhost', port=10001, debug=True)


application = default_app()