#!/usr/bin/env python3
import argparse
import csv
import json
import os
import pathlib
import shutil
import subprocess
import sys
import tempfile
from typing import List, Dict, Set
from datetime import datetime

# ---------- Defaults tailored to your project ----------
DEFAULT_SUBMISSIONS = "downloads/CECS 274 SEC 01 3208 (Fall 2025)/Module 4_ Hash Tables"
DEFAULT_TESTS_DIR = "tests/m4"
DEFAULT_SUPPORT_DIR = "tests/m4"
DEFAULT_OUTPUT_DIR = "tests/m4"
DEFAULT_TESTS_DIR = "tests/m4"
OUTPUT_DIR = "tests/m4"
DEFAULT_RESULTS_CSV = "m4_code_results.csv"
DEFAULT_SUMMARY_CSV = "m4_code_summary.csv"
DEFAULT_LOG_FILE = "m4_grading_log.txt"
DEFAULT_TIMEOUT = 20  # seconds per test (hard stop)
# Provide the exact filenames expected from each student:
TARGET_FILENAMES = {
    "BookStore.py", "ChainedHashTable.py", "main.py"
}
# -------------------------------------------------------

class ConsoleLogger:
    """A logger that writes to both console and file."""
    def __init__(self, log_file_path: str):
        self.log_file = open(log_file_path, 'w', encoding='utf-8')
        self.start_time = datetime.now()
        self.log(f"=== MA4 Grading Started at {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} ===")
    
    def log(self, message: str):
        timestamp = datetime.now().strftime('%H:%M:%S')
        log_message = f"[{timestamp}] {message}"
        print(log_message)
        self.log_file.write(log_message + '\n')
        self.log_file.flush()
    
    def log_traceback(self, student: str, test_name: str, message: str, error: str = "", stderr: str = ""):
        self.log(f"  ✗ {test_name} FAILED for {student}")
        self.log(f"    MESSAGE: {message[:300]}")
        if error:
            self.log(f"    ERROR TRACEBACK:")
            for line in error.split('\n')[:20]:
                if line.strip():
                    self.log(f"      {line}")
        if stderr:
            self.log(f"    STDERR:")
            for line in stderr.split('\n')[:10]:
                if line.strip():
                    self.log(f"      {line}")
    
    def close(self):
        end_time = datetime.now()
        duration = end_time - self.start_time
        self.log(f"=== MA4 Grading Completed at {end_time.strftime('%Y-%m-%d %H:%M:%S')} (Duration: {duration}) ===")
        self.log_file.close()

def find_tests(tests_dir: pathlib.Path) -> List[pathlib.Path]:
    """
    Discover tests; return Python tests first, then Shell tests, each group sorted by name.
    """
    py_tests: List[pathlib.Path] = []
    sh_tests: List[pathlib.Path] = []
    for p in tests_dir.iterdir():
        if not p.is_file():
            continue
        if p.name.startswith("test_") and p.suffix == ".py":
            py_tests.append(p)
        elif p.name.startswith("test_") and p.suffix == ".sh":
            sh_tests.append(p)
    return sorted(py_tests, key=lambda x: x.name) + sorted(sh_tests, key=lambda x: x.name)

def iter_student_dirs(submissions_dir: pathlib.Path) -> List[pathlib.Path]:
    return sorted([p for p in submissions_dir.iterdir() if p.is_dir()])

def collect_student_sources(student_dir: pathlib.Path, targets: Set[str]) -> Dict[str, pathlib.Path]:
    """
    Search the student's submission tree for each required filename.
    Returns a map {filename: path_found}. Missing files are omitted.
    Skips common noise directories.
    """
    found: Dict[str, pathlib.Path] = {}
    skip_dirs = {".venv", "venv", "__pycache__", ".pytest_cache", ".git"}
    for root, dirs, files in os.walk(student_dir):
        # prune
        dirs[:] = [d for d in dirs if d not in skip_dirs]
        for fname in targets:
            if fname in files and fname not in found:
                found[fname] = pathlib.Path(root) / fname
        if set(found.keys()) == set(targets):
            break
    return found

