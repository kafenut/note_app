#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app,db
from flask_migrate import Migrate,MigrateCommand
from flask_script import Manager,Server

manager=Manager(app)
migrate=Migrate(app,db)

manager.add_command('runserver',Server())
manager.add_command('db',MigrateCommand)

if __name__=='__main__':
    manager.run()
