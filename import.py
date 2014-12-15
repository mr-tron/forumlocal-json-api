#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from base import *
import datetime
import methods
from urllib import parse
from utils import *

def import_backups_posts(filename):
    parsed_file = open(filename, 'r')
    s = Session()
    i = 0
    while True:
        line = parsed_file.readline()
        if i < 2210260:
            i += 1
            continue
        if line == '':
            s.commit()
            break
        post = {x.split('=')[0]: x.split('=')[1] for x in line.split()}
        if not methods.check_user_exists(parse.unquote(post['Username'], encoding='cp1251')):
            s.add(User(parse.unquote(post['Username'], encoding='cp1251')))
            s.commit()
        s.add(Post(post_id=post['Number'],
                   parent=post['Parent'],
                   main=post['Main'],
                   local_main=post['Local_Main'],
                   subject=parse.unquote(post['Subject'], encoding='cp1251'),
                   date=datetime.datetime.fromtimestamp(int(post['UnixTime'])),
                   user=parse.unquote(post['Username'], encoding='cp1251'),
                   board=post['Board'],
                   body=parse.unquote(post['Body'], encoding='cp1251'),
                   archive=False
                   )
              )
        #print(i)
        #i += 1
        print(i)
        try:
            s.commit()
            print('Commited')
        except Exception as err:
            log.error('Fail import post %s ' % i)
            s.rollback()
        i += 1

#import_backups_posts('posts')
import_backups_posts('aposts')