def copy_support_files(support_dir: pathlib.Path, work_dir: pathlib.Path, overwrite: bool = False):
    """
    Copy support files (e.g., input_generator.py, mainCP.py) into the student's work dir.
    Do not overwrite student's files unless explicitly requested.
    """
    if not support_dir.exists():
        return
    for item in support_dir.iterdir():
        if item.is_file():
            dst = work_dir / item.name
            if not overwrite and dst.exists():
                continue
            try:
                shutil.copy2(item, dst)
            except Exception:
                # ignore if we can't copy; test may not need it
                pass

def write_runner(tmp_dir: pathlib.Path) -> pathlib.Path:
    runner_path = tmp_dir / "runner.py"
    runner_path.write_text(RUNNER_CODE, encoding="utf-8")
    return runner_path

def _read_json_or_text(fp: pathlib.Path):
    """
    Try to json-load the file; if it fails, return the raw text and an error string.
    """
    try:
        with open(fp, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return data, ""
    except Exception as e:
        try:
            raw = fp.read_text(encoding="utf-8")
        except Exception:
            raw = ""
        return None, f"Failed to parse JSON from {fp.name}; raw content captured:\n{raw[:1000]}\nError: {e}"

def run_shell_test(test_file: pathlib.Path, work_dir: pathlib.Path, timeout: float) -> Dict[str, str]:
    # Modern location
    modern_outputs = work_dir / "__outputs__"
    if modern_outputs.exists():
        for old in modern_outputs.glob("*"):
            try: old.unlink()
            except Exception: pass
    modern_outputs.mkdir(parents=True, exist_ok=True)

    # Legacy location: ../outputs
    legacy_outputs = work_dir.parent / "outputs"
    legacy_outputs.mkdir(parents=True, exist_ok=True)

    # Extract desired id from test filename, e.g., test_146297.sh -> "146297"
    import re
    m = re.search(r"test_(\d+)\.", test_file.name)
    desired_id = m.group(1) if m else None

    env = os.environ.copy()
    env["OUTPUTS_DIR"] = str(modern_outputs.resolve())

    try:
        proc = subprocess.run(
            ["bash", str(test_file.resolve())],
            cwd=str(work_dir.resolve()),
            env=env,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        out = (proc.stdout or "").strip()
        err = (proc.stderr or "").strip()

        # Prefer modern JSON (*.json)
        candidates = sorted(modern_outputs.glob("*.json"))
        if not candidates:
            # Legacy: prefer matching <id>.txt, else first .txt
            legacy = list(legacy_outputs.glob("*.txt"))
            if desired_id:
                legacy = sorted(legacy, key=lambda p: (p.stem != desired_id, p.name))
            candidates = legacy

        if not candidates:
            msg = ("Shell test wrote no result file.\nExpected either:\n"
                   f"  1) {modern_outputs}/<id>.json  (preferred), or\n"
                   f"  2) {legacy_outputs}/<id>.txt  (legacy)\n")
            if out: msg += f"\nSTDOUT:\n{out[:1000]}"
            if err: msg += f"\n\nSTDERR:\n{err[:1000]}"
            return {"ok": False, "message": msg, "error": ""}

        fp = candidates[0]
        try:
            # First, try strict JSON
            data = json.loads(fp.read_text(encoding="utf-8"))
        except Exception:
            # Repair legacy JSON-ish: convert raw newlines in strings to \n
            raw = fp.read_text(encoding="utf-8", errors="replace")
            repaired = raw.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")
            try:
                data = json.loads(repaired)
            except Exception as e:
                msg = f"Failed to parse JSON from {fp.name}; raw content captured:\n{raw[:1000]}\nError: {e}"
                if out: msg += f"\n\nSTDOUT:\n{out[:1000]}"
                if err: msg += f"\n\nSTDERR:\n{err[:1000]}"
                return {"ok": False, "message": msg[:2000], "error": ""}

        passed = bool(data.get("passed", False))
        log = str(data.get("log", ""))
        if out: log = f"{log}\n\nSTDOUT:\n{out[:1000]}".strip()
        if err: log = f"{log}\n\nSTDERR:\n{err[:1000]}".strip()
        return {"ok": passed, "message": log[:2000], "error": ""}

    except subprocess.TimeoutExpired:
        return {"ok": False, "message": f"Test timed out after {timeout} seconds", "error": ""}


def main():
    ap = argparse.ArgumentParser(description="Run MA2 tests against multiple student files.")
    ap.add_argument("--submissions-dir", default=DEFAULT_SUBMISSIONS)
    ap.add_argument("--tests-dir", default=DEFAULT_TESTS_DIR)
    ap.add_argument("--support-dir", default=DEFAULT_SUPPORT_DIR)
    ap.add_argument("--results-csv", default=DEFAULT_RESULTS_CSV)
    ap.add_argument("--summary-csv", default=DEFAULT_SUMMARY_CSV)
    ap.add_argument("--log-file", default=DEFAULT_LOG_FILE)
    ap.add_argument("--timeout", type=float, default=DEFAULT_TIMEOUT, help="Per-test timeout in seconds")
    ap.add_argument("--python-bin", default=sys.executable)
    args = ap.parse_args()

    submissions_dir = pathlib.Path(args.submissions_dir)
    tests_dir = pathlib.Path(args.tests_dir)
    support_dir = pathlib.Path(args.support_dir)
    results_csv = pathlib.Path(args.results_csv)
    summary_csv = pathlib.Path(args.summary_csv)
    log_file = pathlib.Path(args.log_file)
    
    logger = ConsoleLogger(str(log_file))

    if not submissions_dir.exists():
        logger.log(f"ERROR: Submissions directory not found: {submissions_dir.resolve()}")
        logger.close()
        raise SystemExit(f"Submissions directory not found: {submissions_dir.resolve()}")
    if not tests_dir.exists():
        logger.log(f"ERROR: Tests directory not found: {tests_dir.resolve()}")
        logger.close()
        raise SystemExit(f"Tests directory not found: {tests_dir.resolve()}")
    if not support_dir.exists():
        logger.log(f"WARN: Support dir not found: {support_dir.resolve()} (tests that import helpers may fail)")

    tests = find_tests(tests_dir)
    if not tests:
        logger.log(f"ERROR: No test_*.py or test_*.sh found in {tests_dir.resolve()}")
        logger.close()
        raise SystemExit(f"No test files found in {tests_dir.resolve()}")

    logger.log(f"Found {len(tests)} test(s): {[t.name for t in tests]}")

    results_csv.parent.mkdir(parents=True, exist_ok=True)
    summary_csv.parent.mkdir(parents=True, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmpd:
        tmp_root = pathlib.Path(tmpd)
        runner_path = write_runner(tmp_root)

        # Aggregates
        summary: Dict[str, Dict[str, int]] = {}

        with open(results_csv, "w", newline="", encoding="utf-8") as rf:
            rw = csv.writer(rf)
            rw.writerow(["student_email(s)", "test_file", "passed", "message"])

            # module names we want to force-import (stems)
            required_modules = ",".join(sorted({pathlib.Path(f).stem for f in TARGET_FILENAMES}))

            for student_dir in iter_student_dirs(submissions_dir):
                student = student_dir.name
                summary.setdefault(student, {"total": 0, "passed": 0, "failed": 0, "missing_files": 0})

                # Create a per-student working dir and place their sources there
                work_dir = tmp_root / f"work_{student.replace(os.sep,'_')}"
                work_dir.mkdir(parents=True, exist_ok=True)

                # 1) Copy student target files
                found_map = collect_student_sources(student_dir, TARGET_FILENAMES)
                missing = sorted(list(TARGET_FILENAMES - set(found_map.keys())))
                if missing:
                    summary[student]["missing_files"] = len(missing)
                    logger.log(f"INFO: {student}: missing required files: {missing}")
                    # Optional: auto-skip tests if critical files missing
                    if len(missing) == len(TARGET_FILENAMES):
                        logger.log(f"SKIPPING {student}: all files missing")
                        continue

                for fname, src_path in found_map.items():
                    dst = work_dir / fname
                    try:
                        shutil.copy2(src_path, dst)
                    except Exception as e:
                        logger.log(f"WARN: could not copy {src_path} -> {dst}: {e}")

                # 2) Copy support files (e.g., input_generator.py, mainCP.py) WITHOUT overwriting student code
                copy_support_files(support_dir, work_dir, overwrite=False)

                # make package-import happy
                (work_dir / "__init__.py").write_text("", encoding="utf-8")

                logger.log(f"RUN: {student} -> using {len(found_map)}/{len(TARGET_FILENAMES)} files")

                # Run each test (Python first, then Shell) in its own subprocess with a deterministic seed
                for idx, tfile in enumerate(tests):
                    seed = 1337 + idx

                    if tfile.suffix == ".sh":
                        # --- Shell test path ---
                        result = run_shell_test(tfile, work_dir, timeout=args.timeout)
                        ok = bool(result.get("ok", False))
                        message = result.get("message", "")
                        error = result.get("error", "")

                        full_message = message
                        if missing:
                            full_message = f"Missing files: {missing}\n\n" + full_message

                        rw.writerow([student, tfile.name, int(ok), full_message])
                        summary[student]["total"] += 1
                        if ok:
                            summary[student]["passed"] += 1
                            logger.log(f"  ✓ {tfile.name}")
                        else:
                            summary[student]["failed"] += 1
                            logger.log(f"  ✗ {tfile.name}: {message[:140]}")
                        continue

                    # --- Python test path ---
                    cmd = [
                        args.python_bin,
                        str(runner_path),
                        str(work_dir.resolve()),             # student's working directory with sources
                        str(tests_dir.resolve()),            # tests dir (for util imports)
                        str(support_dir.resolve() if support_dir.exists() else ""),
                        str(tfile.resolve()),                # specific test file to run
                        str(seed),
                        required_modules,                    # module names we must preload
                    ]
                    try:
                        proc = subprocess.run(
                            cmd,
                            capture_output=True,
                            text=True,
                            timeout=args.timeout,
                        )
                        out = (proc.stdout or "").strip()
                        err = (proc.stderr or "").strip()

                        # parse JSON
                        data = {}
                        try:
                            data = json.loads(out) if out else {}
                        except json.JSONDecodeError:
                            data = {"ok": False, "message": "Invalid JSON output", "error": f"STDOUT: {out[:500]}\nSTDERR: {err[:500]}"}

                        ok = bool(data.get("ok", False))
                        message = data.get("message", "")
                        error = data.get("error", "")

                        full_message = message
                        if missing:
                            full_message = f"Missing files: {missing}\n\n" + full_message
                        if error:
                            full_message += f"\n\nERROR:\n{error}"
                        if proc.returncode != 0:
                            full_message += f"\n\n(subprocess exit code: {proc.returncode})"
                        if err and not error:
                            full_message += f"\n\nSTDERR:\n{err}"

                        rw.writerow([student, tfile.name, int(ok), full_message])
                        summary[student]["total"] += 1
                        if ok:
                            summary[student]["passed"] += 1
                            logger.log(f"  ✓ {tfile.name}")
                        else:
                            summary[student]["failed"] += 1
                            logger.log(f"  ✗ {tfile.name}: {message[:140]}")

                    except subprocess.TimeoutExpired:
                        rw.writerow([student, tfile.name, 0, f"Test timed out after {args.timeout} seconds"])
                        summary[student]["total"] += 1
                        summary[student]["failed"] += 1
                        logger.log(f"  ✗ {tfile.name}: TIMEOUT")

        # Write summary
        with open(summary_csv, "w", newline="", encoding="utf-8") as sf:
            sw = csv.writer(sf)
            sw.writerow(["student_email(s)", "total_tests", "passed", "failed", "percent_passed", "missing_required_files"])
            for student, s in sorted(summary.items()):
                total = s["total"]
                passed = s["passed"]
                failed = s["failed"]
                pct = (passed / total * 100.0) if total else 0.0
                sw.writerow([student, total, passed, failed, f"{pct:.2f}", s["missing_files"]])

    logger.log(f"✅ Results:  {results_csv.resolve()}")
    logger.log(f"✅ Summary:  {summary_csv.resolve()}")
    logger.log(f"✅ Log file: {log_file.resolve()}")
    logger.close()

# ---------------- runner: executes one *Python* test file ----------------
# Arguments:
#   argv[1] = student_src_dir   (directory containing student's source files)
#   argv[2] = tests_dir         (directory of tests; may contain util.py, etc.)
#   argv[3] = support_dir       (optional; can be empty string)
#   argv[4] = single test file path to run
#   argv[5] = seed (int)
#   argv[6] = required module names (csv)
RUNNER_CODE = r"""
import json, os, random, sys, traceback, unittest, importlib.util, runpy, builtins
from pathlib import Path

def add_path(p):
    if p and p not in sys.path:
        sys.path.insert(0, p)

def _inside(base: Path, target: Path) -> bool:
    try:
        target.resolve().relative_to(base.resolve())
        return True
    except Exception:
        return False

def preload_student_modules(student_src_dir: Path, module_names_csv: str):
    '''
    Preload specified modules by filename from the student's source directory,
    and pin them into sys.modules to ensure imports resolve to student code.
    If any module fails (syntax/import error), skip that module but continue others.
    '''
    if not module_names_csv:
        return
    names = [n.strip() for n in module_names_csv.split(",") if n.strip()]
    for name in names:
        py_path = student_src_dir / f"{name}.py"
        if not py_path.exists():
            print(f"PRELOAD WARNING: {py_path.name} missing", file=sys.stderr)
            continue
        try:
            spec = importlib.util.spec_from_file_location(name, str(py_path))
            mod = importlib.util.module_from_spec(spec)
            assert spec.loader is not None
            spec.loader.exec_module(mod)  # type: ignore
            sys.modules[name] = mod
        except Exception as e:
            print(f"PRELOAD WARNING: Failed to load {py_path.name}: {type(e).__name__}: {e}", file=sys.stderr)
            import types
            dummy = types.ModuleType(name)
            sys.modules[name] = dummy

def load_single_test_module(test_path: Path):
    spec = importlib.util.spec_from_file_location(test_path.stem, str(test_path))
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)  # type: ignore
    return mod

def run_unittest_mode(test_file: Path):
    test_mod = load_single_test_module(test_file)
    suite = unittest.defaultTestLoader.loadTestsFromModule(test_mod)
    result = unittest.TestResult()
    suite.run(result)
    if result.testsRun == 0:
        return {"ok": False, "message": "No unittest tests discovered in file."}
    if result.wasSuccessful():
        return {"ok": True, "message": f"All {result.testsRun} test(s) passed"}
    else:
        if result.failures:
            tc, tb = result.failures[0]
            return {"ok": False, "message": f"Failure in {tc.id()}", "error": tb}
        elif result.errors:
            tc, tb = result.errors[0]
            return {"ok": False, "message": f"Error in {tc.id()}", "error": tb}
        return {"ok": False, "message": "Unknown failure", "error": ""}

def run_gradescope_compat(test_file: Path, outputs_dir: Path):
    import io, contextlib
    outputs_dir.mkdir(parents=True, exist_ok=True)

    _real_open = builtins.open
    def _patched_open(file, *args, **kwargs):
        if isinstance(file, str) and file.startswith("/outputs/"):
            file = str(outputs_dir / os.path.basename(file))
        return _real_open(file, *args, **kwargs)

    buf_out, buf_err = io.StringIO(), io.StringIO()
    builtins.open = _patched_open  # type: ignore
    try:
        with contextlib.redirect_stdout(buf_out), contextlib.redirect_stderr(buf_err):
            runpy.run_path(str(test_file), run_name="__main__")
    finally:
        builtins.open = _real_open  # restore

    candidates = sorted(outputs_dir.glob("*.json"))
    if not candidates:
        out_s = buf_out.getvalue()
        err_s = buf_err.getvalue()
        return {"ok": None, "message": "no-json", "stdout": out_s[:1000], "stderr": err_s[:1000]}
    try:
        with open(candidates[0], "r", encoding="utf-8") as fh:
            data = json.load(fh)
        passed = bool(data.get("passed", False))
        log = str(data.get("log", ""))
        out_s = buf_out.getvalue()
        err_s = buf_err.getvalue()
        if out_s:
            log = f"{log}\n\nSTDOUT:\n{out_s[:1000]}".strip()
        if err_s:
            log = f"{log}\n\nSTDERR:\n{err_s[:1000]}".strip()
        return {"ok": passed, "message": log[:2000]}
    except Exception:
        out_s = buf_out.getvalue()
        err_s = buf_err.getvalue()
        msg = "Failed to read outputs JSON"
        if out_s:
            msg += f"\n\nSTDOUT:\n{out_s[:1000]}"
        if err_s:
            msg += f"\n\nSTDERR:\n{err_s[:1000]}"
        return {"ok": False, "message": msg, "error": traceback.format_exc()}

def main():
    # argv:
    #   1 = student_src_dir
    #   2 = tests_dir (e.g., .../tests/m3)
    #   3 = support_dir (may be empty)
    #   4 = test_file path
    #   5 = seed
    #   6 = required module names (csv)
    student_src_dir = Path(sys.argv[1])
    tests_dir = Path(sys.argv[2])
    support_dir = Path(sys.argv[3]) if sys.argv[3] else None
    test_file = Path(sys.argv[4])
    seed = int(sys.argv[5])
    required_modules_csv = sys.argv[6] if len(sys.argv) > 6 else ""

    # ---- PATHS: make "import tests.m3.*" resolvable ----
    add_path(str(student_src_dir))

    # Add parent of 'tests' so 'import tests.*' works, and the subdir itself
    try:
        add_path(str(tests_dir.parent))   # -> .../tests
    except Exception:
        pass
    add_path(str(tests_dir))              # -> .../tests/m3

    if support_dir:
        try:
            add_path(str(support_dir.parent))
        except Exception:
            pass
        add_path(str(support_dir))

    # ---- Create virtual 'tests' & 'tests.m3' packages (robust to missing __init__.py) ----
    import types
    tests_root_dir = tests_dir if tests_dir.name == "tests" else tests_dir.parent
    if "tests" not in sys.modules:
        tests_pkg = types.ModuleType("tests")
        tests_pkg.__path__ = [str(tests_root_dir)]
        sys.modules["tests"] = tests_pkg
    if "tests.m3" not in sys.modules:
        m3_pkg = types.ModuleType("tests.m3")
        m3_pkg.__path__ = [str(tests_dir)]
        sys.modules["tests.m3"] = m3_pkg

    # Always chdir & seed (FIX: not inside support_dir block)
    os.chdir(student_src_dir)
    random.seed(seed)

    # PRELOAD after paths are fixed
    preload_student_modules(student_src_dir, required_modules_csv)

    # Try Gradescope-style first; fallback to unittest if no JSON
    outputs_dir = student_src_dir / "__outputs__"
    if outputs_dir.exists():
        for old in outputs_dir.glob("*"):
            try:
                old.unlink()
            except Exception:
                pass

    try:
        gs_result = run_gradescope_compat(test_file, outputs_dir)
        if gs_result.get("ok", None) is None and gs_result.get("message") == "no-json":
            ut_result = run_unittest_mode(test_file)
            if not ut_result.get("ok", False) and "No unittest tests discovered" in ut_result.get("message", ""):
                stdout = gs_result.get("stdout", "")
                stderr = gs_result.get("stderr", "")
                extra = ""
                if stdout:
                    extra += f"\n\n(When executed as script) STDOUT:\n{stdout}"
                if stderr:
                    extra += f"\n\n(When executed as script) STDERR:\n{stderr}"
                ut_result["message"] += extra
            print(json.dumps(ut_result))
        else:
            print(json.dumps(gs_result))
    except Exception as e:
        print(json.dumps({"ok": False, "message": str(e), "error": traceback.format_exc()}))

if __name__ == "__main__":
    main()
"""


if __name__ == "__main__":
    main()
