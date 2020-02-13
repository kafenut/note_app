#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import os
from config import IMG_UPLOAD_FOLDER
def save_img_base64(s,user):
    img=base64.b64decode(s.split(',',1)[1]) 
    delete=False
    if user.avatar:
        num=int(user.avatar[:-5].split('_v=')[1])
        filename=user.nickname+'_v='+str(num+1)+'.jpeg'
        delete=True
    else:
        filename=user.nickname+'_v=1'+'.jpeg'
    pathname=os.path.join(IMG_UPLOAD_FOLDER,filename)
    with open(pathname,'wb') as f:
        f.write(img)              
        if delete:
            os.remove(user.avatar)
        user.avatar=pathname
    return True

from config import NOTE_UPLOAD_FOLDER
def save_note(title,body,nickname,code):
    tpath=nickname+'/'+str(code)+'.txt'
    body=body.encode('utf-8')
    if len(body)>50000:
        return '笔记过长！'
    #if folder don't exist
    if not os.path.exists(NOTE_UPLOAD_FOLDER+nickname):
        os.mkdir(NOTE_UPLOAD_FOLDER+nickname);
    with open(NOTE_UPLOAD_FOLDER+tpath,'wb') as f:
        f.write(body)
    return tpath
    
def del_note(path,title):
    tpath=NOTE_UPLOAD_FOLDER+path
    #if there is no such file
    print(tpath)
    if not os.path.exists(tpath):
        return '文件未存在！'
    os.remove(tpath)
    return 'delete successfully!'
