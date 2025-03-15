import http.server
import socketserver
import os
import urllib.parse
import json
import socket
import datetime
import threading
from pymongo import MongoClient

# Конфігурація
HTTP_PORT = 3000
SOCKET_PORT = 5000
MONGODB_URI = "mongodb://mongodb:27017/"
DATABASE_NAME = "mydatabase"
COLLECTION_NAME = "messages"

# Клас HTTP-обробника
class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse