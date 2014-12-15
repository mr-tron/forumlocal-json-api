# -*- coding: utf-8 -*-


import uuid
from sqlalchemy import Column, Integer, String, MetaData, DateTime, TIMESTAMP, SmallInteger, ForeignKey, create_engine, \
    Boolean, func, BigInteger, UnicodeText, LargeBinary
from sqlalchemy.dialects.mysql import MEDIUMTEXT
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.ext.declarative import declarative_base

engine = create_engine('mysql+mysqlconnector://forumlocal@localhost/forumlocal?charset=utf8')
Session = sessionmaker(bind=engine)
metadata = MetaData()
Base = declarative_base(metadata=metadata)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'mysql_charset': 'utf8'}
    id = Column(Integer)
    nick = Column(String(30), index=True, primary_key=True)
    name = Column(String(250))
    title = Column(String(50))
    email = Column(String(100))
    post_count = Column(Integer)
    rating = Column(Integer)
    homepage = Column(String(150))
    occupation = Column(String(100))
    hobbies = Column(String(200))
    location = Column(String(250))
    bio = Column(String(250))
    icq = Column(String(250))
    sex = Column(String(250))
    register_date = Column(DateTime)
    first_message_date = Column(DateTime)
    last_online_date = Column(DateTime)
    last_message_date = Column(DateTime)
    signature = Column(String(200))
    avatar = Column(String(20))
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    def __init__(self, nick):
        self.nick = nick

    def __repr__(self):
        return "{'user': %s, 'id': %s}" % (self.nick, self.id)


class Post(Base):
    __tablename__ = 'posts'
    __table_args__ = {'mysql_charset': 'utf8'}
    post_id = Column(BigInteger, primary_key=True)  # уникальный айди поста
    main = Column(BigInteger)  # айди первого поста в данном треде. идентифицурует тред
    local_main = Column(BigInteger)  # в ветке обсуждаемого треда айди первого поста внутри обсуждения.
                                     # если этот айди у поста не ноль. то он 100% находится внутри обсуждения
    parent = Column(BigInteger)  # родительский пост в дереве ответов. у первого поста - 0
    user = Column(String(30), ForeignKey('users.nick'))
    date = Column(DateTime)
    edit_date = Column(DateTime)
    edit_by = Column(String(30), ForeignKey('users.nick'))
    board = Column(String(250))
    layer = Column(String(1))
    alt = Column(Boolean)
    archive = Column(Boolean)
    subject = Column(String(250))
    body = Column(MEDIUMTEXT)
    rating = Column(SmallInteger)
    update_time = Column(TIMESTAMP, server_default=func.now(), onupdate=func.current_timestamp())

    def __init__(self, post_id, parent, main, local_main, subject, date, user, board, body, archive=False):
        self.post_id = post_id
        self.parent = parent
        self.main = main
        self.local_main = local_main
        self.subject = subject
        self.date = date
        self.user = user
        self.board = board
        self.body = body
        self.archive = archive


metadata.create_all(engine)