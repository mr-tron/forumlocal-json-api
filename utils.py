#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import time
import logging as log
log.basicConfig(format='%(filename)s[LINE:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s',
                level=log.INFO,
                filename='../forum_application.log')

def timer(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
        print("Время выполнения функции %s: %f" % (f, (time.time()-t)))
        return res

    return tmp