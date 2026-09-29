import bisect
import json
import os
import time


ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

JSON_PATH = os.path.join(
    ROOT,
    "data",
    "processed",
    "transactions.json"
)

RESULTS_PATH = os.path.join(
    ROOT,
    "docs",
    "dsa_results.txt"
)


def linear_search(records, target_id):
    """
    Linear Search
    Time complexity: O(n)
    Searches each record from the beginning until the ID is found.
    """
    for record in records:
        if record["id"] == target_id:
            return record

    return None


def dict_lookup(index, target_id):
    """
    Dictionary Lookup
    Average time complexity: O(1)
    Uses the transaction ID as a dictionary key.
    """
    return index.get(target_id)


def binary_search(sorted_ids, records, target_id):
    """
    Binary Search
    Time complexity: O(log n)
    Requires the IDs to be sorted first.
    """
    left = 0
    right = len(sorted_ids) - 1

    while left <= right:
        middle = (left + right) // 2

        if sorted_ids[middle] == target_id:
            return records[middle]

        if sorted_ids[middle] < target_id:
            left = middle + 1
        else:
            right = middle - 1

    return None


def time_method(function, ids, repeats):
    """
    Measure the average time for one lookup.
    Python 3.4 compatible.
    """
    start = time.clock()

    for _ in range(repeats):
        for transaction_id in ids:
            function(transaction_id)

    elapsed = time.clock() - start

    return elapsed / float(repeats * len(ids))


def benchmark(records, label, repeats):
    """
    Compare Linear Search, Dictionary Lookup,
    and Binary Search.
    """

    # Dictionary index: transaction ID -> transaction
    index = {}

    for record in records:
        index[record["id"]] = record

    # Sort records by ID for Binary Search
    ordered = sorted(records, key=lambda record: record["id"])

    sorted_ids = []

    for record in ordered:
        sorted_ids.append(record["id"])

    # IDs to search
    ids = []

    for record in records:
        ids.append(record["id"])

    # Last ID represents the worst case for Linear Search
    worst = ids[-1]

    # Check that all methods return the same record
    for transaction_id in ids:

        linear_result = linear_search(
            records,
            transaction_id
        )

        dictionary_result = dict_lookup(
            index,
            transaction_id
        )

        binary_result = binary_search(
            sorted_ids,
            ordered,
            transaction_id
        )

        assert linear_result is dictionary_result
        assert dictionary_result is binary_result

    # Average lookup times
    linear_time = time_method(
        lambda transaction_id: linear_search(
            records,
            transaction_id
        ),
        ids,
        repeats
    )

    dictionary_time = time_method(
        lambda transaction_id: dict_lookup(
            index,
            transaction_id
        ),
        ids,
        repeats
    )

    binary_time = time_method(
        lambda transaction_id: binary_search(
            sorted_ids,
            ordered,
            transaction_id
        ),
        ids,
        repeats
    )

    # Worst-case lookup times
    linear_worst = time_method(
        lambda transaction_id: linear_search(
            records,
            transaction_id
        ),
        [worst],
        2000
    )

    dictionary_worst = time_method(
        lambda transaction_id: dict_lookup(
            index,
            transaction_id
        ),
        [worst],
        2000
    )

    binary_worst = time_method(
        lambda transaction_id: binary_search(
            sorted_ids,
            ordered,
            transaction_id
        ),
        [worst],
        2000
    )

    results = [
        ("Linear search", linear_time, linear_worst),
        ("Dictionary lookup", dictionary_time, dictionary_worst),
        ("Binary search", binary_time, binary_worst)
    ]

    lines = []

    lines.append(
        "=== {}: {} records (average over every ID, {} pass(es)) ===".format(
            label,
            len(records),
            repeats
        )
    )

    lines.append(
        "{:<20}{:>22}{:>27}{:>20}".format(
            "Method",
            "Avg per lookup (us)",
            "Worst case (us)",
            "Speedup vs linear"
        )
    )

    for name, average_time, worst_time in results:

        speedup = linear_time / average_time

        lines.append(
            "{:<20}{:>22.3f}{:>27.3f}{:>19.1f}x".format(
                name,
                average_time * 1000000,
                worst_time * 1000000,
                speedup
            )
        )

    return "\n".join(lines)


def main():

    # Check that the JSON file exists
    if not os.path.exists(JSON_PATH):
        print("ERROR: transactions.json was not found.")
        print("Expected file: {}".format(JSON_PATH))
        return

    # Load transaction data
    with open(JSON_PATH, "r") as file:
        records = json.load(file)

    print("Loaded {} transaction records.".format(len(records)))
    print("")

    # Make sure we have at least 20 records
    if len(records) < 20:
        print(
            "ERROR: The dataset contains fewer than 20 records."
        )
        return

    # Run benchmark on first 20 records
    small_results = benchmark(
        records[:20],
        "Small set",
        2000
    )

    # Run benchmark on full dataset
    full_results = benchmark(
        records,
        "Full dataset",
        5
    )

    final_results = small_results + "\n\n" + full_results

    print(final_results)

    # Create docs directory if necessary
    docs_directory = os.path.dirname(RESULTS_PATH)

    if not os.path.exists(docs_directory):
        os.makedirs(docs_directory)

    # Save benchmark results
    with open(RESULTS_PATH, "w") as file:
        file.write(final_results + "\n")

    print("")
    print(
        "Saved DSA results to {}".format(RESULTS_PATH)
    )


if __name__ == "__main__":
    main()
