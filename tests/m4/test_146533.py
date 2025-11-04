
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
    import ChainedHashTableCP
    import random
    
    def TestCase():
      # TestCase must return a TestOutput Object
      # TestObject is initialized
      student_ch_table = ChainedHashTable.ChainedHashTable()
      expected_ch_table = ChainedHashTableCP.ChainedHashTable()
      
      r = random.randint(5, 15)
      msg = "Creating a ChainedHashTable with elements...\n"
      try:
          keys = []
          for i in range(r):
            key = random.randint(10, 100)
            val = chr(random.randint(65, 85))
            expected_ch_table.add(key, val)
            student_ch_table.add(key, val)
            if key not in keys:
              keys.append(key)
              msg += f"\n(k: {key}, v: {val})"
            else:
              msg += f"\n(k: {key}, v: {val})  <= Should not be added; key already exists"
    
    
          msg += "\n\nExpected Hash Table:\n" + str(expected_ch_table) 
          msg += "\n\nReturned Hash Table:\n" + str(student_ch_table) 
          s_key = keys[random.randint(0, len(keys))]
          msg += "\n\nSearching for key: " + str(s_key)
    
          student_value = student_ch_table.find(s_key)
          expected_value = expected_ch_table.find(s_key)
          msg += "\nExpected: "+ str(expected_value) +"\nReturned: " +str(student_value)
          if student_value != expected_value:
            msg += "\nTest failed."
            return TestOutput(passed=False, logs=msg)
          else:
            msg += "\nTest passed."
            return TestOutput(passed=True, logs=msg)
      except Exception as e:
          msg += f"\nThe following unexpected error occurred:\n{e}"
          return TestOutput(passed=False, logs=msg)

    output = TestCase()
    assert(isinstance(output, TestOutput))
except Exception as e:
    errorLogs = traceback.format_exc()
    output = TestOutput(False, str(errorLogs))
f = open("/outputs/146533.json", "w")
json.dump({"id": "146533", "passed": output.passed, "log": output.logs}, f)
f.close()
