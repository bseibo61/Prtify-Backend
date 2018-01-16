import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
import spotipy.util as util

def auth():
    # Want to export these later
    client_id = "a843addfdfca4298ae0d7abb074e5c94"
    client_secret = "7062c3bbd0a34b3697bf4bff1680f272"
    username = "crimefightingcoconut"
    scope = "user-read-currently-playing"
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return client_credentials_manager

token = util.prompt_for_user_token("crimefightingcoconut","user-read-currently-playing",client_id="a843addfdfca4298ae0d7abb074e5c94",client_secret="7062c3bbd0a34b3697bf4bff1680f272",redirect_uri="http://127.0.0.1:8080/callback/")
client_id

sp = spotipy.Spotify(client_credentials_manager=auth())
sp.trace = True # turn on tracing
sp.trace_out = True # turn on trace out
user = sp.user("crimefightingcoconut")

playlists = sp.user_playlists(user)

print sp.me()
# while playlists:
#     for i, playlist in enumerate(playlists['items']):
#         print("%4d %s %s" % (i + 1 + playlists['offset'], playlist['uri'],  playlist['name']))
#     if playlists['next']:
#         playlists = sp.next(playlists)
#     else:
#         playlists = None
