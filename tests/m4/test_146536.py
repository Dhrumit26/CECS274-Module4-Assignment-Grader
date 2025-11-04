
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
    
          msg += "\n\nExpected Hash Table (before removal):\n" + str(expected_ch_table) 
          msg += "\n\nReturned Hash Table (before removal):\n" + str(student_ch_table) 
          remove_key = r-1
          msg += "\n\nRemoving key: " + str(remove_key)
    
          student_ch_table.remove(remove_key)
          expected_ch_table.remove(remove_key)
    
          msg += "\n\nExpected Hash Table (after removal):\n" + str(expected_ch_table) 
          msg += "\n\nReturned Hash Table (after removal):\n" + str(student_ch_table) 
    
          expected_size = expected_ch_table.size()
          student_size = student_ch_table.size()
    
          msg += "\nExpected size after removal: "+ str(expected_size) +"\nReturned size: " +str(student_size)
    
          c = random.randint(3, 26)
          msg += "\n\nAdding " + str(c)+ " more elements." 
          for i in range(c):
            expected_ch_table.add(i+1, chr(65+i))
            student_ch_table.add(i+1, chr(65+i))
    
          msg += "\n\nExpected Hash Table (after additions):\n" + str(expected_ch_table) 
          msg += "\n\nReturned Hash Table (after additions):\n" + str(student_ch_table)  
          expected_size = expected_ch_table.size()
          student_size = student_ch_table.size()
    
          msg += "\nExpected size after additions: "+ str(expected_size) +"\nReturned size: " +str(student_size)
    
    
          new_key = c-2
          msg += "\n\nSearching for key: " + str(new_key)
          student_search = student_ch_table.find(new_key)
          expected_search = expected_ch_table.find(new_key)
          msg += "\nExpected: "+str(expected_search)+"\nReturned: " + str(student_search)
    
          if expected_size != student_size or expected_search != student_search:
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
f = open("/outputs/146536.json", "w")
json.dump({"id": "146536", "passed": output.passed, "log": output.logs}, f)
f.close()
