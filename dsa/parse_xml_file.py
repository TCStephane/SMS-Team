import json
import re
import sys
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
XML_PATH = ROOT / "data" / "raw" / "modified_sms_v2.xml"
JSON_PATH = ROOT / "data" / "processed" / "transactions.json"

NUM = r"([\d,]+(?:\.\d+)?)"  # 1,000 or 2000 or 10.5 (unnamed group = the amount)
TS = r"(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})"


def to_num(s):
    """'1,000' -> 1000 (int when whole, else float). None/empty -> None."""
    if s is None:
        return None
    s = s.replace(",", "").strip()
    if not s:
        return None
    return int(s) if re.fullmatch(r"\d+", s) else float(s)


def first(pattern, text):
    m = re.search(pattern, text)
    return m.group(1).strip() if m else None


# (type, regex) - checked in order, first match wins.
PATTERNS = [
    ("received", re.compile(
        rf"You have received {NUM} RWF from (?P<sender>.+?) \((?P<sender_phone>[\d\*]+)\)")),
    ("bank_transfer", re.compile(
        rf"You have transferred {NUM} RWF to (?P<receiver>.+?) \((?P<receiver_phone>\d+)\)")),
    ("bank_deposit", re.compile(rf"A bank deposit of {NUM} RWF")),
    ("withdrawal", re.compile(rf"withdrawn {NUM} RWF from your mobile money account")),
    ("transfer", re.compile(
        rf"^\*165\*S\*{NUM} RWF transferred to (?P<receiver>.+?) \((?P<receiver_phone>\d+)\)")),
    ("merchant_payment", re.compile(
        rf"^\*164\*S\*Y'ello,A transaction of {NUM} RWF by (?P<receiver>.+?) on your MOMO account")),
    ("airtime", re.compile(rf"Your payment of {NUM} RWF to Airtime")),
    ("cash_power", re.compile(rf"Your payment of {NUM} RWF to MTN Cash Power")),
    ("bundle", re.compile(rf"Your payment of {NUM} RWF to Bundles and Packs")),
    ("payment", re.compile(
        rf"Your payment of {NUM} RWF to (?P<receiver>.+?)(?: \d+)? (?:with token|has been completed)")),
    ("failed", re.compile(
        rf"transaction with amount {NUM} RWF for (?P<receiver>.+?) with message")),
    ("bundle_purchase", re.compile(r"^Yello!Umaze kugura .*?igura " + NUM + r" RWF")),
    ("reversal", re.compile(
        rf"Your transaction to (?P<receiver>.+?) \((?P<receiver_phone>\d+)\) with {NUM} RWF has been reversed")),
    ("deposit", re.compile(rf"^\d+\) \d{{4}}-\d{{2}}-\d{{2}} DEPOSIT RWF {NUM} Receiver:")),
    ("otp", re.compile(r"one-time password")),
    ("reversal", re.compile(
        rf"A reversal has been initiated for your transaction to (?P<receiver>.+?) "
        rf"\((?P<receiver_phone>\d+)\) with {NUM} RWF")),
]

FIXED_RECEIVER = {"airtime": "Airtime", "cash_power": "MTN Cash Power",
                  "bundle": "Bundles and Packs", "bundle_purchase": "MTN Bundles"}
OUTGOING = {"transfer", "bank_transfer", "payment", "merchant_payment", "airtime",
            "cash_power", "bundle", "bundle_purchase", "failed", "reversal"}


def extract_fields(body):
    """Pull transaction_type, amount, sender, receiver, fee, balance, tx id, timestamp from body."""
    rec = {"transaction_type": "other", "amount": None, "fee": None, "balance_after": None,
           "sender": None, "receiver": None, "sender_phone": None, "receiver_phone": None,
           "transaction_id": None}

    for ttype, rx in PATTERNS:
        m = rx.search(body)
        if not m:
            continue
        rec["transaction_type"] = ttype
        named_idx = set(rx.groupindex.values())
        amount = next((g for i, g in enumerate(m.groups(), 1)
                       if i not in named_idx and g is not None), None)
        rec["amount"] = to_num(amount)
        gd = m.groupdict()
        rec["sender"], rec["receiver"] = gd.get("sender"), gd.get("receiver")
        rec["sender_phone"], rec["receiver_phone"] = gd.get("sender_phone"), gd.get("receiver_phone")
        break

    t = rec["transaction_type"]
    if t == "received":
        rec["receiver"] = "You"
    elif t in OUTGOING:
        rec["sender"] = "You"
        rec["receiver"] = rec["receiver"] or FIXED_RECEIVER.get(t)
    elif t in ("bank_deposit", "deposit"):
        rec["sender"], rec["receiver"] = "Bank", "You"
    elif t == "withdrawal":
        ag = re.search(r"via agent: (.+?) \((\d+)\)", body)
        rec["sender"] = "You"
        rec["receiver"] = ag.group(1) if ag else "Agent"
        rec["receiver_phone"] = ag.group(2) if ag else None

    rec["fee"] = to_num(first(rf"Fee (?:was|paid):? {NUM} RWF", body))
    rec["balance_after"] = to_num(first(
        rf"(?:[Nn]ew balance|NEW BALANCE)(?:\s*:\s*| is )\s*{NUM} RWF", body))
    if rec["amount"] is not None and rec["fee"] is None:
        rec["fee"] = 0  # SMS states no fee (e.g. money received / deposits)
    rec["transaction_id"] = (first(r"Financial Transaction Id: (\d+)", body)
                             or first(r"TxId:\s*(\d+)", body))
    rec["timestamp"] = first(rf"\bat {TS}", body)
    return rec


def parse(xml_path=XML_PATH):
    """XML -> list of dictionaries (one per <sms>), with key fields extracted from body."""
    records = []
    for i, sms in enumerate(ET.parse(xml_path).getroot().iter("sms"), start=1):
        body = sms.get("body", "")
        rec = {"id": i}
        rec.update(extract_fields(body))
        epoch_ms = int(sms.get("date", 0))
        rec["date_epoch_ms"] = epoch_ms
        if rec["timestamp"] is None:  # SMS with no "at <time>" (e.g. bundle purchases)
            rec["timestamp"] = datetime.fromtimestamp(
                epoch_ms / 1000, tz=timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
        rec["readable_date"] = sms.get("readable_date")
        rec["body"] = body
        records.append(rec)
    return records


def main():
    xml_path = Path(sys.argv[1]) if len(sys.argv) > 1 else XML_PATH
    records = parse(xml_path)
    JSON_PATH.parent.mkdir(parents=True, exist_ok=True)
    with open(JSON_PATH, "w", encoding="utf-8") as f:
        json.dump(records, f, indent=2, ensure_ascii=False)
    other = sum(1 for r in records if r["transaction_type"] == "other")
    print(f"Parsed {len(records)} records -> {JSON_PATH}  (unclassified: {other})")


if __name__ == "__main__":
    main()