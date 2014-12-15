#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
from urllib import parse  # нужен для кодирования русских ников. выпилить надо
import requests
from bs4 import BeautifulSoup
import time
from datetime import datetime
import re
from utils import *
from checksum import checksum


def timer(f):
    def tmp(*args, **kwargs):
        t = time.time()
        res = f(*args, **kwargs)
        print("Время выполнения функции %s: %f" % (f, (time.time()-t)))
        return res

    return tmp

highpoints = re.compile('[\U00010000-\U0010ffff]')

forum_url = "http://forumlocal.ru/"
user_page = "showprofile.php?Cat=&User=%s&page=1&what=showmembers"
user_list_page = "showmembers.php?Cat=&sb=14&page=%i"
post_request_page = "showflat.php?Cat=&Board=soft&Number=%i&showlite="
threads_list_page = "postlist.php?Cat=&Board=%s&page=%i&showlite=l"
reply_form_page = "newreply.php?Cat=&Number=%i&fullview=&src=pt&what=showflat&o=&vc=1&showlite="
reply_post_url = 'addpost.php?showlite='
rate_post_url = 'doratepost.php?number=%i&src=&rating=%i&check=%s'


def normalize(data):
    if isinstance(data, dict):
        for i in data.keys():
            if isinstance(data[i], str):
                data[i] = highpoints.sub(u'', data[i])
    return data


def get_user_info_by_name(nick):
    parse_page = requests.get(forum_url + user_page % parse.quote(nick.encode("cp1251")))
    parse_page.connection.close()
    parsed_page = BeautifulSoup(parse_page.content.decode('cp1251'))

    try:
        parameters = parsed_page.find("table", {"class": "lighttable"}).find_all("tr", recursive=False)
    except Exception as err:
        print('Parsing failed: %s' % err)
        return {}

    user = {"nick": nick}

    try:
        user["email"] = parameters[0].find("a").string.replace("&nbsp;", "")
    except:
        user["email"] = ""
    user["avatar"] = parameters[0].find("img").get("src")
    user["name"] = parameters[1].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    user["title"] = parameters[2].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    user["post_count"] = parameters[3].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    user["rating"] = parameters[4].find("b").string.replace("&nbsp;", "").strip()
    try:
        user["homepage"] = parameters[5].find("a").string.replace("&nbsp;", "")
    except:
        user["homepage"] = ""
    user["occupation"] = parameters[6].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    user["hobbies"] = parameters[7].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    user["location"] = parameters[8].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    user["icq"] = parameters[10].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    user["sex"] = parameters[11].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    reg_date = parameters[12].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    user["register_date"] = datetime.fromtimestamp(time.mktime(time.strptime(reg_date, "%d.%m.%Y %H:%M")))
    online_date = parameters[13].find("td", {"class": None}).string.replace("&nbsp;", "").strip()
    if online_date:
        user["last_online_date"] = datetime.fromtimestamp(time.mktime(time.strptime(online_date, "%d.%m.%Y %H:%M")))
    else:
        user["last_online_date"] = []

    return normalize(user)


def get_threads_list_by_board(board, page_number):
    parse_page = requests.get(forum_url + threads_list_page % (board, page_number))
    parse_page.connection.close()
    parsed_page = BeautifulSoup(parse_page.content.decode('cp1251'))
    threads_list = parsed_page.body.table.find_all('table', {'width': '100%'})

    threads = []
    for i in threads_list:
        if not i.has_attr('class'):
            t = i.find_all('td')
            threads += [{'id':  re.search('Number=([0-9]*)', t[0].a['href']).group(1),
                         'subject': t[0].text.strip(),
                         'user': t[1].text.strip()}]
    return threads


