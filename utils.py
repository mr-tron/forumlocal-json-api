#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import time
import configparser
import logging as log

config = configparser.ConfigParser()
config.read('config.cfg')

log.basicConfig(format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                level=log._nameToLevel[config['log']['log_level']],
                filename='application.log')


def timer(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
        print("Время выполнения функции %s: %f" % (f, (time.time()-t)))
        return res

    return tmp