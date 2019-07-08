import requests
import threading
import sys
import spotify_credentials

client_id = spotify_credentials.client_id
client_secret = spotify_credentials.client_secret
grant_type = 'client_credentials'
body_params = {'grant_type' : grant_type}

playlists = []
global result


def client_auth(ci,cs):
	url='https://accounts.spotify.com/api/token'
	req = requests.post(url, data=body_params, auth = (ci, cs))
	return req.json()["access_token"], req.status_code


def getListPlaylists(token, userid):
	url = "https://api.spotify.com/v1/users/{}/playlists?limit=50".format(userid);
	data = requests.get(url, headers={"Authorization": 'Bearer ' + token})

#	print(data.json())
	for i in data.json()["items"]:
		playlists.append((i["id"], i["name"]));

	return

def searchPlaylist(playlist_id, token, query):
	found = False;

	url = "https://api.spotify.com/v1/playlists/{}/tracks".format(playlist_id[0])
	data = requests.get(url, headers={"Authorization": 'Bearer ' + token})
	for i in data.json()["items"]:
		for j in i["track"]["artists"]:
			if j["id"] == query:
				found = True
				print(str(found) + " -> " + playlist_id[1])
				return
	# result = result & found
	return

def artist_id(token,query,limit):
	url = 'https://api.spotify.com/v1/search?query='+query+'&type=artist&market=US&offset=0&limit=' + limit
	art_id = requests.get(url, headers={"Authorization": 'Bearer ' + token}).json()['artists']['items'][0]['id']
	return art_id

def checkArtistById(token, id):
	url = "https://api.spotify.com/v1/artists/{}".format(id)
	data = requests.get(url, headers={"Authorization": 'Bearer ' + token})
	return data.json()["name"]



def main():

	if(len(sys.argv) != 3):
		print("usage: checkout.py <userid> <artist> ")

	register = client_auth(client_id,client_secret)
	token = register[0]
	userid = sys.argv[1]

	if register[1] == 200:
		print("hey {}, have you heard of {}? ".format( userid, sys.argv[2]))
		result = False
		query = artist_id(token, sys.argv[2], str(10))
		name = checkArtistById(token, query)
		print("\t[DEBUGINFO]", name + " -> " + query)

		getListPlaylists(token, userid)
		threads = list()
		for i in range(0,len(playlists)):
			t  = threading.Thread(target=searchPlaylist, args=(playlists[i],token,query))
			threads.append(t)
			t.start()

		for index, thread in enumerate(threads):
			thread.join()
	else:
		print("\t[DEBUGINFO]", register)
	return


if (__name__ == "__main__") : main()