#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from app import app,db,login_manager
from flask import render_template,flash,redirect,session,url_for,g,request
from flask_login import login_required,login_user,logout_user,current_user
from datetime import datetime
from app.models import User,Blog,Comment,Sub_Comment,Note,Issue,Note_Comment
from config import BLOGS_PER_PAGE,ISSUE_PER_PAGE,NOTE_PER_PAGE,ADMIN_ID
from app.function import save_img_base64,save_note,del_note
from sqlalchemy import and_,inspect

import json

ADMIN=User.query.filter_by(id=ADMIN_ID).first()
KAFENUT_NOTES=Note.query.filter_by(author_id=ADMIN.id)

@app.route('/')
@app.route('/index')
def index():
    global KAFENUT_NOTES
    if not g.user.is_authenticated: 
        notes=Note.query.order_by(Note.upload_time.desc()).limit(5)
    else:
        notes=g.user.followed_notes.order_by(Note.upload_time.desc()).limit(5)    
    return render_template('index.html',notes=notes,kafenut_notes=KAFENUT_NOTES)

#user
@app.route('/register',methods=['POST','GET'])
def register():   
    global KAFENUT_NOTES
    if request.method=='GET':       
        return render_template('register.html',kafenut_notes=KAFENUT_NOTES)
    Get=request.form.get
    if User.query.filter_by(email=Get('email')).first():
        flash('The email has been registered!')
        return redirect(url_for('register'))
    elif User.query.filter_by(nickname=Get('nickname')).first():
        flash('This nickname has been registered!')
        return redirect(url_for('register'))
    else:
        user=User(nickname=Get('nickname'),email=Get('email'),passwd=Get('passwd'),about_me=Get('about_me'),role='normal user')
        db.session.add(user)
        db.session.commit()
        flash('Register successfully!')
        login_user(user)
        return redirect(url_for('index'))

@app.route('/user/<nickname>',methods=['POST','GET'])
def user(nickname):
    global KAFENUT_NOTES
    user=User.query.filter_by(nickname=nickname).first() 
    if request.method=='GET':
        page=int(request.args.get('page',default=1))
        notes=Note.query.filter_by(author_id=user.id).order_by(Note.upload_time.desc()).paginate(page,NOTE_PER_PAGE,False)   #a paginate object
        return render_template('user.html',user=user,notes=notes,layout='user',kafenut_notes=KAFENUT_NOTES)
    
    else:   #when receiving a post
        if user!=g.user:
            flash('You have no privilege to access this page!')
            return render_template('index.html',kafenut_notes=KAFENUT_NOTES)
        Get=request.form.get
        if Get('avatar_str'):
            if not save_img_base64(Get('avatar_str'),user):
                flash('Profile error: can\'t this profile')
        if User.query.filter_by(email=Get('email')).first()!=g.user:
            flash('Edit error: this email has been registered!')
            return redirect(url_for('user',nickname=g.user.nickname))
        user.email=Get('email')
        user.tel_num=Get('tel_num')
        user.about_me=Get('about_me')
        db.session.add(user)
        db.session.commit()
        flash('修改成功！')
   
        return redirect(url_for('user',nickname=g.user.nickname))

@app.route('/user/<nickname>/blogs')
def blogs(nickname):
    global KAFENUT_NOTES
    user=User.query.filter_by(nickname=nickname).first()
    if user == None:
        flash('Can\'t find user '+nickname+' !')
        return redirect(url_for('index'))
    page=int(request.args.get('page',default=1))
    blogs=Blog.query.filter_by(author=user).order_by(Blog.upload_time.desc()).paginate(page,BLOGS_PER_PAGE,False)  #a paginate object  
    return render_template('blogs.html',blogs=blogs,user=user,kafenut_notes=KAFENUT_NOTES)


