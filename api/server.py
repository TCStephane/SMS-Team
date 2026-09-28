from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib.parse import urlparse
import json
import base64
import binascii
import secrets
from pathlib import Path
import os


USERNAME = os.environ.get("API_USERNAME", "admin")
PASSWORD = os.environ.get("API_PASSWORD", "secret")

REQUIRED_FIELDS = ("transaction_type", "amount", "sender", "receiver")


ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "data" / "processed" / "transactions.json"
with open(JSON_PATH, 'r') as file:
    records = json.load(file)
transactions = {r["id"]: r for r in records}


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
        new_record = dict(data)
        new_record["id"] = new_id
        transactions[new_id] = new_record
        self.send_json(201, new_record)


    def get_id(self):
        parts = self.path_parts()
        if len(parts) != 2 or parts[0] != "transactions":
            return None, (404, "Not Found")
        try:
            return int(parts[1]), None
        except ValueError:
            return None, (400, "Invalid ID")


    def do_PUT(self):
        if not self.is_authorized():
            self.send_unauthorized()
            return

        tid, err = self.get_id()
        if err:
            self.send_json(err[0], {"error": err[1]})
            return

        if tid not in transactions:
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

        updated = dict(data)
        updated["id"] = tid
        transactions[tid] = updated
        self.send_json(200, transactions[tid])


    def do_DELETE(self):
        if not self.is_authorized():
            self.send_unauthorized()
            return

        tid, err = self.get_id()
        if err:
            self.send_json(err[0], {"error": err[1]})
            return

        if tid not in transactions:
            self.send_json(404, {"error": "Not Found"})
            return

        del transactions[tid]
        self.send_json(200, {"message": f"Transaction {tid} deleted"})

if __name__ == "__main__":
    server = HTTPServer(("localhost", 8000), TransactionHandler)
    print("Serving on http://localhost:8000")
    server.serve_forever()