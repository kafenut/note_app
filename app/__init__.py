#!/usr/bin/env python3
# -*- coding: utf-8 -*-

#bind orm to app
from flask_sqlalchemy import SQLAlchemy
from flask import Flask
app=Flask(__name__)
app.config.from_object('config')
db=SQLAlchemy(app)

#bing login_manager to app
from flask_login import LoginManager
login_manager=LoginManager()
login_manager.init_app(app)

#bind global env
from .momentjs import momentjs
app.jinja_env.globals['momentjs']=momentjs

#import other components
from app import views,models
