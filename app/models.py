#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import db,app
from config import NOTE_UPLOAD_FOLDER
from sqlalchemy import or_


Follow=db.Table('follow',
     db.Column('follower_id',db.Integer,db.ForeignKey('user.id')),
     db.Column('followed_id',db.Integer,db.ForeignKey('user.id'))
    )

class Blog(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    upload_time=db.Column(db.DateTime)
    last_cmmt_time=db.Column(db.DateTime)
    like_num=db.Column(db.Integer,default=0)
    title=db.Column(db.String(50))
    body=db.Column(db.String(500))

    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    cmmts=db.relationship('Comment',backref='to_blog',lazy='dynamic',foreign_keys='Comment.to_blog_id')   
    sub_cmmts=db.relationship('Sub_Comment',backref='to_blog',lazy='dynamic',foreign_keys='Sub_Comment.to_blog_id')
    #author=db.relationship('User',backref='blogs')

    def __repr__(self):
        return 'Class Blog: author is '+self.author.nickname

class User(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    nickname=db.Column(db.String(60),index=True,unique=True)
    role=db.Column(db.String(20))
    email=db.Column(db.String(144),index=True,unique=True)
    tel_num=db.Column(db.String(20),index=True,unique=True)
    passwd=db.Column(db.String(128))
    about_me=db.Column(db.String(512))
    last_seen=db.Column(db.DateTime)
    avatar=db.Column(db.String(500))
    folder=db.Column(db.String(120))

    blogs=db.relationship('Blog',backref='author',lazy='dynamic',foreign_keys='Blog.author_id')
    notes=db.relationship('Note',backref='author',lazy='dynamic',foreign_keys='Note.author_id')   #something unexpected will happen if we use dynamic load
    cmmts=db.relationship('Comment',backref='author',lazy='dynamic',foreign_keys='Comment.author_id')   
    sub_cmmts=db.relationship('Sub_Comment',backref='author',lazy='dynamic',foreign_keys='Sub_Comment.author_id')
    note_cmmts=db.relationship('Note_Comment',backref='author',lazy='dynamic',foreign_keys='Note_Comment.author_id')
    issues=db.relationship('Issue',backref='author',lazy='dynamic',foreign_keys='Issue.author_id')
    
    followeds=db.relationship('User',
                             secondary=Follow,
                             primaryjoin=(Follow.c.follower_id==id),
                             secondaryjoin=(Follow.c.followed_id==id),
                             backref=db.backref('followers',lazy='dynamic'),
                             lazy='dynamic'
                             )
    #followers: join=(Follow.c.followed_id=id)

    def is_following(self,user):
        return self.followeds.filter(Follow.c.followed_id == user.id).count()>0

    def follow(self,user):
        if not self.is_following(user):
            self.followeds.append(user)
            return self
        return None

    def unfollow(self,user):
        if self.is_following(user):
            self.followeds.remove(user)
            return self
        return None

    def get_avatar(self,size=50):
        if self.avatar:
            return self.avatar[5:]
        return '/static/img/avatar/anonymous.png'

    @property
    def folders(self):
        return self.folder.split('.')

    @property
    def followed_blogs(self):
        return Blog.query.join(Follow,(Follow.c.followed_id==Blog.author_id)).filter(Follow.c.follower_id==self.id).order_by(Blog.upload_time.desc())

    @property
    def followed_notes(self):
        return Note.query.join(Follow,(Follow.c.followed_id==Note.author_id)).filter(or_(Follow.c.follower_id==self.id,Note.author_id==self.id,Note.author_id==1))
    
    def __repr__(self):
        return 'Class User: '+self.nickname

    #flask_login
    @property
    def is_authenticated(self):
        return True

    @property
    def is_active(self):
        return True

    @property
    def is_anonymous(self):
        return True

    def get_id(self):
        return self.id

class Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    upload_time=db.Column(db.DateTime)
    like_num=db.Column(db.Integer,default=0)
    body=db.Column(db.String(500))
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    #author=db.relationship('User',backref='cmmts')
    to_blog_id=db.Column(db.Integer,db.ForeignKey('blog.id'))
    sub_cmmts=db.relationship('Sub_Comment',backref='under_cmmt',lazy='dynamic')

    def __repr__(self):
        return 'Class Comment: author is '+self.author.nickname

class Sub_Comment(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    upload_time=db.Column(db.DateTime)
    like_num=db.Column(db.Integer,default=0)
    body=db.Column(db.String(500))

    to_cmmt_id=db.Column(db.Integer)
    #to_cmmt=db.relationship('Sub_Comment',backref='sub_cmmts')
    to_blog_id=db.Column(db.Integer,db.ForeignKey('blog.id'))
    #to_blog=db.relationship('Blog',backref='sub_cmmts')
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    #author=db.relationship('User',backref='sub_cmmts')
    under_cmmt_id=db.Column(db.Integer,db.ForeignKey('comment.id'))
    #under_cmmt=db.relationship('Comment',backref='cmmts')

    @property
    def to_cmmt(self):
        if self.to_cmmt_id is None:
            return None
        return Sub_Comment.query.filter_by(id=self.to_cmmt_id).first()
    
    def __repr__(self):
        return 'Class Sub_Comment : author is ' +self.author.nickname

class Note(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    upload_time=db.Column(db.DateTime)
    title=db.Column(db.String(50))
    path=db.Column(db.String(100))
    logic_folder=db.Column(db.String(100))   #the logical folder user specified
    view_num=db.Column(db.Integer,default=0)
    like_num=db.Column(db.Integer,default=0)
    

    #author=db.relationship('User',backref='notes')
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))

    cmmts=db.relationship('Note_Comment',backref='to_note',lazy='dynamic',foreign_keys='Note_Comment.to_note_id')
    
    @property
    def summary(self,num=20):
        with open(NOTE_UPLOAD_FOLDER+self.path,'r',encoding='utf-8') as f:   #window encoding default is gbk
            s=f.read(20)
        return s+' ...'

class Note_Comment(db.Model):
    __tablename__='note_comment' #flask_migrate will foolishly set table_name to note__comment

    id=db.Column(db.Integer,primary_key=True)
    upload_time=db.Column(db.DateTime)
    body=db.Column(db.String(200))
    floor=db.Column(db.Integer,unique=True)
    level=db.Column(db.Integer,default=2)
    like_num=db.Column(db.Integer,default=0)

    #author=db.relationship('User',backref='note_cmmts')
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))
    #to_note=db.relationship('User',backref='cmmts')
    to_note_id=db.Column(db.Integer,db.ForeignKey('note.id'))
    to_cmmt_id=db.Column(db.Integer,db.ForeignKey('note_comment.id'))
    under_cmmt_id=db.Column(db.Integer,db.ForeignKey('note_comment.id'))
    #to_user_id=db.Column(db.Integer,db.ForeignKey('user.id'))

    @property         #something wrong about sqlalchemy, so I achieve it on my own 
    def sub_cmmts(self):
        return self.query.filter_by(to_cmmt_id=self.id)

    @property
    def under_cmmts(self):
        return self.query.filter_by(under_cmmt_id=self.id)

    @property
    def to_cmmt(self):
        return self.query.filter_by(id=self.to_cmmt_id).first()

    @property
    def under_cmmt(self):
        return self.query.filter_by(id=self.under_cmmt_id).first()
      
class Issue(db.Model):
    id=db.Column(db.Integer,primary_key=True)
    upload_time=db.Column(db.DateTime)
    title=db.Column(db.String(50))
    body=db.Column(db.String(200))
    fixed=db.Column(db.Integer,default=0)
    
    #author=db.relationship('User',backref='issues')
    author_id=db.Column(db.Integer,db.ForeignKey('user.id'))

    
    

    




