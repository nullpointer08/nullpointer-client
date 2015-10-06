'''
Demonstration for a client which downloads a playlist,
downloads files from the playlist and begins to view them according 
to the playlist schedule.

Configure the client/client.properties file before starting.

For a very simple playlist server navigate to the folder:

$ cd client/dev_test_server/
$ python dev_test_server.py

Note: it matters what folder the server is started in
The server will start serving files in the folder, e.g.
the playlist.json file.

To check if it is running

$ curl localhost:8080/playlist.json
'''

from client.client import Client

client = Client('./client/client.properties')
client.poll_playlist()
