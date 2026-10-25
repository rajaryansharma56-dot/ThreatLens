# ThreatLens — Login Security Analyzer

**A lightweight, rule-based authentication log analyzer built with C++, Python, and a web dashboard.**

ThreatLens analyzes login outcomes, identifies repeated authentication failures, and highlights accounts that may require further investigation. It combines a C++ detection engine with a Python HTTP server and a browser-based dashboard.

> **Project status:** Educational cybersecurity prototype. Detection is rule-based; results are indicators for investigation, not proof of an attack.

---

## Overview

Authentication logs can reveal suspicious patterns, such as repeated failed login attempts against the same account. ThreatLens processes login-result records and applies configurable-style threshold rules to flag potentially suspicious activity.

The project demonstrates how a native C++ program can work with a Python backend and a web interface to create a small, locally running security-analysis tool.

## Features

- **Authentication log analysis** — processes username and login-result records.
- **Repeated-failure detection** — flags accounts with repeated failed attempts or consecutive failure streaks.
- **Severity classification** — assigns `MEDIUM` or `HIGH` severity based on the implemented thresholds.
- **Web dashboard** — presents analysis metrics and visual summaries.
- **JSON and CSV exports** — supports exporting analysis results.
- **Local execution** — the Python server runs on the local machine and communicates with the C++ engine.
- **Simple architecture** — separates detection logic, backend communication, and frontend presentation.

## Tech Stack

| Component | Technology |
|---|---|
| Detection engine | C++ |
| Backend server | Python |
| Frontend | HTML, CSS, JavaScript |
| Data exchange | JSON |
| Export formats | JSON, CSV |
| Development environment | Windows, Git, GitHub |

## Project Architecture

```text
ThreatLens/
├── main.cpp             # C++ log-analysis engine
├── server.py            # Python HTTP server and API
├── web/
│   ├── index.html       # Dashboard structure
│   ├── style.css        # Dashboard styling
│   └── script.js        # Frontend interactions
├── README.md
├── .gitignore
├── threatlens.exe       # Locally compiled executable
└── login_logs.txt       # Local test input
```

`threatlens.exe` and `login_logs.txt` are local runtime files and may not be included in the Git repository. Build the executable and create a test log locally before running the complete application.

## How Detection Works

ThreatLens evaluates the login outcomes recorded for each username.

### Input format

Each record contains a username followed by a numeric result:

```text
alice 0
alice 0
alice 1
bob 1
bob 0
```

- `0` — failed login
- `1` — successful login

The input format does not include timestamps, so the analyzer cannot reconstruct real event times or a true time-based attack timeline.

### Detection rules

An account is flagged when either of the following conditions is met:

- **Repeated failures:** at least 3 failed login attempts in total.
- **Consecutive failures:** a streak of at least 3 consecutive failed attempts.

The implemented severity rules are:

| Severity | Condition |
|---|---|
| `HIGH` | At least 3 consecutive failures, or at least 5 total failed attempts |
| `MEDIUM` | The account is flagged but does not meet the `HIGH` threshold |

These are simple heuristic rules intended for demonstration. They do not establish malicious intent, and legitimate users can also generate repeated failures.

## Getting Started

### Prerequisites

- Windows
- A C++ compiler such as `g++` (MinGW-w64)
- Python 3
- A modern web browser
- Git, if cloning the repository

### 1. Clone the repository

```bash
git clone https://github.com/rajaryansharma56-dot/ThreatLens.git
cd ThreatLens
```

### 2. Compile the C++ engine

If you have `g++` installed, compile the engine from the project root:

```bash
g++ main.cpp -o threatlens.exe
```

Make sure the compiler is available in your system's `PATH`.

### 3. Prepare a test log

Create a local file named `login_logs.txt` in the project root and add synthetic records, for example:

```text
alice 0
alice 0
alice 0
alice 1
bob 1
charlie 0
charlie 0
charlie 0
charlie 0
charlie 0
```

Use synthetic data for testing. Do not upload real authentication logs or sensitive account information to a public repository.

### 4. Start the Python server

```bash
python server.py
```

The server is configured to run locally at:

```text
http://127.0.0.1:8000
```

Open this address in your browser to access the dashboard.

> Keep the server terminal open while using the dashboard. Stop the server with `Ctrl+C` when finished.

### 5. Run the analysis

Use the dashboard's log-analysis controls to process the prepared input. Review the resulting metrics and severity classifications, then try the available JSON and CSV export options.

**Note:** The steps above describe the intended local workflow. Successful execution depends on the current implementation, compiler setup, and available input files.

## API Endpoints

The Python backend exposes the following local endpoints:

| Endpoint | Purpose |
|---|---|
| `/api/status` | Reports backend and C++ engine availability |
| `/api/analyze` | Runs or requests log analysis |

The server uses the C++ executable for analysis and returns data to the web dashboard. Refer to `server.py` for the exact request methods, parameters, and response structure.

## Testing Checklist

Use synthetic test records to verify the main behaviors.

- [ ] The server starts and reports whether the C++ engine is available.
- [ ] The dashboard loads in a browser.
- [ ] A successful login record is processed correctly.
- [ ] Three failed attempts for one account trigger a flag.
- [ ] Three consecutive failures trigger `HIGH` severity.
- [ ] Five total failures trigger `HIGH` severity.
- [ ] JSON export produces valid output.
- [ ] CSV export produces the expected records.
- [ ] Invalid or unexpected input is handled safely.

These checks are a suggested validation plan; mark them complete only after testing the current version.

## Security and Limitations

ThreatLens is a learning project and is **not a production security monitoring system**.

- **Rule-based detection:** no machine-learning model or advanced behavioral analysis is implemented.
- **No timestamps:** input records lack event times, limiting temporal analysis.
- **Potential false positives:** repeated failures can result from typing mistakes, expired credentials, or legitimate account activity.
- **Input validation:** production use would require stronger validation and robust error handling.
- **Local demonstration:** the server is intended for local use, not exposure to an untrusted network.
- **Sensitive data:** use synthetic records and avoid committing credentials, personal information, or real login logs.
- **No incident attribution:** flags identify patterns that merit review; they do not identify an attacker.

## Future Improvements

Potential next steps include:

- Timestamp-aware log processing and time-window analysis
- Configurable detection thresholds
- More comprehensive input validation and automated tests
- Improved reporting and investigation summaries
- Additional detection rules and anomaly analysis
- Authentication, access controls, and deployment hardening before any broader use

## Learning Objectives

This project explores:

- File processing and rule-based detection in C++
- Communication between a native executable and a Python backend
- HTTP endpoints and JSON data exchange
- Frontend dashboard development
- Data export and basic cybersecurity log analysis
- Version control and project documentation with Git and GitHub

## Author

**Raj Aryan Sharma**

Electronics & Instrumentation Engineering student interested in C++, software development, electronics, and cybersecurity.

- GitHub: [@rajaryansharma56-dot](https://github.com/rajaryansharma56-dot)
- Project repository: [ThreatLens](https://github.com/rajaryansharma56-dot/ThreatLens)

## License

No license has been specified yet. Until a license is added to the repository, do not assume that others have permission to redistribute or reuse this project's code.
