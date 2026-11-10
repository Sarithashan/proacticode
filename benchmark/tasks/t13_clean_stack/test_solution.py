import pytest

from solution import Queue, Stack


def test_stack_order():
    s = Stack()
    s.push(1)
    s.push(2)
    assert s.peek() == 2
    assert s.pop() == 2
    assert len(s) == 1


def test_queue_order():
    q = Queue()
    q.enqueue("a")
    q.enqueue("b")
    assert q.dequeue() == "a"
    assert len(q) == 1


def test_empty_errors():
    with pytest.raises(IndexError):
        Stack().pop()
    with pytest.raises(IndexError):
        Stack().peek()
    with pytest.raises(IndexError):
        Queue().dequeue()
