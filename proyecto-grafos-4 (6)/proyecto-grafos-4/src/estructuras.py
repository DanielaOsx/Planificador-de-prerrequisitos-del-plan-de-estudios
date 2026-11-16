"""Estructuras auxiliares propias: Nodo, NodoDoble, Pila (LIFO), Cola (FIFO) y
MonticuloMin (cola de prioridad). Sin collections.deque ni heapq."""


class Nodo:
    """Nodo de una lista simplemente enlazada."""

    def __init__(self, dato, siguiente=None):
        self.dato = dato
        self.siguiente = siguiente


class NodoDoble:
    """Nodo de una lista doblemente enlazada."""

    def __init__(self, dato):
        self.dato = dato
        self.anterior = None
        self.siguiente = None


class Pila:
    """Pila (LIFO) sobre lista enlazada: push y pop en O(1)."""

    def __init__(self):
        self._tope = None
        self._n = 0

    def push(self, dato):
        self._tope = Nodo(dato, self._tope)
        self._n += 1

    def pop(self):
        if self.vacia():
            raise IndexError("pop sobre pila vacía")
        dato = self._tope.dato
        self._tope = self._tope.siguiente
        self._n -= 1
        return dato

    def peek(self):
        if self.vacia():
            raise IndexError("peek sobre pila vacía")
        return self._tope.dato

    def vacia(self):
        return self._tope is None

    def elementos(self):
        """Contenido de tope a fondo (para las trazas). O(n)."""
        res, actual = [], self._tope
        while actual is not None:
            res.append(actual.dato)
            actual = actual.siguiente
        return res

    def __len__(self):
        return self._n


class Cola:
    """Cola (FIFO) sobre lista enlazada con frente y final: O(1)."""

    def __init__(self):
        self._frente = self._final = None
        self._n = 0

    def encolar(self, dato):
        nuevo = Nodo(dato)
        if self._final is None:
            self._frente = self._final = nuevo
        else:
            self._final.siguiente = nuevo
            self._final = nuevo
        self._n += 1

    def desencolar(self):
        if self._frente is None:
            raise IndexError("desencolar sobre cola vacía")
        dato = self._frente.dato
        self._frente = self._frente.siguiente
        if self._frente is None:
            self._final = None
        self._n -= 1
        return dato

    def frente(self):
        if self._frente is None:
            raise IndexError("frente sobre cola vacía")
        return self._frente.dato

    def vacia(self):
        return self._frente is None

    def elementos(self):
        """Contenido de frente a final (para las trazas). O(n)."""
        res, actual = [], self._frente
        while actual is not None:
            res.append(actual.dato)
            actual = actual.siguiente
        return res

    def __len__(self):
        return self._n


class MonticuloMin:
    """Cola de prioridad con montículo binario: el menor sale primero.
    El padre de la posición i está en (i-1)//2; sus hijos en 2i+1 y 2i+2.
    No lo usa el planificador (lo usan Dijkstra, Prim y A*); forma parte de la
    base común de la guía."""

    def __init__(self):
        self._a = []

    def insertar(self, prioridad, dato):                # O(log n)
        self._a.append((prioridad, dato))
        i = len(self._a) - 1
        while i > 0 and self._a[i][0] < self._a[(i - 1) // 2][0]:
            p = (i - 1) // 2
            self._a[i], self._a[p] = self._a[p], self._a[i]
            i = p

    def extraer(self):                                  # O(log n)
        if not self._a:
            raise IndexError("extraer sobre montículo vacío")
        raiz, ultimo = self._a[0], self._a.pop()
        if self._a:
            self._a[0] = ultimo
            i, n = 0, len(self._a)
            while True:
                m, izq, der = i, 2 * i + 1, 2 * i + 2
                if izq < n and self._a[izq][0] < self._a[m][0]:
                    m = izq
                if der < n and self._a[der][0] < self._a[m][0]:
                    m = der
                if m == i:
                    break
                self._a[i], self._a[m] = self._a[m], self._a[i]
                i = m
        return raiz

    def vacio(self):
        return not self._a

    def __len__(self):
        return len(self._a)
