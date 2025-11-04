from ChainedHashTableCP import ChainedHashTable
import random

def test():
        """write your own tester in this function"""
        print("Testing ChainedHashTable...") # Assume hash function is f(key) = key mod 2^d
        table = ChainedHashTable()
        items = [(23, 'A'), (15, 'B'), (11, 'C'), (10, 'D'), (9, 'E'), (16, 'F'), (21, 'G')]
        for i in range(3):
            item = items[i]
            key = item[0]
            value = item[1]
            print('\n' + '-' * 40)
            print(f"Adding key = {key}, value = {value}")
            table.add(key, value)
            print(f"Table after addition:\n{table}\nNumber of elements n = {table.size()}"
                  f"\nLength of table: {2 ** table.d}")
        print('\n' + '-' * 40)
        print("Removing item with key 23 from table.\nTable BEFORE removal:", table)
        print(f"Number of elements n = {table.size()}\nLength of table: {2 ** table.d}")
        table.remove(23)
        print("\n" + "-"*20+"\nAFTER removal:", table)

        del items[0]
        print(f"\nNumber of elements n = {table.size()}\nLength of table: {2 ** table.d}")

        for i in range(3, len(items)):
            item = items[i]
            key = item[0]
            value = item[1]
            print('\n' + '-' * 40)
            print(f"Adding key = {key}, value = {value}")
            table.add(key, value)
            print(f"Table AFTER addition:\n{table}")
            print(f"\nNumber of elements n = {table.size()}\nLength of table: {2 ** table.d}")

        print(f"Replacing value of key 16 to be 'K':")
        table.set(16, 'K')
        print(table)

        while len(items) > 0:
            idx = random.randint(0, len(items)-1)
            key, val = items[idx]
            print('\n'+'-'*40)
            print(f"Removing item with key {key} from table.\nTable BEFORE removal:", table)
            print(f"Number of elements n = {table.size()}\nLength of table: {2 ** table.d}")
            table.remove(key)
            print("\n" + "-"*20 +"\nAFTER removal:", table)
            del items[idx]
            print(f"Number of elements n = {table.size()}\nLength of table: {2 ** table.d}")
