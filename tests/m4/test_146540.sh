
#!/bin/bash

function TestOutput {
    logs=${2:-""}
    logs=${logs//\"/\\\"}
    JSON_FMT='{"id":"%s","passed": %s, "log":"%s"}'
    printf "$JSON_FMT" "146540" $1 "$logs"  > ../outputs/146540.txt
}

#!/bin/bash

# Error handling function
error_exit() {
    TestOutput false "ERROR: $1"
    exit 1
}

# Run input_generator.py and check for errors
if ! python input_generator.py; then
    error_exit "input_generator.py failed to execute properly."
fi

# Check if calc_in_2.txt exists
if [ ! -f "calc_in_2.txt" ]; then
    error_exit "calc_in_2.txt not found."
fi


# Run Python solution script and capture output
expected_output=$(python mainCP.py < calc_in_2.txt) || error_exit "Python solution script failed."
student_output=$(python main.py < calc_in_2.txt) || error_exit "Python script main.py failed."


# Expected stored variables
expected_vars=$(echo "$expected_output" | sed -n '/Displaying stored variables:/,/Displayed/ { /Displaying stored variables:/d; /Displayed/d; p; }') || error_exit "Issue encountered while generating expected outcome."

# Expected final outcome
# Split the variable into an array of lines
IFS=$'\n' read -r -d '' -a lines <<< "$expected_vars"

# Calculate the index to start from for the second half
start_index=$(( ${#lines[@]} / 2 ))

# Extract the second half of the lines
second_half=$(printf "%s\n" "${lines[@]:start_index}")


# Initialize an array to store lines
expected=()

# Use a while loop to read each line
while IFS= read -r line; do
    # Store each line into a separate variable
    expected+=("$line")
done <<< "$expected_vars"

echo "Testing Calculator System: Replacing the value of an existing variable"
echo "Expected Stored Variables:"
for ((i = 0; i < ${#expected[@]}; i++)); do
    echo "${expected[i]}"
done

# Received stored variables
received_vars=$(echo "$student_output" | sed -n '/Displaying stored variables:/,/Displayed/ { /Displaying stored variables:/d; /Displayed/d; p; }') || error_exit "Issue encountered while generating expected outcome."


# Initialize an array to store lines
received=()

# Use a while loop to read each line
while IFS= read -r line; do
    # Store each line into a separate variable
    received+=("$line")
done <<< "$received_vars"


printf "\nReceived Stored Variables:\n"
for ((i = 0; i < ${#received[@]}; i++)); do
    echo "${received[i]}"
done

# Sort both lists
expected_list=($(printf "%s\n" "${expected[@]}" | sort))
received_list=($(printf "%s\n" "${received[@]}" | sort))


# Construct message
msg="Testing Calculator store_var(var, val, True) ...

STUDENT OUTPUT:
$student_output
-------------------------------------------
FEEDBACK:

* What this tester did:
      1. Selected option 1 of the Calculator Menu to store at least two new variables.
      2. Selected option 2 of the Calculator Menu to display all stored variables.
      3. Selected option 1 of the Calculator Menu to edit the value of an existing variable.
      4. Selected option 2 of the Calculator Menu to display all stored variables (the edited value should appear).

* Expected the following stored variables and corresponding final values:
$second_half"

# Check if the correct book was accessed
if [ "${expected_list[*]}" = "${received_list[*]}" ] && [[ -n "${expected_vars}" ]] && [[ ! "${expected_vars}" =~ ^[[:space:]]+$ ]]; then
    TestOutput true "$msg\n\nRESULT: Variables were CORRECTLY stored and displayed.\n\nTest PASSED."
else
    TestOutput false "$msg\n\nRESULT: Variables were NOT PROPERLY stored and/or displayed or an UNEXPECTED ERROR occurred.\n\nTest FAILED."
fi
