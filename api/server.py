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
        elif self.path.startswith('/transactions/'):
            path_split = self.path.split('/')
            try:
                transaction_id = int(path_split[2])
                for transaction in transactions:
                    if transaction["id"] == transaction_id:
                        self.send_response(200)
                        self.send_header('Content-Type', 'application/json')
                        self.end_headers()
                        self.wfile.write(json.dumps(transaction).encode())
                        return
                    
                self.send_response(404)
                self.end_headers()
                self.wfile.write(b'Not Found')
            except ValueError:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b'Invalid ID')
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'Not Found')

server = HTTPServer(('localhost', 8000), TransactionHandler)
server.serve_forever()