from client.client import Client

client = Client('./client/client.properties')
client.poll_playlist()
