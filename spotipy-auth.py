import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

def auth():
    # Want to export these later
    client_id = "a843addfdfca4298ae0d7abb074e5c94"
    client_secret = "7062c3bbd0a34b3697bf4bff1680f272"
    client_credentials_manager = SpotifyClientCredentials(client_id=client_id, client_secret=client_secret)
    return client_credentials_manager

util.prompt_for_user_token(username,scope,client_id=client_id,client_secret=client_secret,redirect_uri=localhost:8080/callback)


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