#blogs
@app.route('/blog_page',methods=['GET','POST'])
def blog_page():
    global KAFENUT_NOTES
    id=request.args.get('id')
    if id:
        id=int(id)
    blog=Blog.query.filter_by(id=id).first() 
    if blog is None:
            flash('No such blog!')
            return redirect('/index')
    
    if request.method=='GET':                          
        return render_template('blog_page.html',blog=blog,kafenut_notes=KAFENUT_NOTES)
    
    if g.user is None: #if method==POST(receiving a comment)
        flash('You need to log in to commend!')
        return render_template('index',kafenut_notes=KAFENUT_NOTES)
    Get=request.form.get
    if not Get('under_cmmt_id'):   #if it is a comment to blog
        cmmt=Comment(to_blog=blog,body=Get('body'),upload_time=datetime.utcnow(),author=g.user)
    else:
        under_cmmt=Comment.query.filter_by(id=Get('under_cmmt_id')).first()
        if under_cmmt is None:
            flash('No such comment!')
            return redirect('/index')
        if Get('to_cmmt_id'):
            cmmt=Sub_Comment(under_cmmt=under_cmmt,to_blog=blog,to_cmmt_id=Get('to_cmmt_id'),body=Get('body'),upload_time=datetime.utcnow(),author=g.user)
        else:
            cmmt=Sub_Comment(under_cmmt=under_cmmt,to_blog=blog,body=Get('body'),upload_time=datetime.utcnow(),author=g.user)
    db.session.add(cmmt)
    db.session.commit()
    flash('Comment successfully!')
    return redirect(url_for('blog_page')+'?id='+str(id))

@login_required
@app.route('/write_blog',methods=['GET','POST'])
def write_blog():
    global KAFENUT_NOTES
    if request.method=='GET':
        return render_template('new_blog.html',kafenut_notes=KAFENUT_NOTES)
    Get=request.form.get
    blog=Blog(title=Get('title'),body=Get('body'),author=g.user,upload_time=datetime.utcnow(),last_cmmt_time=datetime.utcnow())
    db.session.add(blog)
    db.session.commit()
    flash('Your blog is successfully uploaded!')
    return redirect(url_for('index'))

@login_required
@app.route('/like_blog',methods=['POST',])
def like_blog():
    global KAFENUT_NOTES
    data=json.loads(request.get_data())
    resp={'success':False}
    if data['type']=='blog':
        obj=Blog.query.filter_by(id=data['id']).first()
    elif data['type']=='cmmt':
        obj=Comment.query.filter_by(id=data['id']).first()
    elif data['type']=='sub_cmmt':
        obj=Sub_Comment.query.filter_by(id=data['id']).first()
    elif data['type']=='note_cmmt':
        obj=Note_Comment.query.filter_by(id=data['id']).first()
    else:
        flash('Wrong link')
        return redirect(url_for('index'))
        
    if data['title']!='like_blog':
        resp['text']='Bad data!'
    elif obj is None:
        resp['text']='No such object!'
    elif data['like']==True:
        obj.like_num+=1
        db.session.add(obj)
        db.session.commit()
        resp['success']=True
    else:
        obj.like_num-=1
        db.session.add(obj)
        db.session.commit()
        resp['success']=True
    return json.dumps(resp)     

