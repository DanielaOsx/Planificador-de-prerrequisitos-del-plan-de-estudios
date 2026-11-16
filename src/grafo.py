"""Grafo dirigido ponderado con lista de adyacencia y su variante con matriz."""


class Grafo:
    """Grafo dirigido. adj: u -> [(v, peso), ...] (orden de inserción)."""

    def __init__(self):
        self.adj = {}

    def agregar_vertice(self, u):
        if u in self.adj:
            return False
        self.adj[u] = []
        return True

    def agregar_arista(self, u, v, w=1):                # O(1)
        """Agrega u -> v. Lanza ValueError si u == v. No revisa duplicados:
        una arista repetida se cuenta dos veces (también en el grado de entrada)."""
        if u == v:
            raise ValueError(f"lazo no permitido: {u} -> {u}")
        self.agregar_vertice(u)
        self.agregar_vertice(v)
        self.adj[u].append((v, w))

    def quitar_arista(self, u, v):
        """Elimina u -> v si existe. Devuelve True si la eliminó."""
        if u not in self.adj:
            return False
        antes = len(self.adj[u])
        self.adj[u] = [(x, w) for x, w in self.adj[u] if x != v]
        return len(self.adj[u]) < antes

    def existe_arista(self, u, v):                      # O(d+(u))
        return u in self.adj and any(x == v for x, _ in self.adj[u])

    def vertices(self):
        return list(self.adj)

    def vecinos(self, u):                               # O(1)
        if u not in self.adj:
            raise KeyError(u)
        return self.adj[u]

    def aristas(self):                                  # O(V + E)
        return [(u, v, w) for u, lista in self.adj.items() for v, w in lista]

    def grados_entrada(self):                           # O(V + E)
        grados = {u: 0 for u in self.adj}
        for lista in self.adj.values():
            for v, _ in lista:
                grados[v] += 1
        return grados

    def grado_salida(self, u):
        return len(self.vecinos(u))

    def num_vertices(self):
        return len(self.adj)

    def num_aristas(self):
        return sum(len(lista) for lista in self.adj.values())

    def a_matriz(self):
        """Construye el GrafoMatriz equivalente."""
        m = GrafoMatriz(self.vertices())
        for u, v, w in self.aristas():
            m.agregar_arista(u, v, w)
        return m


class GrafoMatriz:
    """Matriz de adyacencia (solo comparativa). None = no hay arista."""

    def __init__(self, vertices):
        self.nombres = list(vertices)
        self.idx = {u: i for i, u in enumerate(self.nombres)}
        n = len(self.nombres)
        self.m = [[None] * n for _ in range(n)]         # memoria Θ(V²)

    def agregar_arista(self, u, v, w=1):                # O(1)
        if u == v:
            raise ValueError(f"lazo no permitido: {u} -> {u}")
        self.m[self.idx[u]][self.idx[v]] = w

    def existe_arista(self, u, v):                      # O(1)
        return self.m[self.idx[u]][self.idx[v]] is not None

    def vecinos(self, u):                               # O(V): recorre la fila
        fila = self.m[self.idx[u]]
        return [(self.nombres[j], w) for j, w in enumerate(fila) if w is not None]

    def vertices(self):
        return list(self.nombres)

    def aristas(self):
        return [(u, v, w) for u in self.nombres for v, w in self.vecinos(u)]

    def grados_entrada(self):
        grados = {u: 0 for u in self.nombres}
        for u in self.nombres:
            for v, _ in self.vecinos(u):
                grados[v] += 1
        return grados

    def num_vertices(self):
        return len(self.nombres)

    def celdas(self):
        return len(self.nombres) ** 2
