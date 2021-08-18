from flask import Flask
import os


TEMPLATE_FOLDER = os.path.join(os.path.split(__file__)[0], "templates")
app = Flask(__name__, static_folder="static", template_folder=TEMPLATE_FOLDER)
app.secret_key = "secret key"
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024
app.config['SESSION_TYPE'] = 'filesystem'