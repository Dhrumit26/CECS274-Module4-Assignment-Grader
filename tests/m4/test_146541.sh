#!/usr/bin/env bash
set -euo pipefail

# Ensure output directory exists
mkdir -p ../outputs

# ---------------- JSON writer (escapes newlines/quotes safely) ----------------
TestOutput() {
  local passed="$1"
  local logs="${2-}"

  local log_json
  if command -v jq >/dev/null 2>&1; then
    # Turn raw multiline text into a single JSON string
    log_json="$(printf '%s' "$logs" | jq -R -s .)"
  else
    # Fallback: Python's json.dumps
    log_json="$(
      python3 - <<'PY' <<< "$logs"
import sys, json
print(json.dumps(sys.stdin.read()))
PY
    )"
  fi

  # log_json is already a JSON string literal; don't add extra quotes
  printf '{"id":"%s","passed": %s, "log":%s}\n' "146541" "$passed" "$log_json" > ../outputs/146541.txt
}

# ---------------- error helper ----------------
error_exit() {
  TestOutput false "ERROR: $1"
  exit 1
}

# ---------------- generate inputs ----------------
if ! python input_generator.py; then
  error_exit "input_generator.py failed to execute properly."
fi

# Check if calc_in_3.txt exists
if [ ! -f "calc_in_3.txt" ]; then
  error_exit "calc_in_3.txt not found."
fi

# Pull the expression shown on line 11 (best-effort)
expression="$(sed -n '11p' calc_in_3.txt || true)"

# ---------------- run reference & student programs (capture stdout+stderr) ----------------
expected_output="$(python mainCP.py < calc_in_3.txt 2>&1)" || error_exit "Python solution script failed."
student_output="$(python main.py   < calc_in_3.txt 2>&1)" || error_exit "Python script main.py failed."

# ---------------- extract sections (POSIX-safe; no grep -P) ----------------
# Expected stored variables block between known markers
expected_vars="$(printf '%s\n' "$expected_output" | sed -n '/Displaying stored variables:/,/Displayed/{
  /Displaying stored variables:/d
  /Displayed/d
  p
}')" || error_exit "Issue encountered while generating expected outcome."

# Extract 'Result: ...' value (appears after a prompt). Match anywhere on the line.
# If there are multiple Result lines, take the first.
expected="$(printf '%s\n' "$expected_output" | sed -n 's/.*Result: //p' | head -n 1)" || error_exit "Issue encountered while generating student outcome."
received="$(printf '%s\n' "$student_output"  | sed -n 's/.*Result: //p' | head -n 1)" || error_exit "Issue encountered while generating student outcome."

# ---------------- build feedback message ----------------
msg="Testing Calculator print expression with replaced values ...

STUDENT OUTPUT:
$student_output
-------------------------------------------
FEEDBACK:

* What this tester did:
      1. Selected option 1 of the Calculator Menu to store at least two variables.
      2. Selected option 2 of the Calculator Menu to display all stored variables.
      3. Selected option 3 of the Calculator Menu to display the expression: 
      				$expression
         with existing stored values replaced into the expression.
      

* Expected the following stored variables and corresponding values:
$expected_vars

* Expected the following expression with values replaced:
$expected"

# ---------------- verdict ----------------
if [ "$expected" = "$received" ] && [[ -n "${expected}" ]] && [[ ! "${expected}" =~ ^[[:space:]]+$ ]]; then
  TestOutput true "$msg

RESULT: Stored values were CORRECTLY replaced into expression.

Test PASSED."
else
  TestOutput false "$msg

RESULT: Expression was incorrect and/or displayed or an UNEXPECTED ERROR occurred.

Test FAILED."
fi
