from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import base64
import binascii
import secrets

USERNAME = "admin"
PASSWORD = "secret"

REQUIRED_FIELDS = ("type", "amount", "sender", "receiver")

transactions = {
    1: {"id": 1, "type": "payment", "amount": 1000, "sender": "A", "receiver": "B"},
    2: {"id": 2, "type": "deposit", "amount": 5000, "sender": "C", "receiver": "D"},
}


def validate_transaction(data):
    for field in REQUIRED_FIELDS:
        if field not in data:
            return f"Missing field: {field}"
    amount = data["amount"]
    if isinstance(amount, bool) or not isinstance(amount, (int, float)):
        return "amount must be a number"
    return None


class TransactionHandler(BaseHTTPRequestHandler):

    def path_parts(self):
        # Ignores query strings and empty segments: "/transactions/1" -> ["transactions", "1"]
        return [p for p in urlparse(self.path).path.split("/") if p]

    def do_GET(self):

        if not self.is_authorized():
            self.send_unauthorized()
            return

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

    def is_authorized(self):
        header = self.headers.get("Authorization")
        if header is None:
            return False

        if not header.startswith('Basic '):
            return False

        encode = header[len("Basic "):]

        try:
            decoded = base64.b64decode(encode).decode("utf-8")
            username, password = decoded.split(":", 1)
        except (binascii.Error, UnicodeDecodeError, ValueError):
            return False

        user_ok = secrets.compare_digest(username.encode(), USERNAME.encode())
        pass_ok = secrets.compare_digest(password.encode(), PASSWORD.encode())
        return user_ok and pass_ok
        
    def send_json(self, status, data, extra_headers=None):
        body = json.dumps(data).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        if extra_headers:
            for name, value in extra_headers.items():
                self.send_header(name, value)
        self.end_headers()
        self.wfile.write(body)

    def send_unauthorized(self):
        self.send_json(
            401,
            {"error": "Unauthorized"},
            {"WWW-Authenticate": 'Basic realm="MoMo API"'},
        )


    def read_json_body(self):
        try:
            length = int(self.headers.get("Content-Length", 0))
            if length <= 0:
                return None
            raw = self.rfile.read(length)
            data = json.loads(raw)
        except (ValueError, UnicodeDecodeError):
            return None

        if not isinstance(data, dict):
            return None
        return data

    
    def do_POST(self):
        if not self.is_authorized():
            self.send_unauthorized()
            return

        if self.path_parts() != ["transactions"]:
            self.send_json(404, {"error": "Not Found"})
            return

        data = self.read_json_body()
        if data is None:
            self.send_json(400, {"error": "Invalid or missing JSON body"})
            return

        error = validate_transaction(data)
        if error:
            self.send_json(400, {"error": error})
            return

        new_id = max(transactions, default=0) + 1
        new_record = {
            "id": new_id,
            "type": data["type"],
            "amount": data["amount"],
            "sender": data["sender"],
            "receiver": data["receiver"],
        }
        transactions[new_id] = new_record
        self.send_json(201, new_record)

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), TransactionHandler)
    print("Serving on http://localhost:8000")
    server.serve_forever()