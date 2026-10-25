
#include <iostream>
#include <fstream>
#include <sstream>
#include <string>
#include <vector>
#include <iomanip>

using namespace std;

const int TOTAL_FAILURE_THRESHOLD = 3;
const int CONSECUTIVE_FAILURE_THRESHOLD = 3;

struct Account {
    string username;
    int successfulLogins = 0;
    int failedLogins = 0;
    int currentFailureStreak = 0;
    int longestFailureStreak = 0;
};

struct AnalysisResult {
    int successfulLogins = 0;
    int failedLogins = 0;
    int invalidRecords = 0;
    int totalRecords = 0;
    int flaggedAccounts = 0;
};

struct AnalysisData {
    vector<Account> accounts;
    AnalysisResult result;
};

bool isValidUsername(const string& username) {
    if (username.empty() || username.size() > 64) {
        return false;
    }

    for (unsigned char ch : username) {
        if (!((ch >= 'a' && ch <= 'z') ||
              (ch >= 'A' && ch <= 'Z') ||
              (ch >= '0' && ch <= '9') ||
              ch == '_' || ch == '-' || ch == '.')) {
            return false;
        }
    }

    return true;
}

int findAccount(const vector<Account>& accounts,
                const string& username) {
    for (int i = 0; i < static_cast<int>(accounts.size()); i++) {
        if (accounts[i].username == username) {
            return i;
        }
    }

    return -1;
}

AnalysisData analyzeLogStream(istream& input) {
    AnalysisData data;
    string line;

    while (getline(input, line)) {
        if (line.find_first_not_of(" \t\r\n") == string::npos) {
            continue;
        }

        data.result.totalRecords++;

        stringstream ss(line);
        string username, status, extra;

        if (!(ss >> username >> status) || (ss >> extra)) {
            data.result.invalidRecords++;
            continue;
        }

        if (!isValidUsername(username) ||
            (status != "0" && status != "1")) {
            data.result.invalidRecords++;
            continue;
        }

        int index = findAccount(data.accounts, username);

        if (index == -1) {
            Account account;
            account.username = username;
            data.accounts.push_back(account);
            index = static_cast<int>(data.accounts.size()) - 1;
        }

        Account& account = data.accounts[index];

        if (status == "1") {
            data.result.successfulLogins++;
            account.successfulLogins++;
            account.currentFailureStreak = 0;
        } else {
            data.result.failedLogins++;
            account.failedLogins++;
            account.currentFailureStreak++;

            if (account.currentFailureStreak >
                account.longestFailureStreak) {
                account.longestFailureStreak =
                    account.currentFailureStreak;
            }
        }
    }

    for (const Account& account : data.accounts) {
        if (account.failedLogins >= TOTAL_FAILURE_THRESHOLD ||
            account.longestFailureStreak >=
                CONSECUTIVE_FAILURE_THRESHOLD) {
            data.result.flaggedAccounts++;
        }
    }

    return data;
}

string jsonEscape(const string& value) {
    string output;

    for (unsigned char ch : value) {
        switch (ch) {
            case '"':  output += "\\\""; break;
            case '\\': output += "\\\\"; break;
            case '\b': output += "\\b"; break;
            case '\f': output += "\\f"; break;
            case '\n': output += "\\n"; break;
            case '\r': output += "\\r"; break;
            case '\t': output += "\\t"; break;
            default:
                if (ch < 0x20) {
                    const char hex[] = "0123456789abcdef";
                    output += "\\u00";
                    output += hex[(ch >> 4) & 0x0F];
                    output += hex[ch & 0x0F];
                } else {
                    output += static_cast<char>(ch);
                }
        }
    }

    return output;
}

string getDetectionReason(const Account& account) {
    bool repeated = account.failedLogins >=
                    TOTAL_FAILURE_THRESHOLD;
    bool consecutive = account.longestFailureStreak >=
                       CONSECUTIVE_FAILURE_THRESHOLD;

    if (repeated && consecutive) {
        return "Repeated and consecutive failures";
    }

    if (consecutive) {
        return "Consecutive failed logins";
    }

    return "Repeated failed logins";
}

string getSeverity(const Account& account) {
    if (account.longestFailureStreak >=
            CONSECUTIVE_FAILURE_THRESHOLD ||
        account.failedLogins >= 5) {
        return "HIGH";
    }

    return "MEDIUM";
}

