#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from base import *
import parser
from utils import *

# ############# внутренние методы


def update_all_users_info():
    s = Session()
    i = 0
    step = 25
    while True:
        user_list = s.query(User).slice(i, i+step).all()
        if not user_list:
            break
        for user in user_list:
            update_user_info(user)
        print(i)
        i += step
        s.commit()


def update_user_info(user):
    log.info('Get and parse user: "%s"' % user)
    if type(user) == User:
        try:
            user_info = parser.get_user_info_by_name(user.nick)
        except:
            log.error('Failed get and parse user: "%s"' % user)
            return None
        log.debug('Got user info: %s' % str(user_info))
        for key in user_info.keys():
            if user_info[key]:
                if user.__getattribute__(key) != user_info[key]:
                    user.__setattr__(key, user_info[key])
    elif type(user) == str:
        s = Session()
        user_object = s.query(User).get(user)
        if user_object:
            update_user_info(user_object)
            s.commit()
            s.close()
        else:
            try:
                user_info = parser.get_user_info_by_name(user)
                log.debug('Got user info: %s' % str(user_info))
            except:
                log.error('Failed get and parse user: "%s"' % user)
                raise Exception
            user_object = User(user_info['nick'])
            update_user_info(user_object)


def download_full_user_list():
    s = Session()
    i = 1
    while True:
        t = parser.user_list_by_page(i)
        for i in t:
            if not s.query(User).get(i):
                log.info('Add new user to base: %s' % i)
                s.add(User(i))
        s.commit()
        if len(t) != 25:
            print(i)
            break


def update_user_list():
    log.info('Started user list update.')
    s = Session()
    t = parser.user_list_by_page(1)
    for i in t:
        if not s.query(User).get(i):
            log.info('Add new user to base: %s' % i)
            s.add(User(i))
    s.commit()


def check_user_exists(nick):
    s = Session()
    t = s.query(User).get(nick)
    s.close()
    if t:
        log.debug('User exist: %s' % nick)
        return True
    else:
        log.debug('User don`t exist: %s' % nick)
        return False


def add_posts_to_base(posts):
    s = Session()
    for post in posts:
        try:
            s.add(Post(post_id=post['post_id'],
                       parent=post['parent'],
                       main=post['main'],
                       local_main=post['local_main'],
                       subject=post['subject'],
                       date=post['date'],
                       user=post['user'],
                       board=post['board'],
                       body=post['body'],
                       archive=post['archive']))
            s.commit()
        except Exception:
            s.rollback()
    s.close()


# ###### Методы для отдачи в апи
def get_user_info(nick):
    s = Session()
    u = s.query(User).get(nick)
    s.close()
    if u:
        answer = {i: u.__dict__[i] for i in u.__dict__ if i != '_sa_instance_state'}
        return answer
    return {'Error': 'User does not exist!'}


def get_threads_list(board, page):
    # в перспективе брать из базы
    return parser.get_threads_list_by_board(board, page)


def get_thread(main, page):
    if page == 'all':
        posts = parser.thread_posts_by_page(main, page)
    else:
        posts = parser.thread_posts_by_page(main, int(page) * 20)
    if posts:
        add_posts_to_base(posts)
    return posts


def get_post(post_id):
    s = Session()
    p = s.query(Post).get(post_id)
    if not p:
        posts = parser.thread_posts_by_id(post_id)
        if posts:
            add_posts_to_base(posts)
        p = s.query(Post).get(post_id)
    if p:
        return {i: p.__dict__[i] for i in p.__dict__ if i != '_sa_instance_state'}
    else:
        return {'Error': 'Post does not exist!'}


def post_reply(post_id, body, cookies, subject=None, layer=0, icon='book.gif'):
    log.info('User %s answer on post %i' % (cookies['w3t_w3t_myid'], post_id))
    return parser.post_reply(post_id, body, cookies, subject, layer, icon)


def vote_post(post_id, rating, cookies):
    log.info('User %s vote for post %i with rating %i' % (cookies['w3t_w3t_myid'], post_id, rating))
    return parser.vote_post(post_id, rating, cookies)