
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
      
      r = random.randint(10, 15)
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
    
    
          msg += "\n\nExpected Hash Table:" + str(expected_ch_table) 
          msg += "Expected size: " + str(expected_ch_table.size())
          msg += "\n\nReturned Hash Table:" + str(student_ch_table) 
          msg += "Returned size: " + str(student_ch_table.size())
    
    
          while expected_ch_table.size() > 1:
            remove_key = keys[random.randint(0, len(keys)-1)]
            msg += "\n\n"+ "-"*35 +"\nRemoving key: " + str(remove_key)
            keys.remove(remove_key)
            student_ch_table.remove(remove_key)
            expected_ch_table.remove(remove_key)
    
            msg += "\n\nExpected Hash Table (after removal):" + str(expected_ch_table) 
            msg += "\n\nReturned Hash Table (after removal):" + str(student_ch_table) 
    
            expected_size = expected_ch_table.size()
            student_size = student_ch_table.size()
    
            msg += "\nExpected size after removal: "+ str(expected_size) +"\nReturned size: " +str(student_size)
    
            msg += "\n\nSearching for the removed key: " + str(remove_key) 
            student_search = student_ch_table.find(remove_key)
            msg += "\nExpected: None\nReturned: " + str(student_search)
    
            if expected_size != student_size or student_search is not None:
              msg += "\nTest failed."
              return TestOutput(passed=False, logs=msg)
            else:
              for k in keys:
               expected_bin = expected_ch_table._hash(k)
               actual_bin = student_ch_table._hash(k)
               expected_val = expected_ch_table.find(k)
               actual_val = student_ch_table.find(k)
               if expected_bin != actual_bin:
                      msg += f"Item with key {k} was stored in bin: {actual_bin}.\nExpected bin: {expected_bin}\n\nTest failed."
                      return TestOutput(passed=False, logs=msg)
               elif expected_val != actual_val:
                      msg += f"Key {k} is mapped to value {actual_val}.\nExpected value: {expected_val}\n\nTest failed."
                      return TestOutput(passed=False, logs=msg)
    
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
f = open("/outputs/146535.json", "w")
json.dump({"id": "146535", "passed": output.passed, "log": output.logs}, f)
f.close()
