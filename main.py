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

# Підключення до MongoDB
client = MongoClient(MONGODB_URI)
db = client[DATABASE_NAME]
collection = db[COLLECTION_NAME]

# Клас HTTP-обробника
class MyHTTPRequestHandler(http.server.SimpleHTTPRequestHandler):
    def do_POST(self):
        if self.path == '/message':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            params = urllib.parse.parse_qs(post_data)
            
            username = params.get("username", [None])[0]
            message = params.get("message", [None])[0]
            
            if username and message:
                # Відправка повідомлення на Socket-сервер
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
                    sock.connect(("localhost", SOCKET_PORT))
                    data = json.dumps({"username": username, "message": message}).encode('utf-8')
                    sock.sendall(data)
                
                # Перенаправлення користувача після відправки форми
                self.send_response(302)
                self.send_header('Location', '/')
                self.end_headers()
            else:
                self.send_error(400, "Bad Request: Missing fields")
        else:
            self.send_error(404)
    
    def do_GET(self):
        if self.path.startswith("/static/"):
            self.path = self.path[1:]  # Видаляємо слеш для коректного шляху
        
        if self.path == "/error.html":
            self.send_response(404)
        
        return http.server.SimpleHTTPRequestHandler.do_GET(self)

# Запуск HTTP-сервера
def start_http_server():
    with socketserver.TCPServer(("", HTTP_PORT), MyHTTPRequestHandler) as httpd:
        print(f"HTTP Server запущено на порті {HTTP_PORT}")
        httpd.serve_forever()

# Запуск Socket-сервера для обробки повідомлень
def start_socket_server():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
        server_socket.bind(("", SOCKET_PORT))
        server_socket.listen()
        print(f"Socket Server запущено на порті {SOCKET_PORT}")
        
        while True:
            conn, _ = server_socket.accept()
            with conn:
                data = conn.recv(1024)
                if data:
                    message_data = json.loads(data.decode('utf-8'))
                    message_data["date"] = datetime.datetime.now().isoformat()
                    collection.insert_one(message_data)
                    print("Збережено повідомлення:", message_data)

# Запускаємо сервери у різних потоках
if __name__ == "__main__":
    threading.Thread(target=start_http_server).start()
    threading.Thread(target=start_socket_server).start()

