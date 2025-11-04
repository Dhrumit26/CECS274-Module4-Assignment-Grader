# Grading Automation

This small script lists your available CodePost courses. It requires a CodePost API key.

## Setup

```bash
# Create a virtual environment (recommended name: venv)
python3 -m venv venv

# Activate the environment (Linux/macOS)
source venv/bin/activate

1. Ensure you're using the workspace's Python 3.9 environment.
2. Install dependencies (already installed if you ran with this workspace):

```bash
pip install -r requirements.txt
```

3. Export your CodePost API key in your shell:

```bash
export CODEPOST_API_KEY=your_api_key_here
```

## Run main.py to get the courseID and assignmentID

```bash
python main.py
```

## Put the courseID and assignmentID into download_submissions.py and then run the download_submission.py to retrieve the submission from CodePost
```bash
  python download_submission.py
```
## Run the grade_module_4.py to run against the test cases
```bash
  python grade_module_4.py
```
## Run the Student_csv_excel.py to convert student_grades_csv file to Excel
```bash
  python Student_csv_excel.py
```
