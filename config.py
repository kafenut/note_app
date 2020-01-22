#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#app config
DEBUG=True
SQLALCHEMY_DATABASE_URI='mysql+pymysql://test_user_1:test_user_1@localhost:3306/awesome_web_app?charset=utf8'
SQLALCHEMY_ECHO=False
SQLALCHEMY_TRACK_MODIFICATIONS=True

import os
IMG_UPLOAD_FOLDER='./app/static/img/avatar/'
NOTE_UPLOAD_FOLDER='./app/templates/note/'
ALLOWED_EXTENDSIONS=set(['jpg','png','jpeg'])
MAX_CONTENT_LENGTH=16*1024*1024

#login_config
SECRET_KEY='youwillneverguess'  #also mysql root password
ADMIN_ACCOUNT='kafenut@xg.com'
ADMIN_PASSWD='zxyishandsome'
ADMIN_ID='1'

#page
BLOGS_PER_PAGE=5
ISSUE_PER_PAGE=5
NOTE_PER_PAGE=10