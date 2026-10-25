
import subprocess
import json
import sys


def run_test(name, logs, expected_flagged,
             expected_invalid, expected_severities):

    try:
        result = subprocess.run(
            ["threatlens.exe", "--json"],
            input=logs,
            capture_output=True,
            text=True,
            timeout=10
        )
    except FileNotFoundError:
        print("ERROR: threatlens.exe not found.")
        print("Compile main.cpp first:")
        print("g++ main.cpp -o threatlens.exe")
        sys.exit(1)
    except subprocess.TimeoutExpired:
        print(name + ": FAIL - Engine timed out")
        return False

    if result.returncode != 0:
        print(name + ": FAIL - Engine error")
        print(result.stderr)
        return False

    try:
        data = json.loads(result.stdout)
    except json.JSONDecodeError:
        print(name + ": FAIL - Invalid JSON output")
        print(result.stdout)
        return False

    if "metrics" not in data or "detections" not in data:
        print(name + ": FAIL - Missing JSON fields")
        return False

    actual_flagged = data["metrics"]["flagged_accounts"]
    actual_invalid = data["metrics"]["invalid_records"]

    actual_severities = sorted(
        item["severity"] for item in data["detections"]
    )

    expected_severities = sorted(expected_severities)

    passed = (
        actual_flagged == expected_flagged
        and actual_invalid == expected_invalid
        and actual_severities == expected_severities
        and len(data["detections"]) == expected_flagged
    )

    if passed:
        print(name + ": PASS")
    else:
        print(name + ": FAIL")
        print("Expected flagged:", expected_flagged)
        print("Actual flagged:", actual_flagged)
        print("Expected invalid:", expected_invalid)
        print("Actual invalid:", actual_invalid)
        print("Expected severities:", expected_severities)
        print("Actual severities:", actual_severities)

    return passed


def main():
    tests = [
        (
            "Three consecutive failures",
            "alice 0\nalice 0\nalice 0\n",
            1, 0, ["HIGH"]
        ),
        (
            "Successful login resets streak",
            "bob 0\nbob 0\nbob 1\n",
            0, 0, []
        ),
        (
            "Invalid records are counted",
            "alice 0\nbob 2\ncharlie 1 extra\n",
            0, 2, []
        ),
        (
            "Five failures trigger HIGH severity",
            "david 0\ndavid 0\ndavid 0\ndavid 0\ndavid 0\n",
            1, 0, ["HIGH"]
        ),
        (
            "Two failures are not flagged",
            "emma 0\nemma 0\n",
            0, 0, []
        ),
        (
            "Medium severity detection",
            "frank 0\nfrank 0\nfrank 1\nfrank 0\n",
            1, 0, ["MEDIUM"]
        ),
        (
            "Mixed HIGH and MEDIUM detections",
            "grace 0\ngrace 0\ngrace 0\n"
            "henry 0\nhenry 0\nhenry 1\nhenry 0\n",
            2, 0, ["HIGH", "MEDIUM"]
        ),
        (
            "Empty input",
            "",
            0, 0, []
        ),
        (
            "Blank lines are ignored",
            "\n  \n\t\n",
            0, 0, []
        ),
        (
            "Invalid username is rejected",
            "bad$user 0\n",
            0, 1, []
        ),
        (
            "Success-only account is not flagged",
            "ivy 1\nivy 1\nivy 1\n",
            0, 0, []
        ),
        (
            "Repeated failures separated by successes",
            "jack 0\njack 1\njack 0\njack 1\njack 0\n",
            1, 0, ["MEDIUM"]
        )
    ]

    passed_count = 0

    print("\nTHREATLENS AUTOMATED TEST SUITE")
    print("=" * 35)

    for test in tests:
        if run_test(*test):
            passed_count += 1

    total = len(tests)

    print("=" * 35)
    print(f"Results: {passed_count}/{total} tests passed")

    if passed_count == total:
        print("Overall result: ALL TESTS PASSED")
        sys.exit(0)
    else:
        print("Overall result: SOME TESTS FAILED")
        sys.exit(1)


if __name__ == "__main__":
    main()
