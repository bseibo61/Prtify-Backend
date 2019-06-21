import json
import flask
from flask import Flask, request, redirect, g, render_template, url_for
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

firebase = firebase.FirebaseApplication('https://voteify.firebaseio.com/', None)
result = firebase.get('/parties', None)
print("result",result)

app = Flask(__name__)

# remove this line when done serving static files
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0

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
pass_through_party = manager.Value(c_char_p, "")
party = ""

auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": SCOPE,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": CLIENT_ID
}

@app.route("/")
def index():
    return redirect(url_for("static",filename="Prtify-WebApp/index.html"))

@app.route("/auth/<new_party>/<uid>")
def auth(new_party, uid):
    global pass_through_party
    pass_through_party.value = new_party
    party = pass_through_party.value
    print("Party is: ",party, "uid is:",uid)
    # Auth Step 1: Authorization
    url_args = "&".join(["{}={}".format(key,urllib.parse.quote(val)) for key,val in auth_query_parameters.items()])
    auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)

    # Add Party to Firebase
    # I really don't understand why this import has to be here   
    from firebase import firebase
    firebase = firebase.FirebaseApplication('https://voteify.firebaseio.com/', None)

    # Add Party
    result = firebase.patch('/parties/'+party+'/', {'name': party, 'users': []})
    # Adds uid to users
    firebase.patch('/parties/'+party+'/users/'+uid+'/', {'uid': uid} )
    # add party to user info
    firebase.patch('/users/'+uid+'/', {'party': party})

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

    # This will need to change to the address of the flask server
    return redirect("http://localhost:5000/main.html")

# finds the ammount of time left until the currently playing song ends and passes
# it to the slepper function
def getTime():
    print("requests is:",requests.get("https://api.spotify.com/v1/me/player/currently-playing",headers=authorization_header.value).status_code)
    # Check if there even is a song playing 
    if requests.get("https://api.spotify.com/v1/me/player/currently-playing",headers=authorization_header.value).status_code == 204:
        print("No song playing yet")
        sleeper(10)
    else:
        curr_json = json.loads(requests.get("https://api.spotify.com/v1/me/player/currently-playing",headers=authorization_header.value).text)
        duration_ms = curr_json['item']['duration_ms']
        progress_ms = curr_json['progress_ms']
        sleeper((duration_ms-progress_ms)/1000)

# waits for the given time then calls to play the next song
def sleeper(s):
    try:
        # if requests has songs in it, add requests to queue
        from firebase import firebase
        global party
        firebase = firebase.FirebaseApplication('https://voteify.firebaseio.com/', None)
        result = firebase.get('/parties', None)
        print("sleeper party:",party)

        num = float(s)
        time.sleep(num)

        print("Restarting Test Sufjan")
        play_song("The Only Thing","Sufjan Stevens")
    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        exit()

# needs to grab song from firebase then put it in playback
# Note: song will only play if spotfy is already playing
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
    print("PLAY SONG!!")
    getTime()

# Starts running continuously as program is started, kicks off song listening loop when it gets the authorization_header
def try_authentication(auth_header, pass_through_party, f):
    global party
    
    party = pass_through_party.value
    while auth_header.value == "" or pass_through_party.value == "":
        time.sleep(1)
        party = pass_through_party.value
    f()


# removes other charactors from last fm for url query
def letters(input):
    valids = []
    for character in input:
        if character.isalpha():
            valids.append(character)
        elif character == ' ':
            valids.append('+')
    return ''.join(valids)

# This should log into firebase and move songs from the requests to the queue
# Right now it just checks if the request queue is populated every 5 seconds,
# but it would be better if there was a firebase listener on the requests queue
def requests_to_queue():
    # Makes sure user is logged in
    while authorization_header.value == "":
        time.sleep(1)
        print(authorization_header.value)
    
    try:
        # if requests has songs in it, add requests to queue
        from firebase import firebase
        global party
        firebase = firebase.FirebaseApplication('https://voteify.firebaseio.com/', None)
        requests = firebase.get('/parties/'+party+'/requests/pizza/', None)
        # TODO: requests gets the name and artest of the song to move to the queue.  Move it with spotify api.  Also this gets called every 5 seconds but a firebase listener would be better so figure that out
        print("REQUESTS TO QUEUE party:",party)
        print("requests to queue json",requests)
        time.sleep(5)
        requests_to_queue()

    except KeyboardInterrupt:
        print("KeyboardInterrupt")
        exit()

    print("requests to queue")


# Kicks off multithreading
if __name__ == "__main__":
    song_loop_process = Process(target=try_authentication, args=(authorization_header,pass_through_party,getTime))
    queue_process = Process(target=try_authentication, args=(authorization_header,pass_through_party,requests_to_queue))

    song_loop_process.start()  
    queue_process.start()

    app.run(debug=True, use_reloader=False, port=PORT)
    song_loop_process.join()
    queue_process.join()
