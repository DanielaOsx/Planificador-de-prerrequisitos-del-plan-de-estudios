"""Generador de DAG aleatorios sin ciclos.
Se permutan los vértices y solo se crean aristas de una posición menor a una
mayor de la permutación: así es imposible formar un ciclo."""
import random
from .grafo import Grafo


def dag_aleatorio(n, m, semilla=None):
    if m > n * (n - 1) // 2:
        raise ValueError("m excede el máximo de aristas de un DAG con n vértices")
    rnd = random.Random(semilla)
    perm = list(range(n))
    rnd.shuffle(perm)
    g = Grafo()
    for u in range(n):
        g.agregar_vertice(u)
    usadas = set()
    while len(usadas) < m:
        i, j = rnd.randrange(n), rnd.randrange(n)
        if i < j and (i, j) not in usadas:
            usadas.add((i, j))
            g.agregar_arista(perm[i], perm[j], 1)
    return g


def con_ciclo(g):
    """Copia de g con una arista de retorno v -> u sobre una arista u -> v
    existente, lo que cierra un ciclo de longitud 2."""
    copia = Grafo()
    for u in g.vertices():
        copia.agregar_vertice(u)
    for u, v, w in g.aristas():
        copia.agregar_arista(u, v, w)
    aristas = g.aristas()
    if aristas:
        u, v, _ = aristas[0]
        copia.agregar_arista(v, u, 1)
    return copia
