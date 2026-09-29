# MoMo Transactions API Documentation
 
**Base URL:** `http://localhost:8000`
 
**Authentication:** Every endpoint requires HTTP Basic Auth. Missing or invalid credentials return `401 Unauthorized` with header `WWW-Authenticate: Basic realm="MoMo API"`.
 
**Required fields for POST/PUT body:** `transaction_type`, `amount`, `sender`, `receiver` (`amount` must be a number).
 
---
 
## 1. GET /transactions
 
List all transactions.
 
**Request**
```
curl -u admin:secret http://localhost:8000/transactions
```
 
**Response — 200 OK**
```json
[
  {
    "id": 1,
    "transaction_type": "received",
    "amount": 2000,
    "fee": 0,
    "balance_after": 2000,
    "sender": "Jane Smith",
    "receiver": "You",
    "sender_phone": "*********013",
    "receiver_phone": null,
    "transaction_id": "76662021700",
    "timestamp": "2024-05-10 16:30:51",
    "date_epoch_ms": 1715351458724,
    "readable_date": "10 May 2024 4:30:58 PM",
    "body": "You have received 2000 RWF from Jane Smith ..."
  }
]
```
 
**Error codes**
| Code | Meaning |
|---|---|
| 401 | Missing or invalid credentials |
 
---
 
## 2. GET /transactions/{id}
 
Get one transaction by its id.
 
**Request**
```
curl -u admin:secret http://localhost:8000/transactions/1
```
 
**Response — 200 OK**
```json
{
  "id": 1,
  "transaction_type": "received",
  "amount": 2000,
  "fee": 0,
  "balance_after": 2000,
  "sender": "Jane Smith",
  "receiver": "You",
  "sender_phone": "*********013",
  "receiver_phone": null,
  "transaction_id": "76662021700",
  "timestamp": "2024-05-10 16:30:51",
  "date_epoch_ms": 1715351458724,
  "readable_date": "10 May 2024 4:30:58 PM",
  "body": "You have received 2000 RWF from Jane Smith ..."
}
```
 
**Error codes**
| Code | Meaning |
|---|---|
| 401 | Missing or invalid credentials |
| 400 | `{"error": "Invalid ID"}` — id is not a number |
| 404 | `{"error": "Not Found"}` — id does not exist |
 
---
 
## 3. POST /transactions
 
Create a new transaction.
 
**Request**
```
curl -u admin:secret -X POST \
  -H "Content-Type: application/json" \
  -d '{"transaction_type":"payment","amount":500,"sender":"You","receiver":"Test"}' \
  http://localhost:8000/transactions
```
 
**Response — 201 Created**
```json
{
  "id": 1692,
  "transaction_type": "payment",
  "amount": 500,
  "sender": "You",
  "receiver": "Test"
}
```
The `id` is auto-assigned (one greater than the current highest id).
 
**Error codes**
| Code | Meaning |
|---|---|
| 401 | Missing or invalid credentials |
| 400 | `{"error": "Invalid or missing JSON body"}` — body isn't valid JSON |
| 400 | `{"error": "Missing field: <name>"}` — a required field is absent |
| 400 | `{"error": "amount must be a number"}` |
 
---
 
## 4. PUT /transactions/{id}
 
Replace an existing transaction.
 
**Request**
```
curl -u admin:secret -X PUT \
  -H "Content-Type: application/json" \
  -d '{"transaction_type":"payment","amount":999,"sender":"You","receiver":"Updated"}' \
  http://localhost:8000/transactions/1
```
 
**Response — 200 OK**
```json
{
  "id": 1,
  "transaction_type": "payment",
  "amount": 999,
  "sender": "You",
  "receiver": "Updated"
}
```
 
**Error codes**
| Code | Meaning |
|---|---|
| 401 | Missing or invalid credentials |
| 400 | `{"error": "Invalid or missing JSON body"}` |
| 400 | `{"error": "Missing field: <name>"}` |
| 400 | `{"error": "amount must be a number"}` |
| 404 | `{"error": "Not Found"}` — id does not exist |
 
---
 
## 5. DELETE /transactions/{id}
 
Delete a transaction by id.
 
**Request**
```
curl -u admin:secret -X DELETE http://localhost:8000/transactions/1
```
 
**Response — 200 OK**
```json
{"message": "Transaction 1 deleted"}
```
 
**Error codes**
| Code | Meaning |
|---|---|
| 401 | Missing or invalid credentials |
| 400 | `{"error": "Invalid ID"}` — id is not a number |
| 404 | `{"error": "Not Found"}` — id does not exist |
 
---
 
## Test evidence
 
Screenshots proving each of the above (successful GET/POST/PUT/DELETE, and an unauthorized request) are in the `screenshots/` folder of this repo.