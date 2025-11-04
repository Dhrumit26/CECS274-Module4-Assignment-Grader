#!/usr/bin/env python3
import os
import pathlib
import sys
import time
import codepost
import dotenv
dotenv.load_dotenv()

# --- CONFIG: update these if needed ---
COURSE_ID = 5284           # FIXME depends on your course
ASSIGNMENT_ID = 37201      # FIXME depends on your assignment
OUTDIR = "./downloads"     # base folder for saving files

# Provide one of:
# 1) a list/tuple/set of exact filenames to download, OR
# 2) set to None to download ALL files in each submission.
TARGET_FILENAMES = {
    "BookStore.py", "ChainedHashTable.py", "main.py"
}
# --------------------------------------

def get_api_key():
    key = os.getenv("CODEPOST_API_KEY", "").strip()
    if not key:
        sys.exit("Missing API key. Set CODEPOST_API_KEY or edit the script to hardcode it.")
    return key

def safe_folder_name(name: str) -> str:
    bad = '<>:"/\\|?*'
    for ch in bad:
        name = name.replace(ch, "_")
    return name.strip()

def main():
    codepost.configure_api_key(get_api_key())

    # 1) Find course
    course = codepost.course.retrieve(COURSE_ID)
    course_dir = safe_folder_name(f"{course.name} ({course.period})")

    # 2) Find assignment (by ID is most reliable)
    assignment = codepost.assignment.retrieve(ASSIGNMENT_ID)
    assignment_dir = safe_folder_name(assignment.name)

    base = pathlib.Path(OUTDIR) / course_dir / assignment_dir
    base.mkdir(parents=True, exist_ok=True)

    # Normalize TARGET_FILENAMES to a set or None
    targets = None if TARGET_FILENAMES in (None, set(), [], ()) else set(TARGET_FILENAMES)

    print(
        "Downloading submissions for:\n"
        f"  Course: {course.name} ({course.period}) [ID {course.id}]\n"
        f"  Assignment: {assignment.name} [ID {assignment.id}]\n"
        f"  -> {base.resolve()}\n"
    )
    if targets is None:
        print("  Filtering: (none) — downloading ALL files.\n")
    else:
        print(f"  Filtering for files named exactly: {sorted(targets)}\n")

    # 3) Get all submissions
    try:
        submissions = assignment.list_submissions()
    except AttributeError:
        try:
            submissions = list(getattr(assignment, "submissions", []))
        except Exception as e:
            sys.exit(f"Could not enumerate submissions: {e}")

    total_files = 0
    skipped_students = []

    for sub in submissions:
        # Build a stable folder name per submission (handles partners/groups)
        students = getattr(sub, "students", []) or []
        folder = ",".join(sorted(students)) if students else f"submission_{sub.id}"
        sub_dir = base / safe_folder_name(folder)
        sub_dir.mkdir(parents=True, exist_ok=True)

        files = getattr(sub, "files", []) or []
        matched_any = False

        for f in files:
            try:
                f.refresh()
            except Exception:
                pass

            name = getattr(f, "name", f"file_{getattr(f,'id','unknown')}")

            # If targets are specified, only keep those names; else keep all files
            if targets is not None and name not in targets:
                continue

            matched_any = True
            rel_path = getattr(f, "path", None)  # optional subdirectory
            code = getattr(f, "code", None)

            out_dir = sub_dir / safe_folder_name(rel_path) if rel_path else sub_dir
            out_dir.mkdir(parents=True, exist_ok=True)
            out_file = out_dir / name

            if code is None:
                print(f"  [skip] {folder}/{name} (no text content)")
                continue

            try:
                with open(out_file, "w", encoding="utf-8", newline="") as fh:
                    fh.write(code)
                total_files += 1
                print(f"  ✓ {folder}/{name}")
            except UnicodeEncodeError:
                with open(out_file, "w", encoding="utf-8", errors="replace", newline="") as fh:
                    fh.write(code)
                total_files += 1
                print(f"  ✓ {folder}/{name} (encoding fallback)")

            # Optional: light throttling on very large classes
            # time.sleep(0.02)

        if not matched_any:
            skipped_students.append(folder)
            if targets is None:
                # Shouldn't happen if downloading all files, but keep the message generic
                print(f"  ✗ {folder} (no files matched)")
            else:
                print(f"  ✗ {folder} (none of {sorted(targets)} found)")

    target_msg = "selected" if targets is not None else "all"
    print(f"\n✅ Done. Saved {total_files} {target_msg} file(s) under: {base.resolve()}")

    if skipped_students:
        print(f"\n⚠️  {len(skipped_students)} submission(s) missing requested files:")
        for student in skipped_students[:10]:
            print(f"    - {student}")
        if len(skipped_students) > 10:
            print(f"    ... and {len(skipped_students) - 10} more")

if __name__ == "__main__":
    main()
