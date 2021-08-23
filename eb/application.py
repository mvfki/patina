#!/usr/bin/python3

import os
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, session, after_this_request, send_file
from flask_session import Session
from werkzeug.utils import secure_filename
from flask_apscheduler import APScheduler
import numpy as np
import cv2
import base64
from datetime import datetime
import hashlib

UPLOAD_FOLDER = 'static/uploaded/'
TEMPLATE_FOLDER = os.path.join(os.path.split(__file__)[0], "templates")
STATIC_FOLDER = os.path.join(os.path.split(__file__)[0], "static")

class Config:
    SCHEDULER_API_ENABLED = True

application = Flask(__name__, static_folder=STATIC_FOLDER, template_folder=TEMPLATE_FOLDER)
application.secret_key = "secret key"
application.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
application.config['SESSION_TYPE'] = 'filesystem'
application.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
application.config.from_object(Config())
scheduler = APScheduler()
scheduler.init_app(application)
scheduler.start()

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])


# STAGE == 0 => Just arrived in homepage
# STAGE == 1 => Just successfully uploaded an image
# STAGE == 2 => Just successfully added the effects

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@application.route('/')
def upload_form():
    session['STAGE'] = 0
    return render_template('upload.html')

@application.route('/', methods=['POST'])
def display_image():
    STAGE = session.get('STAGE')
    if STAGE == 0:
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/')
        file = request.files['file']
        if file.filename == '':
            flash('No image selected!')
            return redirect('/')
        if file and allowed_file(file.filename):
            file_path = save_image(file)
            STAGE = 1
            session['STAGE'] = STAGE
            session['orig_img_path'] = file_path
            return render_template('patina.html', orimg=file_path, stage=STAGE)
        else:
            flash('Please select image of one of these format: png, jpg, jpeg')
            return redirect('/')
    elif STAGE > 0:
        niter = request.form.get('niter', type=int)
        quality = request.form.get('quality', type=int)
        if niter and quality:
            orig_img_path = session.get('orig_img_path')
            if not os.path.exists(orig_img_path):
                flash("会话已过期，请重新上传图片")
                return redirect("/")
            try:
                scheduler.modify_job(orig_img_path, trigger="interval", minutes=10)
            except:
                flash("会话已过期，请重新上传图片")
                return redirect("/")
            img = cv2.imread(orig_img_path)
            img_patina = jpg_comp(iter_patina(img, niter), quality)
            img_path_parent, img_name = os.path.split(orig_img_path)
            new_img_path = os.path.join(img_path_parent, 'patina_'+img_name)
            cv2.imwrite(new_img_path, img_patina)
            session['new_img_path'] = new_img_path
            STAGE = 2
            session['STAGE'] = STAGE
            return render_template('patina.html', orimg=orig_img_path, 
                ptnimg=new_img_path, niter=niter, quality=quality, 
                stage=STAGE)
        else:
            file_path = session.get('orig_img_path')
            return render_template('patina.html', orimg=file_path, stage=STAGE)

# Below are app helpers
def save_image(file):
    '''"file" should be an werkzeug.datastructures.FileStorage object
    Returns an np.ndarray of the (m, n, 3) image'''
    filename = get_secure_filename(file.filename)
    if not os.path.exists(UPLOAD_FOLDER):
        os.mkdir(UPLOAD_FOLDER)
    file_path = os.path.join(application.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    print("Saved file '%s' to '%s'"%(filename, application.config['UPLOAD_FOLDER']))
    print(file_path)
    scheduler.add_job(file_path, delete_file, args=[file_path], trigger="interval", minutes=10)
    return file_path

def delete_file(file_path=None):
    if file_path:
        print("Deleting file:", file_path)
        if os.path.exists(file_path):
            os.remove(file_path)

        img_path_parent, img_name = os.path.split(file_path)
        new_img_path = os.path.join(img_path_parent, 'patina_'+img_name)
        print("Deleting file:", new_img_path)
        if os.path.exists(new_img_path):
            os.remove(new_img_path)
        
        scheduler.remove_job(file_path)

def get_secure_filename(filename):
    dt_obj = datetime.now()
    dt_str = dt_obj.strftime("%y%m%d_%H%M%S")
    
    md5 = hashlib.md5()
    md5. update(filename.encode())
    digest = md5. hexdigest()
    md5_head = digest[:6]

    ext_name = filename.split('.')[-1]
    return dt_str + '_' + md5_head + '.' + ext_name

def start_web_application():
    Session(application)
    sess = Session()
    sess.init_app(application)
    application.debug = True
    application.run()

# Below are computational part functions
def _trim_uv(array):
    array[array>127] = 127
    array[array<-128] = -128
    return array

def _trim(array):
    array[array>255] = 255
    array[array<0] = 0
    return array

def patina(array):
    if array is None:
        return None
    R = array[:,:,0].astype("float")
    G = array[:,:,1].astype("float")
    B = array[:,:,2].astype("float")
    y = _trim(np.floor((77*R + 150*G +  29*B)/256))
    u = _trim_uv(np.floor((-43*R -  85*G + 128*B) /256) - 1)
    v = _trim_uv(np.floor((128*R - 107*G -  21*B) /256) - 1)
    r1 = _trim(np.floor((65536*y           + 91881*v) / 65536))
    g1 = _trim(np.floor((65536*y - 22553*u - 46802*v) / 65536))
    b1 = _trim(np.floor((65536*y + 116130*u         ) / 65536))
    array[:,:,0] = r1
    array[:,:,1] = g1
    array[:,:,2] = b1
    array.astype(np.uint8)
    return array

def iter_patina(array, niter = 6):
    for i in range(niter):
        array = patina(array)

    return array

def jpg_comp(array, quality = 10):
    if array is None:
        return None
    ecd, ecd2 = cv2.imencode(".jpg", array, [int(cv2.IMWRITE_JPEG_QUALITY), quality])
    array = cv2.imdecode(ecd2, cv2.IMREAD_UNCHANGED)
    return array

if __name__ == "__main__":
    Session(application)
    sess = Session()
    sess.init_app(application)
    application.debug = True
    application.run(port=2333)
