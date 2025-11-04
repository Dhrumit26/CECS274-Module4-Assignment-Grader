#!/usr/bin/env bash
set -euo pipefail

# Ensure output directory exists
mkdir -p ../outputs

# Write a valid JSON object to ../outputs/146538.txt
# Properly JSON-escape the entire log string using jq (preferred) or Python fallback.
function TestOutput {
    local passed="$1"
    local logs="${2-}"

    local log_json
    if command -v jq >/dev/null 2>&1; then
        # -R: read raw text, -s: slurp all into a single string, output as JSON string literal
        log_json="$(printf '%s' "$logs" | jq -R -s .)"
    else
        # Fallback to Python's json.dumps
        log_json="$(
            python3 - <<'PY' <<< "$logs"
import sys, json
print(json.dumps(sys.stdin.read()))
PY
        )"
    fi

    # log_json is already a JSON string literal. Do NOT wrap it in extra quotes.
    printf '{"id":"%s","passed": %s, "log":%s}\n' "146538" "$passed" "$log_json" > ../outputs/146538.txt
}

# Error handling helper
error_exit() {
    TestOutput false "ERROR: $1"
    exit 1
}

# --- Test flow ---

# 1) Generate inputs
if ! python input_generator.py; then
    error_exit "input_generator.py failed to execute properly."
fi

# 2) Check required input file
if [ ! -f "store_input.txt" ]; then
    error_exit "store_input.txt not found."
fi

catalog_num="$(sed -n '3 s/[^0-9]//gp' store_input.txt || true)"
key="$(sed -n '7p' store_input.txt || true)"

# 3) Run reference and student programs (capture all output)
expected_output="$(python mainCP.py < store_input.txt 2>&1)" || error_exit "Python solution script failed."
student_output="$(python main.py   < store_input.txt 2>&1)" || error_exit "Python script main.py failed."

# 4) Extract expected / returned book blocks
expected="$(echo "$expected_output" | sed -n '/The following book matching the given key was found at catalog index/,/Action/ { /The following book matching the given key was found at catalog index/d; /Action/d; p; }')" || error_exit "Issue encountered while generating expected outcome."
expected_idx="$(echo "$expected_output" | grep -E "^The following book matching the given key was found at catalog index [0-9]+:" | sed 's/.*index \([0-9]\+\):/\1/' || true)"

returned="$(echo "$student_output" | sed -n '/The following book matching the given key was found at catalog index/,/Action/ { /The following book matching the given key was found at catalog index/d; /Action/d; p; }')" || error_exit "The expected outcome was not returned."
returned_idx="$(echo "$student_output" | grep -E "^The following book matching the given key was found at catalog index [0-9]+:" | sed 's/.*index \([0-9]\+\):/\1/' || true)"

# 5) Build feedback message (raw, multi-line; will be JSON-escaped by TestOutput)
msg="Testing search by key $key on catalog $catalog_num...
STUDENT OUTPUT:
$student_output
-------------------------------------------
FEEDBACK:

* What this tester did:
      1. Loaded catalog $catalog_num
      2. Search for the book matching the key: $key

* Expected the index $expected_idx with the following matching book information:
$expected"

# 6) Compare and emit result as JSON
if [ "$expected_idx" = "$returned_idx" ] && [ "$expected" = "$returned" ] && [[ -n "${expected}" ]] && [[ ! "${expected}" =~ ^[[:space:]]+$ ]]; then
    TestOutput true "$msg

RESULT: Matching book was CORRECTLY identified.

Test PASSED."
else
    TestOutput false "$msg

RESULT: INCORRECT identification or an UNEXPECTED ERROR occurred.

Test FAILED."
fi
