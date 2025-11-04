
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
      student_ht = ChainedHashTable.ChainedHashTable()
      
      found_node = student_ht.find(100)
      msg = "Created empty ChainedHashTable and attempted to find an element with key 100."
      
      if found_node is not None:
        msg += "\nReturned: " + str(found_node) + "\nExpected: None.\nTest failed."
        return TestOutput(passed=False, logs=msg)
      else:
        msg += "\nReturned: " + str(found_node) + "\nExpected: None.\nTest passed."
        return TestOutput(passed=True, logs=msg)

    output = TestCase()
    assert(isinstance(output, TestOutput))
except Exception as e:
    errorLogs = traceback.format_exc()
    output = TestOutput(False, str(errorLogs))
f = open("/outputs/146531.json", "w")
json.dump({"id": "146531", "passed": output.passed, "log": output.logs}, f)
f.close()
