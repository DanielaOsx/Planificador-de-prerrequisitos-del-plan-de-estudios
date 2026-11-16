import pytest
from src.estructuras import Cola, Pila


def test_cola_fifo():
    c = Cola()
    for x in (1, 2, 3):
        c.encolar(x)
    assert c.frente() == 1 and len(c) == 3
    assert [c.desencolar() for _ in range(3)] == [1, 2, 3]
    assert c.vacia()


def test_cola_reutilizable_tras_vaciarse():
    c = Cola()
    c.encolar("a"); c.desencolar(); c.encolar("b")
    assert c.desencolar() == "b" and c.vacia()


def test_cola_excepciones():
    c = Cola()
    with pytest.raises(IndexError):
        c.desencolar()
    with pytest.raises(IndexError):
        c.frente()


def test_pila_lifo():
    p = Pila()
    for x in (1, 2, 3):
        p.push(x)
    assert p.peek() == 3 and len(p) == 3
    assert [p.pop() for _ in range(3)] == [3, 2, 1]
    assert p.vacia()


def test_pila_excepciones():
    p = Pila()
    with pytest.raises(IndexError):
        p.pop()
    with pytest.raises(IndexError):
        p.peek()


def test_elementos_para_trazas():
    c, p = Cola(), Pila()
    for x in "abc":
        c.encolar(x); p.push(x)
    assert c.elementos() == ["a", "b", "c"]
    assert p.elementos() == ["c", "b", "a"]
