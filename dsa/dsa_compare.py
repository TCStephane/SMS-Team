import bisect
import json
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
JSON_PATH = ROOT / "data" / "processed" / "transactions.json"
RESULTS_PATH = ROOT / "docs" / "dsa_results.txt"


def linear_search(records, target_id):
    """O(n): scan the list until the id matches."""
    for rec in records:
        if rec["id"] == target_id:
            return rec
    return None


def dict_lookup(index, target_id):
    """O(1) average: hash the key and jump straight to the record."""
    return index.get(target_id)


def binary_search(sorted_ids, records, target_id):
    """O(log n): needs a list sorted by id (bonus method)."""
    i = bisect.bisect_left(sorted_ids, target_id)
    if i < len(sorted_ids) and sorted_ids[i] == target_id:
        return records[i]
    return None


def time_method(fn, ids, repeats):
    """Average seconds per lookup over `repeats` passes across all ids."""
    start = time.perf_counter()
    for _ in range(repeats):
        for tid in ids:
            fn(tid)
    return (time.perf_counter() - start) / (repeats * len(ids))


def benchmark(records, label, repeats):
    index = {r["id"]: r for r in records}
    ordered = sorted(records, key=lambda r: r["id"])
    sorted_ids = [r["id"] for r in ordered]
    ids = [r["id"] for r in records]
    worst = ids[-1]  # last record = worst case for linear search

    # correctness check: all three methods must agree
    for tid in ids:
        assert linear_search(records, tid) is dict_lookup(index, tid) \
            is binary_search(sorted_ids, ordered, tid)

    rows = {
        "Linear search": time_method(lambda t: linear_search(records, t), ids, repeats),
        "Dictionary lookup": time_method(lambda t: dict_lookup(index, t), ids, repeats),
        "Binary search": time_method(lambda t: binary_search(sorted_ids, ordered, t), ids, repeats),
    }
    worst_case = {
        "Linear search": time_method(lambda t: linear_search(records, worst), [worst], 2000),
        "Dictionary lookup": time_method(lambda t: dict_lookup(index, worst), [worst], 2000),
        "Binary search": time_method(lambda t: binary_search(sorted_ids, ordered, worst), [worst], 2000),
    }
    lin = rows["Linear search"]
    lines = [f"=== {label}: {len(records)} records (avg over every id, {repeats} pass(es)) ===",
             f"{'Method':<20}{'Avg per lookup (us)':>22}{'Worst case, last id (us)':>27}{'Speedup vs linear':>20}"]
    for name, t in rows.items():
        lines.append(f"{name:<20}{t * 1e6:>22.3f}{worst_case[name] * 1e6:>27.3f}{lin / t:>19.1f}x")
    return "\n".join(lines)


def main():
    with open(JSON_PATH, encoding="utf-8") as f:
        records = json.load(f)
    out = [benchmark(records[:20], "Small set", repeats=2000), "",
           benchmark(records, "Full dataset", repeats=5)]
    text = "\n".join(out)
    print(text)
    RESULTS_PATH.parent.mkdir(parents=True, exist_ok=True)
    RESULTS_PATH.write_text(text + "\n", encoding="utf-8")
    print(f"\nSaved to {RESULTS_PATH}")


if __name__ == "__main__":
    main()