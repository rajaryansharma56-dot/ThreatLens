
import subprocess
import json


def run_test(name, logs, expected_flagged, expected_invalid):
    result = subprocess.run(
        ["threatlens.exe", "--json"],
        input=logs,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        print(name + ": FAIL")
        print("Engine error:", result.stderr)
        return

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(name + ": FAIL")
        print("Invalid JSON output:", result.stdout)
        return

    actual_flagged = data["metrics"]["flagged_accounts"]
    actual_invalid = data["metrics"]["invalid_records"]

    if (actual_flagged == expected_flagged and
            actual_invalid == expected_invalid):
        print(name + ": PASS")
    else:
        print(name + ": FAIL")
        print("Expected flagged:", expected_flagged)
        print("Actual flagged:", actual_flagged)
        print("Expected invalid:", expected_invalid)
        print("Actual invalid:", actual_invalid)


# Test 1: Three consecutive failures should flag the account.
run_test(
    "Three consecutive failures",
    "alice 0\nalice 0\nalice 0\n",
    1,
    0
)

# Test 2: A success resets the streak.
# Only two failures occur, so the account should not be flagged.
run_test(
    "Successful login resets streak",
    "bob 0\nbob 0\nbob 1\n",
    0,
    0
)

# Test 3: Invalid records should be counted.
run_test(
    "Invalid records are counted",
    "alice 0\nbob 2\ncharlie 1 extra\n",
    0,
    2
)

# Test 4: Five failures should flag the account.
run_test(
    "Five failures trigger detection",
    "david 0\ndavid 0\ndavid 0\ndavid 0\ndavid 0\n",
    1,
    0
)
