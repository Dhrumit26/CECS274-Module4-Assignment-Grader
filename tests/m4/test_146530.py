
import json
import traceback
import os

class TestOutput:
    def __init__(self, passed, logs):
        assert (isinstance(passed, bool))
        assert (isinstance(logs, str))
        self.passed = passed
        self.logs = logs

try:
    # To call a student's method, uncomment the following line and call <fileName>.<method>
    
    # import <insert student's fileName here>
    import ChainedHashTable
    
    def TestCase():
      # TestCase must return a TestOutput Object
      # TestObject is initialized
      student_stack = ChainedHashTable.ChainedHashTable()
      
      rNone = student_stack.remove(100)
      msg = "Created empty ChainedHashTable and attempted to remove an element."
      
      if rNone is not None:
        msg += "\nReturned: " + str(rNone) + "\nExpected: None.\nTest failed."
        return TestOutput(passed=False, logs=msg)
      else:
        msg += "\nReturned: " + str(rNone) + "\nExpected: None.\nTest passed."
        return TestOutput(passed=True, logs=msg)

    output = TestCase()
    assert(isinstance(output, TestOutput))
except Exception as e:
    errorLogs = traceback.format_exc()
    output = TestOutput(False, str(errorLogs))
f = open("/outputs/146530.json", "w")
json.dump({"id": "146530", "passed": output.passed, "log": output.logs}, f)
f.close()
