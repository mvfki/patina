import os
from .app import app
import urllib.request
from flask import Flask, flash, request, redirect, url_for, render_template, session
from flask_session import Session
from werkzeug.utils import secure_filename
import numpy as np
import cv2
import base64
from .patina import *
from .webfig import *

ALLOWED_EXTENSIONS = set(['png', 'jpg', 'jpeg'])
SESSION_TYPE = 'redis'

# STAGE == 0 => Just arrived in homepage
# STAGE == 1 => Just successfully uploaded an image
# STAGE == 2 => Just successfully added the effects

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS
    
@app.route('/')
def upload_form():
    session['STAGE'] = 0
    return render_template('upload.html')

@app.route('/patina', methods=['POST'])
def display_image():
    STAGE = session.get('STAGE')
    if STAGE == 0:
        if 'file' not in request.files:
            flash('No file part')
            return redirect('/')
        file = request.files['file']
        if file.filename == '':
            flash('未选中图片！')
            return redirect('/')
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            img = read_image_to_array(file)
            img_exist = None
            if len(img.shape) == 3:
                img_exist = True
            img_base64 = array_to_base64(img)
            session["img_base64"] = img_base64
            STAGE = 1
            session['STAGE'] = STAGE
            return render_template('patina.html', orimg=img_base64, stage=STAGE)
        else:
            flash('请选择这些格式的图片：png, jpg, jpeg')
            return redirect('/')
    elif STAGE > 0:
        img_base64 = session.get('img_base64')

        niter = request.form.get('niter', type=int)
        quality = request.form.get('quality', type=int)
        if niter and quality:
            img = base64_to_array(img_base64)
            img_patina = jpg_comp(iter_patina(img, niter), quality)
            img_patina_base64 = array_to_base64(img_patina)
            STAGE = 2
            session['STAGE'] = STAGE
            return render_template('patina.html', orimg=img_base64, 
                ptnimg=img_patina_base64, niter=niter, quality=quality, 
                stage=STAGE)
        else:
            return render_template('patina.html', orimg=img_base64, stage=STAGE)


def read_image_to_array(file):
    '''"file" should be an werkzeug.datastructures.FileStorage object
    Returns an np.ndarray of the (m, n, 3) image'''
    file_bytes = np.asarray(bytearray(file.read()), dtype=np.uint8)
    img = cv2.imdecode(file_bytes, cv2.IMREAD_UNCHANGED)
    return img

def start_web_app(port=2333, debug=True):
    Session(app)
    sess = Session()
    sess.init_app(app)
    app.run(port=port, debug=debug, host="0.0.0.0")

if __name__ == "__main__":
    start_web_app()