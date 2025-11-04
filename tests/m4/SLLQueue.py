from Interfaces import Queue


class SLLQueue(Queue):
    class Node:
        def __init__(self, x: object):
            self.next = None
            self.x = x

    def __init__(self):
        """
        constructor; initializes an empty SLLQueue
        """
        self.head = None
        self.tail = None
        self.n = 0

    def add(self, x: object):
        """
        adds an element to the tail of the queue
        :param x: object type; the new element
        """
        u = SLLQueue.Node(x)
        if self.size() == 0:
            self.head = u
        else:
            self.tail.next = u
        self.tail = u
        self.n += 1

    def remove(self) -> object:
        """
        removes and returns the head of the queue
        :return: object type; the element that was removed from the head of the queue
        :raises: IndexError if the queue is empty
        """
        if self.size() == 0:
            raise IndexError()
        x = self.head.x
        self.head = self.head.next
        self.n -= 1
        if self.size() == 0:
            self.head = None
            self.tail = None

        return x

    def reverse(self):
        """
        reverses the order of the queue
        """
        if self.n > 1:
            dummy = self.head
            parent = dummy.next
            grandparent = parent.next
            dummy.next = None

            while parent != None:
                parent.next = dummy
                dummy = parent
                parent = grandparent
                if parent != None:
                    grandparent = parent.next
            self.tail = self.head
            self.head = dummy

    def size(self) -> int:
        """
        returns the number of elements in the queue
        :return: int type
        """
        return self.n

    def __str__(self):
        s = "["
        u = self.head
        while u is not None:
            s += "%r" % u.x
            u = u.next
            if u is not None:
                s += ","
        return s + "]"

    def __iter__(self):
        self.iterator = self.head
        return self

    def __next__(self):
        if self.iterator != None:
            x = self.iterator.x
            self.iterator = self.iterator.next
        else:
            raise StopIteration()
        return x

# q = SLLQueue()
# for i in range(10):
#     q.add(i)
#
# print(q)
#
# for i in range(q.size()):
#     print(f"Element at {i}: {q.get(i)}")
#
# q.reverse()
# print(q)
# for i in range(q.size()):
#     print(f"Element at {i}: {q.get(i)}")
#
# while q.size() > 0:
#     print(q.remove(), end=" ")
# print(q)
