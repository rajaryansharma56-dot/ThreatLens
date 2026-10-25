
const fileInput = document.getElementById("logFile");
const analyzeButton = document.getElementById("analyzeButton");
const fileStatus = document.getElementById("fileStatus");

const uploadZone = document.getElementById("uploadZone");
const selectedFile = document.getElementById("selectedFile");
const selectedFileName = document.getElementById("selectedFileName");
const selectedFileSize = document.getElementById("selectedFileSize");
const analyzeButtonText = document.getElementById("analyzeButtonText");

const engineStatus = document.getElementById("engineStatus");
const engineStatusDot = document.getElementById("engineStatusDot");
const engineStatusText = document.getElementById("engineStatusText");
const sidebarStatusDot = document.getElementById("sidebarStatusDot");
const sidebarStatusText = document.getElementById("sidebarStatusText");

const reportCount = document.getElementById("reportCount");
const recordsAnalyzed = document.getElementById("recordsAnalyzed");

const MAX_FILE_SIZE = 1_000_000;

let isAnalyzing = false;
let lastAnalysisResult = null;
let lastAnalyzedFile = "";

function setEngineStatus(connected) {
    engineStatus.classList.toggle("connected", connected);
    engineStatus.classList.toggle("disconnected", !connected);
    engineStatusDot.classList.toggle("online", connected);
    sidebarStatusDot.classList.toggle("online", connected);

    engineStatusText.textContent = connected
        ? "C++ ENGINE CONNECTED"
        : "ENGINE NOT CONNECTED";

    sidebarStatusText.textContent = connected
        ? "ENGINE ONLINE"
        : "ENGINE OFFLINE";
}

async function checkEngineStatus() {
    try {
        const response = await fetch("/api/status", {
            cache: "no-store"
        });

        if (!response.ok) {
            throw new Error("Backend unavailable");
        }

        const data = await response.json();

        setEngineStatus(
            data.status === "backend_running" &&
            data.cpp_engine_available === true
        );
    } catch (error) {
        setEngineStatus(false);
    }
}

function formatFileSize(bytes) {
    if (bytes < 1024) return bytes + " B";
    return (bytes / 1024).toFixed(1) + " KB";
}

function showSelectedFile() {
    const file = fileInput.files[0];

    if (!file) {
        selectedFile.hidden = true;
        return;
    }

    selectedFileName.textContent = file.name;
    selectedFileSize.textContent = formatFileSize(file.size);
    selectedFile.hidden = false;
    fileStatus.textContent = "File selected. Ready for analysis.";
}

fileInput.addEventListener("change", showSelectedFile);

uploadZone.addEventListener("dragover", function (event) {
    event.preventDefault();
    uploadZone.classList.add("drag-over");
});

uploadZone.addEventListener("dragleave", function () {
    uploadZone.classList.remove("drag-over");
});

uploadZone.addEventListener("drop", function (event) {
    event.preventDefault();
    uploadZone.classList.remove("drag-over");

    const file = event.dataTransfer.files[0];
    if (!file) return;

    const transfer = new DataTransfer();
    transfer.items.add(file);
    fileInput.files = transfer.files;

    showSelectedFile();
});

analyzeButton.addEventListener("click", analyzeLogs);