def user_list_by_page(page_number):
    parse_page = requests.get(forum_url + user_list_page % page_number)
    parse_page.connection.close()
    parsed_page = BeautifulSoup(parse_page.content.decode('cp1251'))
    user_list = []
    try:
        user_table = parsed_page.findAll("table", {"class": "tableborders"})[2].findAll("tr")
    except Exception as err:
        print('Parsing failed: %s' % err)
        return user_list
    for i in user_table:
        if i["class"][0] in ("lighttable", "darktable"):
            user_list += [i.td.a.string.strip()]
    return user_list


@timer
def thread_posts_by_id(post_id):
    posts = get_all_posts_from_page(post_request_page % post_id)
    return posts


def get_all_posts_from_page(request_page):
    parse_page = requests.get(forum_url + request_page)
    parse_page.connection.close()
    parsed_page = BeautifulSoup(parse_page.content.decode('cp1251'))
    p = parsed_page.body.find_all('table', {'width': '100%', 'border': '0', 'cellpadding': '3'})[1].\
        find_all('tr', recursive=False)
    try:
        u = parsed_page.find_all('td', {'width': '65%', 'valign': 'top', 'align': 'left'})[0].a['href'].split('&')
        board = u[1].lstrip('Board=')
        main = u[2].lstrip('Number=')
        if u[4] == 'src=arc':
            archive = True
        else:
            archive = False

    except Exception as err:
        pass
    posts = []
    i = 0
    while i < len(p):
        try:
            post = {'post_id': p[i].td.a['name'].lstrip('Post'),
                    'user': p[i].td.table.tr.td.a.text,
                    'subject': p[i].find('td', {'class': 'subjecttable'}).table.tr.td.b.text.strip(),
                    'board': board,
                    'main': main,
                    'archive': archive,
                    'local_main': 0
                    }

            post['body'] = ''.join([str(x) for x in p[i+1].tr.font if str(x).find('<font class="small"><a href="/')])

            try:
                post['parent'] = p[i].find('td', {'class': 'subjecttable'}).table.tr.td.font.a['href'].split('&')[2].lstrip('Number=')
                post['date'] = datetime.fromtimestamp(time.mktime(time.strptime(p[i].find('td', {'class': 'subjecttable'}).table.tr.td.find_all('font')[1].text.strip(), "%d.%m.%Y %H:%M")))
            except:
                post['parent'] = 0
                post['date'] = datetime.fromtimestamp(time.mktime(time.strptime(p[i].find('td', {'class': 'subjecttable'}).table.tr.td.font.text.strip(), "%d.%m.%Y %H:%M")))
        except:
            post = {}
        i += 2
        if post:
            posts += [normalize(post)]
    return posts


def post_reply(post_id, body, cookies, subject, layer, icon):
    post_form = requests.get(forum_url + reply_form_page % post_id, cookies=cookies)
    post_form.connection.close()
    parsed_form = BeautifulSoup(post_form.content)
    post_data = {}
    for i in ('postername', 'Cat', 'Reged', 'page', 'Main', 'Parent', 'what', 'sb', 'o', 'oldnumber', 'fpart', 'vc',
              'replyto', 'disc', 'src', 'convert', 'postdata_protection_key', 'textcont'):
        post_data[i] = parsed_form.find('input', {'name': i})['value']
    if subject:
        post_data['Subject'] = subject[:70]
    else:
        post_data['Subject'] = parsed_form.find('input', {'name': 'Subject'})['value']
    post_data['post_layer'] = layer
    post_data['Icon'] = icon
    post_data['Body'] = body
    for i in post_data:
        if isinstance(post_data[i], str):
            post_data[i] = post_data[i].encode('cp1251')
    post_result = requests.post(forum_url + reply_post_url, post_data, cookies=cookies)
    post_result.connection.close()
    return BeautifulSoup(post_result.content).find_all('tr', {'class': 'lighttable'})[0].td.text.strip().splitlines()[0]


def vote_post(post_id, rating, cookies):
    c = checksum(str(post_id) + cookies['w3t_w3t_myid'])
    rating_request = requests.get(forum_url + rate_post_url % (post_id, rating, c), cookies=cookies)
    rating_request.connection.close()
    return int(rating_request.content)
