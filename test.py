#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import unittest
import os

from app.models import User,Comment,Blog,Sub_Comment
from app import app,db

class TestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING']=True
        app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///'+os.path.join(os.getcwd(),'test.db')
        self.app=app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_blog(self):
        alice=User(nickname='alice')
        bob=User(nickname='bob')
        b1=Blog(author=alice)
        b2=Blog(author=bob)
        b3=Blog(author=bob)
        db.session.add_all([alice,bob,b1,b2,b3])
        db.session.commit()
        assert b1.author==alice
        assert b2.author==bob
        for blog in bob.blogs: #user.blogs.all() is a list, user.blogs is a query object ,so does comments.cmmts
            print(blog,blog.id)
        
        c1=Comment(author=bob,to_blog=b1)
        db.session.add(c1)  #need to commit first, so that the database can autocomplete c1.id
        db.session.commit()
        c2=Sub_Comment(author=alice,to_blog=b1,under_cmmt=c1)
        c3=Sub_Comment(author=alice,to_blog=b2,under_cmmt=c1)
        db.session.add_all([c2,c3])
        db.session.commit()
        assert c1.author==bob
        assert c2.author==alice
        assert list(b1.cmmts)==[c1] 
        print(list(c1.cmmts))
        assert list(c1.cmmts)==[c2,c3]

    def test_follow(self):
        bob=User(nickname='bob')
        alice=User(nickname='alice')
        db.session.add_all([bob,alice])
        db.session.commit()

        assert bob.is_following(alice)==False
        assert alice.followers.count()==0
        assert bob.followeds.count()==0

        event=bob.follow(alice)
        db.session.add(event)
        db.session.commit()

        assert bob.is_following(alice)==True
        assert alice.followers.count()==1
        assert bob.followeds.count()==1
        assert alice.followers.first()==bob
        assert bob.followeds.first()==alice

        event=bob.unfollow(alice)
        db.session.add(event)
        db.session.commit()

        assert bob.is_following(alice)==False
        assert alice.followers.count()==0
        assert bob.followeds.count()==0

    def test_followed_posts(self):
        alice=User(nickname='alice')
        bob=User(nickname='bob')
        db.session.add_all([alice,bob])
        db.session.commit()
        
        event=bob.follow(alice)
        db.session.add(event)
        db.session.commit()
        assert bob.followed_blogs.count()==0

        b1=Blog(author=alice)
        b2=Blog(author=alice)
        db.session.add_all([b1,b2])
        db.session.commit()
        assert bob.followed_blogs.all()==[b1,b2]




if __name__=='__main__':
    unittest.main()