async function analyzeLogs() {
    if (isAnalyzing) return;

    const file = fileInput.files[0];

    if (!file) {
        fileStatus.textContent = "Please select a log file first.";
        return;
    }

    if (file.size > MAX_FILE_SIZE) {
        fileStatus.textContent = "File exceeds the 1 MB size limit.";
        return;
    }

    isAnalyzing = true;
    analyzeButton.disabled = true;
    analyzeButtonText.textContent = "Analyzing...";
    fileStatus.textContent = "Sending log data to the C++ engine...";

    try {
        const content = await file.text();

        const response = await fetch("/api/analyze", {
            method: "POST",
            headers: {
                "Content-Type": "text/plain; charset=utf-8"
            },
            body: content
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Analysis request failed.");
        }

        if (
            data.success !== true ||
            !data.metrics ||
            !Array.isArray(data.detections)
        ) {
            throw new Error("Unexpected analysis response.");
        }

        displayResults(data);

        lastAnalysisResult = data;
        lastAnalyzedFile = file.name;

        fileStatus.textContent =
            "Analysis complete: " + file.name +
            " | Processed by the C++ engine";

        setEngineStatus(true);
    } catch (error) {
        fileStatus.textContent = "Analysis failed: " + error.message;
    } finally {
        isAnalyzing = false;
        analyzeButton.disabled = false;
        analyzeButtonText.textContent = "Analyze Logs";
    }
}

function displayResults(data) {
    const metrics = data.metrics;
    const detections = data.detections;

    document.getElementById("successCount").textContent =
        metrics.successful_logins ?? 0;

    document.getElementById("failedCount").textContent =
        metrics.failed_logins ?? 0;

    document.getElementById("invalidCount").textContent =
        metrics.invalid_records ?? 0;

    document.getElementById("flaggedCount").textContent =
        metrics.flagged_accounts ?? detections.length;

    reportCount.textContent =
        detections.length + " DETECTION" +
        (detections.length === 1 ? "" : "S");

    recordsAnalyzed.textContent =
        (metrics.records_analyzed ?? 0) + " RECORDS ANALYZED";

    updateSeveritySummary(detections);
    updateLoginActivityChart(metrics);

    const table = document.getElementById("suspiciousTable");
    table.replaceChildren();

    if (detections.length === 0) {
        const row = document.createElement("tr");
        const cell = document.createElement("td");

        cell.colSpan = 5;
        cell.className = "empty-state";
        cell.textContent = "No suspicious accounts detected.";

        row.appendChild(cell);
        table.appendChild(row);
        return;
    }

    for (const detection of detections) {
        const row = document.createElement("tr");

        const usernameCell = document.createElement("td");
        usernameCell.textContent = detection.username ?? "Unknown";

        const attemptsCell = document.createElement("td");
        attemptsCell.textContent = detection.failed_logins ?? 0;

        const streakCell = document.createElement("td");
        streakCell.textContent =
            detection.longest_failure_streak ?? "N/A";

        const reasonCell = document.createElement("td");
        reasonCell.textContent =
            detection.detection_reason ?? "No reason provided";

        const severityCell = document.createElement("td");
        const severity =
            String(detection.severity ?? "UNKNOWN").toUpperCase();

        severityCell.textContent = severity;

        severityCell.classList.add(
            severity === "HIGH"
                ? "severity-high"
                : severity === "MEDIUM"
                    ? "severity-medium"
                    : "severity-unknown"
        );

        row.append(
            usernameCell,
            attemptsCell,
            streakCell,
            reasonCell,
            severityCell
        );

        table.appendChild(row);
    }
}

function updateSeveritySummary(detections) {
    let highCount = 0;
    let mediumCount = 0;
    let otherCount = 0;

    for (const detection of detections) {
        const severity =
            String(detection.severity ?? "UNKNOWN").toUpperCase();

        if (severity === "HIGH") {
            highCount++;
        } else if (severity === "MEDIUM") {
            mediumCount++;
        } else {
            otherCount++;
        }
    }

    document.getElementById("highSeverityCount").textContent = highCount;
    document.getElementById("mediumSeverityCount").textContent = mediumCount;
    document.getElementById("otherSeverityCount").textContent = otherCount;
}

function updateLoginActivityChart(metrics) {
    const chart = document.getElementById("loginActivityChart");

    if (!chart) return;

    const successful = Math.max(
        0,
        Number(metrics.successful_logins) || 0
    );

    const failed = Math.max(
        0,
        Number(metrics.failed_logins) || 0
    );

    const total = successful + failed;

    chart.replaceChildren();

    if (total === 0) {
        const message = document.createElement("p");
        message.className = "chart-empty-state";
        message.textContent = "No valid login activity to display.";
        chart.appendChild(message);
        return;
    }

    const entries = [
        {
            label: "Successful logins",
            value: successful,
            color: "#36d399"
        },
        {
            label: "Failed logins",
            value: failed,
            color: "#ff657a"
        }
    ];

    for (const entry of entries) {
        const item = document.createElement("div");
        item.className = "activity-bar-item";

        const heading = document.createElement("div");
        heading.className = "activity-bar-heading";

        const label = document.createElement("span");
        label.textContent = entry.label;

        const value = document.createElement("strong");
        value.textContent =
            entry.value + " (" +
            ((entry.value / total) * 100).toFixed(1) + "%)";

        heading.append(label, value);

        const track = document.createElement("div");
        track.className = "activity-bar-track";
        track.setAttribute("role", "img");
        track.setAttribute(
            "aria-label",
            entry.label + ": " + entry.value + " records"
        );

        const bar = document.createElement("div");
        bar.className = "activity-bar-fill";
        bar.style.width = (entry.value / total * 100) + "%";
        bar.style.backgroundColor = entry.color;

        track.appendChild(bar);
        item.append(heading, track);
        chart.appendChild(item);
    }

    const note = document.createElement("p");
    note.className = "chart-footnote";
    note.textContent =
        "Based on valid login records in the selected file. " +
        "Invalid records are excluded; this is not a time-series chart.";

    chart.appendChild(note);
}

function downloadBlob(blob, filename) {
    const url = URL.createObjectURL(blob);
    const link = document.createElement("a");

    link.href = url;
    link.download = filename;

    document.body.appendChild(link);
    link.click();
    link.remove();

    setTimeout(function () {
        URL.revokeObjectURL(url);
    }, 1000);
}

function downloadAnalysisReport() {
    if (!lastAnalysisResult) {
        fileStatus.textContent =
            "Analyze a log file before downloading a report.";
        return;
    }

    const report = {
        project: "ThreatLens",
        version: "1.0",
        generatedAt: new Date().toISOString(),
        sourceFile: lastAnalyzedFile,
        analysis: lastAnalysisResult
    };

    const blob = new Blob(
        [JSON.stringify(report, null, 2)],
        { type: "application/json" }
    );

    downloadBlob(blob, "threatlens-report.json");
    fileStatus.textContent = "JSON report downloaded successfully.";
}

function downloadCSVReport() {
    if (!lastAnalysisResult) {
        fileStatus.textContent =
            "Analyze a log file before downloading a CSV report.";
        return;
    }

    const headers = [
        "Username",
        "Failed Logins",
        "Successful Logins",
        "Longest Failure Streak",
        "Detection Reason",
        "Severity"
    ];

    function escapeCSV(value) {
        const text = String(value ?? "");
        return '"' + text.replace(/"/g, '""') + '"';
    }

    const rows = lastAnalysisResult.detections.map(function (item) {
        return [
            item.username,
            item.failed_logins,
            item.successful_logins,
            item.longest_failure_streak,
            item.detection_reason,
            item.severity
        ].map(escapeCSV);
    });

    const csvContent = [
        headers.map(escapeCSV).join(","),
        ...rows.map(function (row) {
            return row.join(",");
        })
    ].join("\r\n");

    const blob = new Blob(
        ["\uFEFF" + csvContent],
        { type: "text/csv;charset=utf-8;" }
    );

    downloadBlob(blob, "threatlens-detections.csv");
    fileStatus.textContent = "CSV report downloaded successfully.";
}

checkEngineStatus();
