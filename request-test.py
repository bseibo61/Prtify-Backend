import requests

r = requests.get('https://api.spotify.com/v1/browse/featured-playlists')
print r.text
