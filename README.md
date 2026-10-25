# ThreatLens
### Rule-Based Authentication Log Analyzer

ThreatLens is a lightweight security analysis project that examines authentication logs, identifies suspicious login-failure patterns, and classifies flagged accounts according to configurable detection rules.

Built with **C++, Python, HTML, CSS, and JavaScript**, ThreatLens combines a rule-based detection engine with a web dashboard for analyzing results and exporting reports.

## Overview

Repeated authentication failures can indicate suspicious account activity. ThreatLens demonstrates how login records can be processed using simple detection rules to highlight accounts that may require further investigation.

The project is designed as an educational cybersecurity prototype, demonstrating log processing, rule-based detection, backend integration, and dashboard development.

## Features

- **Authentication Log Analysis** — Processes login records to calculate failed attempts and consecutive failure streaks.
- **Suspicious Account Detection** — Flags accounts that meet configured failure thresholds.
- **Severity Classification** — Assigns HIGH or MEDIUM severity according to the configured rules.
- **Web Dashboard** — Displays analyzed records, suspicious accounts, detection reasons, and severity levels.
- **Report Export** — Supports downloading analysis results in JSON and CSV formats.
- **Sample Dataset** — Includes synthetic authentication records for testing.
- **C++ and Python Integration** — Uses a C++ detection engine connected to a Python backend and browser-based interface.

## Technology Stack

| Technology | Purpose |
|---|---|
| C++ | Authentication log analysis and detection rules |
| Python | Backend server and engine integration |
| HTML | Dashboard structure |
| CSS | Dashboard styling |
| JavaScript | Dashboard interactions and data presentation |
| JSON | Structured analysis results |
| CSV | Tabular report export |

## How Detection Works

ThreatLens evaluates login records using configurable rules based on failed login attempts and consecutive failure streaks.

| Condition | Detection behavior |
|---|---|
| 3 or more failed attempts | Account is flagged |
| 3 or more consecutive failures | Account is flagged |
| 5 or more total failures | HIGH severity |
| 3 or more consecutive failures | HIGH severity |
| Other flagged cases | MEDIUM severity |

The implementation's configured thresholds determine the result. A flagged account is not proof of a successful attack; it is an indicator for further investigation.

## Project Structure

```text
ThreatLens/
├── main.cpp
├── server.py
├── README.md
├── LICENSE
├── .gitignore
├── sample_logs.txt
└── web/
    ├── index.html
    ├── style.css
    └── script.js
```

- `main.cpp` — C++ detection engine.
- `server.py` — Python backend server and engine integration.
- `sample_logs.txt` — Synthetic test authentication records.
- `web/index.html` — Dashboard interface.
- `web/style.css` — Dashboard presentation.
- `web/script.js` — Dashboard behavior and data handling.
- `.gitignore` — Excludes selected generated and local runtime files.

## Getting Started

### Prerequisites

- Python 3
- A C++ compiler that supports the project's source code
- A modern web browser
- A terminal or command prompt

### 1. Clone the repository

```bash
git clone https://github.com/rajaryansharma56-dot/ThreatLens.git
cd ThreatLens
```

### 2. Compile the C++ engine

On Windows, using a compiler such as g++:

```bash
g++ main.cpp -o threatlens.exe
```

### 3. Start the backend

Run:

```bash
python server.py
```

### 4. Open the dashboard

Visit:

http://127.0.0.1:8000

Keep the backend running while using the dashboard.

*Note: These instructions reflect the project's current local setup. Compiler availability and any additional dependencies required by the source code may vary by environment.*

## Sample Test Results

ThreatLens was tested with **11 synthetic authentication log records**.

| Metric | Verified result |
|---|---:|
| Records analyzed | 11 |
| Suspicious accounts detected | 2 |
| HIGH-severity detections | 2 |
| MEDIUM-severity detections | 0 |

### Detected Accounts

| Username | Failed logins | Consecutive failures | Severity |
|---|---:|---:|---|
| alice | 3 | 3 | HIGH |
| charlie | 5 | 5 | HIGH |

The sample test also confirmed that the JSON and CSV report downloads work.

These results demonstrate the configured rules against the sample dataset; they are not a benchmark of detection accuracy against real-world attacks.

## Security and Limitations

- ThreatLens uses rule-based detection rather than a trained machine-learning model.
- Its findings depend on the input records and configured thresholds.
- The current input format represents a username and login result, where `0` indicates failure and `1` indicates success.
- The current prototype does not establish a real-time authentication monitoring pipeline.
- Detection results should be treated as indicators, not definitive proof of malicious activity.
- This project is intended for learning and experimentation, not production security monitoring.

Use synthetic or properly authorized data when testing the application. Do not commit passwords, secrets, or sensitive authentication logs to a public repository.

## Future Improvements

Potential enhancements include:

- Timestamp-aware event analysis and detection timelines.
- Additional detection rules and configurable thresholds.
- Improved input validation and error handling.
- Automated tests for detection rules and edge cases.
- More detailed reports and dashboard visualizations.
- Integration with authorized log sources for controlled monitoring experiments.

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE) for details.

## Author

**Raj Aryan Sharma**

GitHub: [@rajaryansharma56-dot](https://github.com/rajaryansharma56-dot)

---

*ThreatLens — Turning authentication logs into actionable security indicators.*
