from SLLQueue import SLLQueue
from DLLDeque import DLLDeque


class MaxQueue(SLLQueue):
    def __init__(self):
        """
        constructor; initializes an empty MaxQueue
        """
        SLLQueue.__init__(self)
        self.max_deque = DLLDeque()

    def add(self, x: object):
        """
        adds a new element to the MaxQueue
        :param x: object type; the new element
        """
        SLLQueue.add(self, x)
        if self.max_deque.size() == 0:
            self.max_deque.add_first(x)
        else:
            n = self.max_deque.size()
            max_ele = self.max_deque.get(0)
            #print("deque size:", n)
            if x > max_ele:
                #print(x, "is larger than current max:", max_ele, "\nAdding", x, "to position 0 in dequeue")
                self.max_deque.clear()
                self.max_deque.add_first(x)
                #print(self.max_deque)
            else:

                tail = self.max_deque.get(n-1)
                #print(x,"is smaller than current max:", max_ele, "\nStarting comparison: x =", x, " vs.", tail)
                while x > tail:
                    #print("Compared x =", x, "against tail =", tail)
                    r = self.max_deque.remove_last()
                    #print("Removed from dequeue:", r)
                    #print("deque contents:", self.max_deque)
                    n -= 1
                    #print("deque size:", n)
                    if n == 0:
                        break
                    tail = self.max_deque.get(n - 1)
                self.max_deque.add_last(x)
        #print("max_deque contents:",self.max_deque)

    def remove(self) -> object:
        """
        removes and returns the element at the head of the MaxQueue
        :return: object type; the element that was removed from the head
        """
        r = SLLQueue.remove(self)
        if self.max_deque.size() > 0:
            if r == self.max_deque.get(0):
                self.max_deque.remove_first()
        return r

    def max(self):
        """
        returns the largest element currently stored in the MaxQueue
        :return: object type; the element with the largest value in the MaxQueue
        """
        return self.max_deque.get(0)





