import json
from flask import Flask, request, redirect, g, render_template
import requests
import base64
import urllib
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util


app = Flask(__name__)

#  Client Keys
client_id = "a843addfdfca4298ae0d7abb074e5c94"
client_secret = "7062c3bbd0a34b3697bf4bff1680f272"
username = "crimefightingcoconut"
scope = "user-read-currently-playing"
client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)

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
STATE = ""
SHOW_DIALOG_bool = True
SHOW_DIALOG_str = str(SHOW_DIALOG_bool).lower()


auth_query_parameters = {
    "response_type": "code",
    "redirect_uri": REDIRECT_URI,
    "scope": scope,
    # "state": STATE,
    # "show_dialog": SHOW_DIALOG_str,
    "client_id": client_id
}

@app.route("/")
def index():
    # Auth Step 1: Authorization
    # url_args = "&".join(["{}={}".format(key,urllib.quote(val)) for key,val in auth_query_parameters.iteritems()])
    # auth_url = "{}/?{}".format(SPOTIFY_AUTH_URL, url_args)
    token = util.prompt_for_user_token("crimefightingcoconut","user-read-currently-playing",client_id="a843addfdfca4298ae0d7abb074e5c94",client_secret="7062c3bbd0a34b3697bf4bff1680f272",redirect_uri="http://127.0.0.1:8080/callback/")

    return redirect(token)

@app.route("/callback/q")
def callback():
    # Auth Step 4: Requests refresh and access tokens
    auth_token = request.args['code']
    code_payload = {
        "grant_type": "authorization_code",
        "code": str(auth_token),
        "redirect_uri": REDIRECT_URI
    }
    base64encoded = base64.b64encode("{}:{}".format(CLIENT_ID, CLIENT_SECRET))
    headers = {"Authorization": "Basic {}".format(base64encoded)}
    post_request = requests.post(SPOTIFY_TOKEN_URL, data=code_payload, headers=headers)

    # Auth Step 5: Tokens are Returned to Application
    response_data = json.loads(post_request.text)
    access_token = response_data["access_token"]
    refresh_token = response_data["refresh_token"]
    token_type = response_data["token_type"]
    expires_in = response_data["expires_in"]

    # Auth Step 6: Use the access token to access Spotify API
    authorization_header = {"Authorization":"Bearer {}".format(access_token)}

    # Get profile data
    user_profile_api_endpoint = "{}/me".format(SPOTIFY_API_URL)
    profile_response = requests.get(user_profile_api_endpoint, headers=authorization_header)
    profile_data = json.loads(profile_response.text)

    # Get user playlist data
    playlist_api_endpoint = "{}/playlists".format(profile_data["href"])
    playlists_response = requests.get(playlist_api_endpoint, headers=authorization_header)
    playlist_data = json.loads(playlists_response.text)

    # Combine profile and playlist data to display
    display_arr = [profile_data] + playlist_data["items"]
    return render_template("index.html",sorted_array=display_arr)

if __name__ == "__main__":
    app.run(debug=True,port=PORT)
