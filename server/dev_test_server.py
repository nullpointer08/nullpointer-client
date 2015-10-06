'''
Starts a simple HTTP server which serves content in the directory of 
this file. Used for small tests of e.g. the client application
'''

import SimpleHTTPServer
import SocketServer

PORT = 8080
Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

httpd = SocketServer.TCPServer(('', PORT), Handler)

print 'Running server at port ', PORT

httpd.serve_forever()
