import os
import tempfile
import time
import sys
import pytest
import zipfile

def test_run_auto_tests_creates_log():
    sys.path.insert(0, os.path.abspath('src'))
    from utils import run_auto_tests
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create a dummy test file
        test_file = os.path.join(tmpdir, 'test_dummy.py')
        with open(test_file, 'w') as f:
            f.write('def test_dummy():\n    assert 1 == 1\n')
        log_file = os.path.join(tmpdir, 'session_log.txt')
        success, output = run_auto_tests(tmpdir, log_file)
        assert success, f"Tests did not pass: {output}"
        assert os.path.exists(log_file), "Log file was not created."
        with open(log_file) as f:
            log = f.read()
        assert "Auto-test-on-save triggered." in log, "Auto-test-on-save was not logged."
        assert "test_dummy.py::test_dummy PASSED" in log, "Test result not logged."

def test_create_bug_report_zip():
    import tempfile
    import os
    from src.utils import create_bug_report_zip
    with tempfile.TemporaryDirectory() as tmpdir:
        # Create dummy files
        file1 = os.path.join(tmpdir, 'log.txt')
        file2 = os.path.join(tmpdir, 'context.txt')
        with open(file1, 'w') as f:
            f.write('log content')
        with open(file2, 'w') as f:
            f.write('context content')
        # Create bug report zip
        zip_path = create_bug_report_zip([file1, file2], tmpdir)
        assert os.path.exists(zip_path), "Bug report zip was not created."
        # Check contents
        with zipfile.ZipFile(zip_path, 'r') as z:
            names = z.namelist()
        assert 'log.txt' in names, "log.txt not in bug report zip."
        assert 'context.txt' in names, "context.txt not in bug report zip." 