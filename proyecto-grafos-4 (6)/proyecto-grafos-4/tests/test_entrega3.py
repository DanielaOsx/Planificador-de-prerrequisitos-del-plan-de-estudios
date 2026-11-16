"""Entrega 3: cola frente a pila, inversiones de nivel, montículo y recorridos."""
import heapq
import random
import pytest
import networkx as nx
from src.algoritmos import (kahn, semestres_minimos, es_orden_valido, inversiones_de_nivel,
                            bfs, dfs)
from src.estructuras import MonticuloMin, NodoDoble
from src.generador import dag_aleatorio, con_ciclo
from tests.test_grafo import plan


def test_300_dag_ambos_ordenes_validos_y_mismos_semestres():
    for semilla in range(300):
        g = dag_aleatorio(30 + semilla % 40, 100, semilla=semilla)
        oc, hc = kahn(g, "cola")
        op, hp = kahn(g, "pila")
        assert not hc and not hp
        assert es_orden_valido(g, oc) and es_orden_valido(g, op)
        assert semestres_minimos(g)[1] >= 1


def test_cola_agrupa_por_semestres_y_pila_no():
    inv_pila = 0
    for semilla in range(100):
        g = dag_aleatorio(40, 80, semilla=semilla)
        nivel, _ = semestres_minimos(g)
        oc, _ = kahn(g, "cola")
        op, _ = kahn(g, "pila")
        assert inversiones_de_nivel(oc, nivel) == 0          # propiedad de la cola
        inv_pila += inversiones_de_nivel(op, nivel)
    assert inv_pila > 0                                      # la pila mezcla semestres


def test_inversiones_plan_ejemplo():
    g = plan()
    nivel, _ = semestres_minimos(g)
    assert inversiones_de_nivel(kahn(g, "cola")[0], nivel) == 0
    assert inversiones_de_nivel(kahn(g, "pila")[0], nivel) == 2     # bajas: FCC->MAS y ARQ->PLM


def test_ambas_estructuras_detectan_ciclos():
    for semilla in range(100):
        g = con_ciclo(dag_aleatorio(30, 60, semilla=semilla))
        assert kahn(g, "cola")[1] and kahn(g, "pila")[1]
        assert set(kahn(g, "cola")[0]) == set(kahn(g, "pila")[0])  # mismas ordenables


def test_stats_tamano_maximo():
    g = plan()
    sc, sp = {}, {}
    kahn(g, "cola", stats=sc)
    kahn(g, "pila", stats=sp)
    assert sc["max_tam"] == 4 and sp["max_tam"] == 3


def test_monticulo_contra_heapq():
    h, ref, r = MonticuloMin(), [], random.Random(1)
    for i in range(1000):
        if r.random() < 0.6 or not ref:
            x = r.randint(0, 10**6) + i / 10**7
            h.insertar(x, i)
            heapq.heappush(ref, (x, i))
        else:
            assert h.extraer() == heapq.heappop(ref)
    assert len(h) == len(ref)


def test_monticulo_vacio():
    with pytest.raises(IndexError):
        MonticuloMin().extraer()


def test_nodo_doble():
    a, b = NodoDoble(1), NodoDoble(2)
    a.siguiente, b.anterior = b, a
    assert a.siguiente.dato == 2 and b.anterior.dato == 1 and a.anterior is None


def test_bfs_dfs_contra_networkx():
    for semilla in range(50):
        g = dag_aleatorio(30, 60, semilla=semilla)
        G = nx.DiGraph()
        G.add_nodes_from(g.vertices())
        G.add_edges_from((u, v) for u, v, _ in g.aristas())
        s = g.vertices()[0]
        esperado = {s} | nx.descendants(G, s)
        assert set(bfs(g, s)) == esperado and set(dfs(g, s)) == esperado
