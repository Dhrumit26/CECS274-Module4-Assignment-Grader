
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
      msg = "Creating a ChainedHashTable with items...\n"
      try:
          keys = []
          for i in range(r):
            key = random.randint(10, 100)
            val = chr(random.randint(65, 85))
    
            if key not in keys:
              expected_ch_table.add(key, val)
              student_ch_table.add(key, val)
              keys.append(key)
              msg += f"\n(k: {key}, v: {val})"
              
    
    
          msg += "\n\nExpected Hash Table:" + str(expected_ch_table) 
          msg += "Expected number of elements: " + str(expected_ch_table.size())
          msg += "\n\nReturned Hash Table:" + str(student_ch_table) 
          msg += "Returned number of elements: " + str(student_ch_table.size())
    
    
    
          if expected_ch_table.size() != student_ch_table.size():
            msg += "\nTest failed."
            return TestOutput(passed=False, logs=msg)
          else:
            rand_key = keys[random.randint(0, len(keys)-1)]
            new_value = random.randint(-10, 10)
            msg +='\n\n'+'-'*40 + f"\nReplacing value for item with key = {rand_key} with new value = {new_value}"
      
            expected_old = expected_ch_table.set(rand_key, new_value)
            received_old = student_ch_table.set(rand_key, new_value)
            msg += f"\nExpected old value: {expected_old}\nReturned old value: {received_old}"
            msg += "\n\nExpected Hash Table:" + str(expected_ch_table) 
            msg += "Expected number of elements: " + str(expected_ch_table.size())
            msg += "\n\nReturned Hash Table:" + str(student_ch_table) 
            msg += "Returned number of elements: " + str(student_ch_table.size())
            for k in keys:
               expected_bin = expected_ch_table._hash(k)
               actual_bin = student_ch_table._hash(k)
               expected_val = expected_ch_table.find(k)
               actual_val = student_ch_table.find(k)
               if expected_bin != actual_bin:
                      msg += f"\nItem with key {k} was stored in bin: {actual_bin}.\nExpected bin: {expected_bin}\n\nTest failed."
                      return TestOutput(passed=False, logs=msg)
               elif expected_val != actual_val:
                      msg += f"\nKey {k} is mapped to value {actual_val}.\nExpected value: {expected_val}\n\nTest failed."
                      return TestOutput(passed=False, logs=msg)
    
            msg += "\nTest passed."
            return TestOutput(passed=True, logs=msg)
      except Exception as e:
          msg += f"\nThe following unexpected error occurred:\n{e}."
          return TestOutput(passed=False, logs=msg)

    output = TestCase()
    assert(isinstance(output, TestOutput))
except Exception as e:
    errorLogs = traceback.format_exc()
    output = TestOutput(False, str(errorLogs))
f = open("/outputs/146537.json", "w")
json.dump({"id": "146537", "passed": output.passed, "log": output.logs}, f)
f.close()
