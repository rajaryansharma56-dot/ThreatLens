# ThreatLens

**A local, rule-based login-log analyzer built with C++, Python, and a
web dashboard.**

ThreatLens reads authentication log records, validates their format,
summarizes login activity, and flags accounts that meet configurable
failure-pattern rules. A browser dashboard presents the results and
supports JSON and CSV report downloads.

> **Project status:** The core workflow has previously been reported as
> working during development. The latest end-to-end checks have not yet
> been confirmed, so verify the checklist in this README before
> describing every feature as tested.

## Features

-   **C++ analysis engine** for parsing and analyzing login records.
-   **Python local backend** that serves the dashboard and forwards logs
    to the C++ executable.
-   **Web dashboard** for summary metrics and flagged-account results.
-   **Input validation** for usernames and record result values.
-   **Detection rules** based on repeated failed login attempts.
-   **Severity labels** (`HIGH` and `MEDIUM`) for flagged accounts.
-   **JSON and CSV exports** for analysis results.
-   **Login activity visualization** comparing successful and failed
    records, when the chart feature is present in the current frontend.
-   **Local-only default binding** to `127.0.0.1`.

## Technology stack

-   C++ --- log parsing, validation, metrics, and detection rules.
-   Python --- local HTTP backend and communication with the C++ engine.
-   HTML, CSS, JavaScript --- dashboard interface and report downloads.

## Project structure

The expected project layout is:

``` text
ThreatLens/
├── main.cpp
├── server.py
├── login_logs.txt
├── threatlens.exe
└── web/
    ├── index.html
    ├── style.css
    └── script.js
```

`threatlens.exe` is the compiled C++ executable. It may need to be
rebuilt if `main.cpp` changes or if the executable is missing.

## Log format

Each non-empty record is expected to contain a username followed by a
result value:

``` text
username result
```

The result value is:

-   `0` --- failed login
-   `1` --- successful login

Example:

``` text
raj 0
raj 0
raj 1
dev 0
dev 0
guest 1
```

The current format does **not** contain timestamps, IP addresses, device
identifiers, or geolocation. Consequently, the activity chart can
compare totals but cannot truthfully show a timeline or identify the
source of a login attempt.

## Validation and detection rules

The current implementation was described as using these rules:

-   Usernames may contain letters, digits, underscores, hyphens, and
    dots.
-   Usernames are limited to 64 characters.
-   Result values are expected to be `0` or `1`.
-   Malformed records are counted as invalid rather than treated as
    valid login attempts.
-   An account is flagged when it has at least 3 total failed logins or
    a longest consecutive failure streak of at least 3.
-   A flagged account is labeled `HIGH` when its longest consecutive
    failure streak is at least 3, or its total failed logins are at
    least 5. Other flagged accounts are labeled `MEDIUM`.

These are demonstration rules, not universal indicators of malicious
activity. A legitimate user who mistypes a password may be flagged, and
a real attack may not match these rules.

## Run locally on Windows

1.  Open the `ThreatLens` project folder.

2.  Ensure `threatlens.exe` has been compiled from `main.cpp`.

3.  Start the Python backend from the project folder. For example, if
    `server.py` uses Python 3:

    ``` powershell
    python server.py
    ```

4.  Keep the terminal running.

5.  Open this address in your browser:

    ``` text
    http://127.0.0.1:8000/
    ```

6.  Select `login_logs.txt` in the dashboard and choose **Analyze
    Logs**.

7.  Review the metrics and flagged-account table, then test the JSON and
    CSV report buttons.

If the server does not start, check that Python is installed and that
port `8000` is not already in use. If the dashboard says the C++ engine
is unavailable, check that `threatlens.exe` exists in the expected
project folder and that `server.py` can execute it.

The exact compiler command and any build dependencies should be
documented after checking the current `main.cpp` and `server.py`; they
are intentionally not guessed here.

## Example test plan

Before presenting or publishing the project, test each case and record
the actual result.

  -----------------------------------------------------------------------
  Test                                Expected behavior
  ----------------------------------- -----------------------------------
  Valid successful record (`user 1`)  Successful-login count increases

  Valid failed record (`user 0`)      Failed-login count increases

  Invalid result value (for example,  Record is counted as invalid
  `user 2`)                           

  Invalid username characters         Record is rejected or counted as
                                      invalid

  Three consecutive failures for one  Account is flagged and marked
  account                             `HIGH`

  Three failures separated by a       Account can be flagged by total
  success                             failures; severity depends on the
                                      total

  No flagged accounts                 Table shows a clear empty state

  JSON export                         A JSON report downloads and can be
                                      opened

  CSV export                          A CSV report downloads and can be
                                      opened

  Missing executable                  Backend/dashboard reports that the
                                      C++ engine is unavailable

  Empty log file                      Dashboard handles the result
                                      without crashing
  -----------------------------------------------------------------------

### Previously used sample expectations

During development, `login_logs.txt` was reported to produce:

-   11 total records
-   2 successful logins
-   7 failed logins
-   2 invalid records
-   2 flagged accounts: `raj` (`HIGH`) and `dev` (`MEDIUM`)

These figures apply only if the local sample file still contains the
same records and the current engine follows the described rules. Re-run
the analysis to confirm them.

## Reports

The dashboard is intended to provide:

-   `threatlens-report.json` --- the complete analysis response plus
    report metadata.
-   `threatlens-detections.csv` --- a spreadsheet-friendly table of
    flagged accounts.

Confirm both downloads and inspect the generated files before marking
report export as tested.

## Security, privacy, and limitations

-   ThreatLens is a **local educational/portfolio demonstration**, not a
    production security monitoring platform.
-   Its rules are simple heuristics and can produce false positives and
    false negatives.
-   The sample log format has no timestamps, so the application cannot
    calculate time-based trends.
-   Do not upload real credentials, passwords, session tokens, or
    sensitive production logs into a demonstration project.
-   The local server is expected to bind to `127.0.0.1`; do not expose
    it publicly without adding appropriate authentication, access
    controls, input limits, and security review.
-   The current analyzer should not be described as AI-powered unless a
    real machine-learning component is added and evaluated.

## Future improvements

Possible future work, after the core version is tested:

-   Add timestamps and source metadata to the log format.
-   Add unit tests for the C++ parsing and detection rules.
-   Add automated backend/API tests.
-   Make the C++ build reproducible with a documented build script.
-   Add configurable detection thresholds.
-   Improve accessibility and responsive layout.
-   Add screenshots of the actual running application.
-   Add a clearly documented test-results section based on observed
    results.

## Verification checklist

-   [ ] Dashboard opens at `http://127.0.0.1:8000/`
-   [ ] C++ engine status reports connected
-   [ ] A valid log file can be analyzed
-   [ ] Successful, failed, and invalid counts match the test data
-   [ ] Severity counts match the detections
-   [ ] Login activity chart reflects the actual counts, if present
-   [ ] JSON report downloads and opens
-   [ ] CSV report downloads and opens
-   [ ] Empty and malformed log files are handled safely
-   [ ] README instructions match the actual project files

## License

No license is specified yet. Add a license file only after choosing a
license appropriate for how you want others to use the project.