#notes
@login_required
@app.route('/new_note',methods=['GET','POST'])
def new_note():
    global KAFENUT_NOTES
    if request.method=='GET':     
        return render_template('new_note.html',kafenut_notes=KAFENUT_NOTES)   

    #if receiving a json
    data=json.loads(request.get_data())
    resp=dict(success=False)
    if data['title']!='new_note':
        resp['text']='错误：无效的访问方法！'
        return json.dumps(resp)
    #if making a new folder
    if data['new_folder']==True:
        if len(g.user.folders) >= 5:
            resp['text']='错误：文件夹数目过多！'
            return json.dumps(resp)
        if '.' in data['note_path']:
            resp['text']='错误：文件夹名中存在非法字符！'
            return json.dumps(resp)
        if len(data['note_path'])>20:
            resp['text']='错误：文件夹名过长！'
            return json.dumps(resp)
        if not data['note_path'] in g.user.folders:
            g.user.folder=g.user.folder+'.'+data['note_path']
            db.session.add(g.user)
    #get next auto increased primary key
    sql="select max(id) from note"
    for i in db.session.execute(sql):
        for x in i:
            code=int(x)+1
    #save the note
    path=save_note(data['note_title'],data['note_body'],g.user.nickname,code)
    if path=='文件过大！':
        resp['text']=path
    else:
        note=Note(title=data['note_title'],upload_time=datetime.utcnow(),author=g.user,logic_folder=data['note_path'],path=path)
        db.session.add(note)
        db.session.commit()
        #reload KAFENUT_NOTES
        if note.author.nickname=='菜姬李':
            KAFENUT_NOTES=Note.query.filter_by(author_id=ADMIN.id)
        resp['success']=True
        resp['text']='Upload successfully!'
        resp['url']=url_for('note',note_id=note.id,nickname=note.author.nickname)
        flash('Nice upload!')
    return json.dumps(resp)

@app.route('/<nickname>/note/<note_id>',methods=['GET','POST'])
def note(nickname,note_id):
    global KAFENUT_NOTES
    user=User.query.filter_by(nickname=nickname).first()
    note=Note.query.filter_by(id=note_id).first()
    if not note:
        flash('No such note!')
        return redirect('index')
    if request.method=='GET':             
        note.view_num+=1
        db.session.add(note)
        db.session.commit()
        #only return level 1 comment
        cmmts=Note_Comment.query.filter(and_(Note_Comment.to_note_id==note.id,Note_Comment.level==1)) 
        return render_template('note_page.html',layout='note_layout',note=note,kafenut_notes=KAFENUT_NOTES,cmmts=cmmts)
   
    #if receiving a comment
    if not g.user:
        flash('You need to login first')
        return redirect(url_for('index'))
    Get=request.form.get
    cmmt=Note_Comment(upload_time=datetime.utcnow(),body=Get('body'),to_note_id=Get('to_note_id'),author_id=g.user.id)
    #if is a sub comment
    if Get('under_cmmt_id'):
        if Get('to_cmmt_id'):
            cmmt.to_cmmt_id=Get('to_cmmt_id')
            pcmmt=Note_Comment.query.filter_by(id=Get('to_cmmt_id'))
            cmmt.under_cmmt_id=pcmmt.under_cmmt.id
        else:
            cmmt.to_cmmt_id=Get('under_cmmt_id')
            cmmt.under_cmmt_id=Get('under_cmmt_id')
        cmmt.level=2
    else:
        cmmt.level=1
        last_cmmt=Note_Comment.query.filter(and_(Note_Comment.to_note_id==note.id,Note_Comment.level==1)).order_by(Note_Comment.upload_time.desc()).first()
        if last_cmmt:
            print(last_cmmt.floor)
            cmmt.floor=last_cmmt.floor+1
        else:
            cmmt.floor=1
    db.session.add(cmmt)  
    db.session.commit()
    return redirect(url_for('note',note_id=note.id)) 

