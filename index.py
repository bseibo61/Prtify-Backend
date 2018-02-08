# This file serves all the pages through flask
import json
from flask import Flask, request, redirect, g, render_template, url_for
import requests
import base64
import urllib

app = Flask(__name__)

CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

@app.route("/")
def index():
    return redirect(url_for('static',filename='Prtify-WebApp/index.html'))


if __name__ == "__main__":
    app.run(debug=True,port=PORT)