void displayJson(const AnalysisData& data) {
    const AnalysisResult& r = data.result;

    cout << "{";
    cout << "\"success\":true,";
    cout << "\"metrics\":{";
    cout << "\"records_analyzed\":" << r.totalRecords << ",";
    cout << "\"successful_logins\":" << r.successfulLogins << ",";
    cout << "\"failed_logins\":" << r.failedLogins << ",";
    cout << "\"invalid_records\":" << r.invalidRecords << ",";
    cout << "\"flagged_accounts\":" << r.flaggedAccounts;
    cout << "},";
    cout << "\"detections\":[";

    bool first = true;

    for (const Account& account : data.accounts) {
        bool flagged =
            account.failedLogins >= TOTAL_FAILURE_THRESHOLD ||
            account.longestFailureStreak >=
                CONSECUTIVE_FAILURE_THRESHOLD;

        if (!flagged) {
            continue;
        }

        if (!first) {
            cout << ",";
        }
        first = false;

        cout << "{";
        cout << "\"username\":\""
             << jsonEscape(account.username) << "\",";
        cout << "\"failed_logins\":" << account.failedLogins << ",";
        cout << "\"successful_logins\":"
             << account.successfulLogins << ",";
        cout << "\"longest_failure_streak\":"
             << account.longestFailureStreak << ",";
        cout << "\"detection_reason\":\""
             << jsonEscape(getDetectionReason(account)) << "\",";
        cout << "\"severity\":\""
             << getSeverity(account) << "\"";
        cout << "}";
    }

    cout << "]";
    cout << "}" << endl;
}

void displayReport(const AnalysisData& data) {
    const AnalysisResult& r = data.result;

    cout << "\n============================================\n";
    cout << "          THREATLENS SECURITY REPORT        \n";
    cout << "============================================\n";
    cout << left << setw(30) << "Records analyzed"
         << r.totalRecords << '\n';
    cout << left << setw(30) << "Successful logins"
         << r.successfulLogins << '\n';
    cout << left << setw(30) << "Failed logins"
         << r.failedLogins << '\n';
    cout << left << setw(30) << "Invalid records"
         << r.invalidRecords << '\n';

    cout << "\n============================================\n";
    cout << "             DETECTION RESULTS              \n";
    cout << "============================================\n";

    bool anyFlagged = false;

    for (const Account& account : data.accounts) {
        bool flagged =
            account.failedLogins >= TOTAL_FAILURE_THRESHOLD ||
            account.longestFailureStreak >=
                CONSECUTIVE_FAILURE_THRESHOLD;

        if (!flagged) {
            continue;
        }

        anyFlagged = true;

        cout << "\nAccount: " << account.username << '\n';
        cout << "Failed logins: " << account.failedLogins << '\n';
        cout << "Successful logins: "
             << account.successfulLogins << '\n';
        cout << "Longest failure streak: "
             << account.longestFailureStreak << '\n';
        cout << "Detection reason: "
             << getDetectionReason(account) << '\n';
        cout << "Severity: " << getSeverity(account) << '\n';
    }

    if (!anyFlagged) {
        cout << "\nNo suspicious accounts detected.\n";
    }

    cout << "\n============================================\n";
    cout << "Flagged accounts: " << r.flaggedAccounts << '\n';
    cout << "============================================\n";
}

int main(int argc, char* argv[]) {
    // Machine-readable mode: Python sends log text through stdin.
    if (argc == 2 && string(argv[1]) == "--json") {
        AnalysisData data = analyzeLogStream(cin);
        displayJson(data);
        return 0;
    }

    // Normal interactive mode: analyze a file by filename.
    string filename;

    cout << "============================================\n";
    cout << "       THREATLENS SECURITY ANALYTICS        \n";
    cout << "============================================\n";
    cout << "Enter log filename (e.g. login_logs.txt): ";

    getline(cin, filename);

    if (filename.empty()) {
        cerr << "ERROR: Filename cannot be empty.\n";
        return 1;
    }

    ifstream file(filename.c_str());

    if (!file.is_open()) {
        cerr << "ERROR: Could not open file: "
             << filename << '\n';
        return 1;
    }

    AnalysisData data = analyzeLogStream(file);
    displayReport(data);

    return 0;
}