@login_required
@app.route('/<nickname>/modify_note/<note_id>',methods=['GET','POST'])
def modify_note(nickname,note_id):
    global KAFENUT_NOTES
    user=User.query.filter_by(nickname=nickname).first()
    note=Note.query.get(int(note_id))
    if note.author.id!=g.user.id:
        flash('你没有权限访问该页面！')
        return redirect('/')
    if request.method=='GET':            
        if not note:
            flash('未找到该笔记！')
            return redirect(url_for('index'))
        return render_template('modify_note.html',note=note,kafenut_notes=KAFENUT_NOTES,layout='note_layout')
   
    #if receiving a modified note(ajax)
    data=json.loads(request.get_data())
    resp=dict(success=False)
    if data['title']!='modify_note':
        resp['text']='非法的访问方式!'
        return json.dumps(resp)
    #if making a new folder
    if data['new_folder']==True:
        if len(g.user.folders) >= 5:
            resp['text']='错误：文件夹数目过多！'
            return json.dumps(resp)
        if '.' in data['note_path']:
            resp['text']='错误：文件夹名中存在非法字符！'
            return json.dumps(resp)
        if len(data['note_path'])>20:
            resp['text']='错误：文件夹名过长！'
            return json.dumps(resp)
        if not data['note_path'] in g.user.folders:
            g.user.folder=g.user.folder+'.'+data['note_path']
            db.session.add(g.user)

    note=Note.query.get(int(data['note_id']))
    if not note:
        resp['text']='未找到目标笔记！'
        return json.dumps(resp)
    else:
        note.title=data['note_title']
        note.upload_time=datetime.utcnow()
        note.logic_folder=data['note_path']
        #update note
        path=save_note(data['note_title'],data['note_body'],g.user.nickname,note.id)
        note.path=path      
        db.session.add(note)
        db.session.commit()
        #reload KAFENUT_NOTES
        if note.author.nickname=='菜姬李':
            KAFENUT_NOTES=Note.query.filter_by(author_id=ADMIN.id)
        resp['success']=True
        resp['text']='修改成功!'     
        resp['url']=url_for('note',note_id=note.id,nickname=note.author.nickname)
        flash('修改成功！')
        return json.dumps(resp)

@login_required
@app.route('/<nickname>/delete_note',methods=['POST',])
def delete_note(nickname):
    global KAFENUT_NOTES
    data=json.loads(request.get_data())
    resp=dict(success=False)
    if data['title']!='delete_note':
        resp['text']='错误的访问方法!'

    note=Note.query.get(int(data['note_id']))
    if note.author.id!=g.user.id:
        resp['text']='你没有权限执行此操作！'

    #identity confirmed
    mes=del_note(note.path,note.title)
    if mes=='delete successfully!':
        db.session.delete(note)
        db.session.commit()
        flash('删除成功！')
    #reload KAFENUT_NOTES
    if note.author.nickname=='菜姬李':
        KAFENUT_NOTES=Note.query.filter_by(author_id=ADMIN.id)
    resp['text']=mes
    resp['success']=True
    resp['url']='/'
    return json.dumps(resp)

#kafenut
@app.route('/kafenut')
def kafenut():
    global KAFENUT_NOTES
    return render_template('kafenut_home.html',layout='note_layout',kafenut_notes=KAFENUT_NOTES)

@app.route('/kafenut/introduction')
def introduction():
    global KAFENUT_NOTES
    return render_template("introduction.html",kafenut_notes=KAFENUT_NOTES)

@app.route('/kafenut/contact_us',methods=['GET','POST'])
def contact():
    global KAFENUT_NOTES
    if request.method=='GET':
        page=int(request.args.get('page',default=1))
        issues=Issue.query.order_by(Issue.upload_time.desc()).paginate(page,ISSUE_PER_PAGE,False)
        return render_template("contact.html",kafenut_notes=KAFENUT_NOTES,issues=issues)
    #receiving a post
    else:
        Get=request.form.get
        if Get('anonymous')=='on':
            id=-1;
        else:
            id=g.user.id
        issue=Issue(upload_time=datetime.utcnow(),title=Get('issue_title'),body=Get('issue_body'),author_id=id)
        db.session.add(issue)
        db.session.commit()
        flash('您的建议已成功上传！')
    return redirect(url_for('contact')) 

#api
@app.route('/api')
def api():
    global KAFENUT_NOTES
    return render_template('api.html',kafenut_notes=KAFENUT_NOTES)

@app.route('/api/user')
def api_get_user():
    id=request.args.get('id')
    nickname=request.args.get('nickname')
    resp=dict(theme='api_get_user')
    
    if id is not None:
        id=int(id)
        user=User.query.filter_by(id=id).first()
    elif nickname is not None:
        user=User.query.filter_by(nickname=nickname).first()
    else:
        resp['success']=False
        resp['reason']='No arguments were given'
    
    if not user:    #No such user
        resp['success']=False
        resp['reason']='No such user'
    else:
        resp['success']=True
        resp['user']=dict(nickname=user.nickname,tel_num=user.tel_num,about_me=user.about_me,follower_num=user.followers.count(),followed_num=user.followeds.count(),blog_num=user.blogs.count(),last_seen_utc=str(user.last_seen))    
    return json.dumps(resp)

