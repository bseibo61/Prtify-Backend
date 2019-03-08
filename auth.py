import json
import flask
from flask import Flask, request, redirect, g, render_template
import requests
import base64
import urllib.parse
import time
import config
import firebase_admin
from firebase_admin import credentials, db
from multiprocessing import Process, Value, Manager
from ctypes import c_char_p
from firebase import firebase

# Sample python-firebase code
# See http://ozgur.github.io/python-firebase/
firebase = firebase.FirebaseApplication('https://voteify.firebaseio.com/', None)
result = firebase.get('/parties', None)
print("result",result)

app = Flask(__name__)

#  Client Keys
CLIENT_ID = config.CLIENT_ID
CLIENT_SECRET = config.CLIENT_SECRET


# Spotify URLS
SPOTIFY_AUTH_URL = "https://accounts.spotify.com/authorize"
SPOTIFY_TOKEN_URL = "https://accounts.spotify.com/api/token"
SPOTIFY_API_BASE_URL = "https://api.spotify.com"
API_VERSION = "v1"
SPOTIFY_API_URL = "{}/{}".format(SPOTIFY_API_BASE_URL, API_VERSION)


# Server-side Parameters
CLIENT_SIDE_URL = "http://127.0.0.1"
PORT = 8080
REDIRECT_URI = "{}:{}/callback/q".format(CLIENT_SIDE_URL, PORT)
SCOPE = "user-modify-playback-state user-read-currently-playing"
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()

manager = Manager()
authorization_header = manager.Value(c_char_p, "")
# authorization_header = Value('c',"")
test = None

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}



# cred = credentials.Certificate('voteify-firebase-adminsdk-awpcw-fb67cf1ed7.json')
# default_app = firebase_admin.initialize_app(cred, {
#     'databaseURL' : 'https://voteify.firebaseio.com/'
# })

# parties = db.reference('parties')

# pull from requests and put in queue
# def request_to_queue():
    
    # temp = root.get()
    # print(temp['parties']['boy'])

# request_to_queue()

@app.route("/")
def index():
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    req = flask.request.json
    print("Request is !!!!!!!!!!!!!!!!: ",req)
    return redirect(auth_url)

@app.route("/auth/<party>")
def auth(party):
    print("Party is: ",party)
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)

    # Add Party to Firebase

    from firebase import firebase

    firebase = firebase.FirebaseApplication('https://voteify.firebaseio.com/', None)
    # result = firebase.get('/parties', None)
    # print("result",result)

    # result = firebase.post('/parties', party, params={'print': 'pretty'}, {'name': party})
    result = firebase.post('/parties', data={party:"data"}, params={'print': 'pretty'})
    print("adding to firebase",result)
    return redirect(auth_url)


@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    notbase64 = "{}:{}".format(CLIENT_ID, CLIENT_SECRET).encode()
    base64encoded = base64.standard_b64encode(notbase64).decode()
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    print(headers)
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    print(response_data)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    global authorization_header
    authorization_header.value = {"Authorization":"Bearer {}".format(access_token)}
    request_data = ["stuff"]
    # getTime(authorization_header)
    # return render_template("index.html",sorted_array=[request_data])
    return redirect("http://benseibold.com/")

# finds the ammount of time left until the currently playing song ends and passes
# it to the slepper function
def getTime():
    curr_json = json.loads(requests.get("https://api.spotify.com/v1/me/player/currently-playing",headers=authorization_header.value).text)
    duration_ms = curr_json['item']['duration_ms']
    progress_ms = curr_json['progress_ms']
    sleeper((duration_ms-progress_ms)/1000)

# waits for the given time then calls to play the next song
def sleeper(s):
    try:
        num = float(s)
        time.sleep(num)
        play_song("The Only Thing","Sufjan Stevens")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        exit()

# needs to grab song from firebase then put it in playback
def play_song(track, artist):
    # gets song id from artist and track
    track_url ="https://api.spotify.com/v1/search?q=track%3A{}".format(track)+"+artist%3"+"A{}&type=track&limit=1".format(artist)
    track_json = json.loads(requests.get(track_url,headers=authorization_header.value).text)
    song_uri = track_json["tracks"]["items"][0]["uri"]
    # put top result on playback
    context_uri = {}
    context_uri["uris"] = [song_uri]
    json_uri = json.dumps(context_uri)
    play = requests.put('https://api.spotify.com/v1/me/player/play',headers=authorization_header.value,data=json_uri)
    getTime()

# Starts running continuously as program is started, kicks off song listening loop when it gets the authorization_header
def try_authentication(auth_header):
    print("try-auth called")
    while auth_header.value == "":
        time.sleep(1)
        print(auth_header.value)
    print("Got auth header")
    # getTime()


# removes other charactors from last fm for url query
def letters(input):
    valids = []
    for character in input:
        if character.isalpha():
            valids.append(character)
        elif character == ' ':
            valids.append('+')
    return ''.join(valids)





if __name__ == "__main__":
    p = Process(target=try_authentication, args=(authorization_header,))
    p.start()  
    app.run(debug=True, use_reloader=False, port=PORT)
    p.join()
