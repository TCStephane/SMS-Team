from http.server import BaseHTTPRequestHandler, HTTPServer
import json

transactions = [
    {"id": 1, "type": "payment", "amount": 1000, "sender": "A", "receiver": "B"},
    {"id": 2, "type": "deposit", "amount": 5000, "sender": "C", "receiver": "D"},
]

class TransactionHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/transactions':
            self.send_response(200)
            self.send_header('Content-Type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(transactions).encode())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

server = HTTPServer(('localhost', 8000), TransactionHandler)
server.serve_forever()