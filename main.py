import codepost
import dotenv
import os
import pathlib
import sys

# Load environment variables from .env file
dotenv.load_dotenv()

# 1️⃣ Configure API key
codepost.configure_api_key(os.getenv("CODEPOST_API_KEY", "").strip())

# 2️⃣ Retrieve course by ID
COURSE_ID = 5284  # CECS 274 SEC 01 3208 (Fall 2025)
course = codepost.course.retrieve(COURSE_ID)

print(f"Using course: {course.name} ({course.period}) — ID: {course.id}")

# 3️⃣ List all assignments correctly
print("\nAssignments in this course:")
for a in course.assignments:  # ✅ iterate directly; no .list()
    print(f"- {a.name} — ID: {a.id}")