@app.route('/api/blogs')
def api_get_blogs():
    nickname=request.args.get('author')
    user=User.query.filter_by(nickname=nickname).first()
    resp=dict(theme='blogs')

    if user is None:
        resp['success']=False
        resp['reason']='No such user'
    else:
        resp['success']=True
        i=1
        blogs=dict()
        for blog in user.blogs.order_by(Blog.upload_time.desc()):
            blogs['blog'+str(i)]=dict(id=blog.id,author=blog.author.nickname,like_num=blog.like_num,cmmt_num=blog.cmmts.count()+blog.sub_cmmts.count(),upload_time=str(blog.upload_time),title=blog.title,body=blog.body)
            i=i+1
        resp['blogs']=blogs
    return json.dumps(resp)

@app.route('/api/blog_page')
def api_get_blog_page():
    id=request.args.get('id')
    resp=dict(theme='blog_page')

    if id is not None:
        id=int(id)
        blog=Blog.query.filter_by(id=id).first()
    else:
        resp['success']=False
        resp['reason']='No arguments were given'

    if not blog:
        resp['success']=False
        resp['reason']='No such blog'
    else:
        resp['success']=True
        obj=dict(author=blog.author.nickname,like_num=blog.like_num,cmmt_num=blog.cmmts.count()+blog.sub_cmmts.count(),upload_time=str(blog.upload_time),last_cmmt_time=str(blog.last_cmmt_time),title=blog.title,body=blog.body)
        i=1
        for cmmt in blog.cmmts.order_by(Comment.upload_time.asc()):
            comment=dict(author=cmmt.author.nickname,like_num=cmmt.like_num,cmmt_num=cmmt.sub_cmmts.count(),upload_time=str(cmmt.upload_time),body=cmmt.body)
            j=1
            for sub_cmmt in cmmt.sub_cmmts.order_by(Sub_Comment.upload_time.asc()):
                sub_comment=dict(author=sub_cmmt.author.nickname,like_num=cmmt.like_num,upload_time=str(sub_cmmt.upload_time),body=sub_cmmt.body)
                if sub_cmmt.to_cmmt is None:   #if it is a wild sub_cmmt
                    sub_comment['to_whom']='None'
                else:
                    sub_comment['to_whom']=sub_cmmt.to_cmmt.author.nickname
                comment['sub_cmmt'+str(j)]=sub_comment
                j=j+1
            obj['cmmt'+str(i)]=comment
            i=i+1
        resp['blog']=obj
    return json.dumps(resp)

#login management
@app.route('/login',methods=['POST',])
def login():
    if g.user and g.user.is_authenticated:
        flash('You have already logged in !')
        return redirect(url_for('/'))

    #receiving a json
    data=json.loads(request.get_data())
    resp=dict(success=False)
    if data['title']!='login':
        resp['text']='Bad data !'
        return json.dumps(resp)
    user=User.query.filter_by(email=data['email']).first()
    if user is None:
        resp['text']='Invalid email !'
    elif user.passwd!=data['passwd']:
        resp['text']='Wrong password !'
    else:
        login_user(user)
        flash('Login successfully !')
        resp['success']=True
        resp['text']='Login successfully !'
    return json.dumps(resp)

@app.route('/logout')
def logout():
    if not g.user.is_authenticated:
        flash('You have not logged in yet !')
        return redirect(url_for('index'))
    logout_user()
    flash('Logout successfully !')
    return redirect(url_for('index'))

@app.before_request
def before_request():
    g.user=current_user
    if g.user.is_authenticated:
        g.user.last_seen=datetime.utcnow()
        db.session.add(g.user)
        db.session.commit()
    return None

@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))



