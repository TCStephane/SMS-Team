from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json

# id -> transaction. Later, load this from Dorcase's parser instead.
transactions = {
    1: {"id": 1, "type": "payment", "amount": 1000, "sender": "A", "receiver": "B"},
    2: {"id": 2, "type": "deposit", "amount": 5000, "sender": "C", "receiver": "D"},
}


class TransactionHandler(BaseHTTPRequestHandler):

    def send_json(self, status, data):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def path_parts(self):
        # Ignores query strings and empty segments: "/transactions/1" -> ["transactions", "1"]
        return [p for p in urlparse(self.path).path.split("/") if p]

    def do_GET(self):
        parts = self.path_parts()

        if parts == ["transactions"]:
            self.send_json(200, list(transactions.values()))

        elif len(parts) == 2 and parts[0] == "transactions":
            try:
                tid = int(parts[1])
            except ValueError:
                self.send_json(400, {"error": "Invalid ID"})
                return

            transaction = transactions.get(tid)
            if transaction is None:
                self.send_json(404, {"error": "Not Found"})
            else:
                self.send_json(200, transaction)

        else:
            self.send_json(404, {"error": "Not Found"})


if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), TransactionHandler)
    print("Serving on http://localhost:8000")
    server.serve_forever()