import os
import random
import pytest
import networkx as nx
from src.algoritmos import (kahn, detectar_ciclo, encontrar_ciclo, semestres_minimos,
                            ruta_critica, plan_por_semestres, es_orden_valido,
                            bfs, dfs, formatear_traza)
from src.generador import dag_aleatorio, con_ciclo
from src.grafo import Grafo
from tests.test_grafo import plan


def test_kahn_cola_orden_esperado():
    orden, hay = kahn(plan(), "cola")
    assert not hay
    assert orden == ["PLM", "ALG", "CD", "MAS", "ED", "CI", "BD", "PAT",
                     "FCC", "WEB", "AA", "ARQ"]


def test_kahn_pila_orden_esperado():
    orden, hay = kahn(plan(), "pila")
    assert not hay
    assert orden == ["ALG", "ED", "FCC", "MAS", "PAT", "BD", "WEB", "ARQ",
                     "PLM", "CD", "CI", "AA"]


def test_ambos_ordenes_validos_y_distintos():
    g = plan()
    oc, _ = kahn(g, "cola")
    op, _ = kahn(g, "pila")
    assert es_orden_valido(g, oc) and es_orden_valido(g, op)
    assert oc != op


def test_estructura_invalida():
    with pytest.raises(ValueError):
        kahn(plan(), "heap")


def test_traza_cola_coincide_con_informe():
    t = []
    kahn(plan(), "cola", traza=t)
    assert len(t) == 13
    assert t[0]["contenido"] == ["PLM", "ALG"]
    assert t[5]["bajan"] == [("FCC", 1, 0), ("AA", 3, 2)]
    assert t[12]["contenido"] == []
    assert "Paso" in formatear_traza(t, "cola")


def test_traza_pila_inicial():
    t = []
    kahn(plan(), "pila", traza=t)
    assert t[0]["contenido"] == ["ALG", "PLM"]       # tope -> fondo


def test_ciclo_arq_alg():
    g = plan(ciclo=True)
    orden, hay = kahn(g)
    assert hay and orden == ["PLM", "CD", "CI"]
    assert len(detectar_ciclo(g)) == 9
    assert encontrar_ciclo(g) == ["ALG", "MAS", "BD", "WEB", "ARQ", "ALG"]


def test_sin_ciclo_listas_vacias():
    g = plan()
    assert detectar_ciclo(g) == [] and encontrar_ciclo(g) == []


def test_semestres_con_ciclo_lanza_error():
    with pytest.raises(ValueError):
        semestres_minimos(plan(ciclo=True))


def test_semestres_minimos_y_ruta_critica():
    g = plan()
    nivel, total = semestres_minimos(g)
    assert total == 5
    assert nivel["PLM"] == 1 and nivel["AA"] == 4 and nivel["ARQ"] == 5
    assert ruta_critica(g) == ["ALG", "MAS", "BD", "WEB", "ARQ"]
    assert len(ruta_critica(g)) == total
    assert plan_por_semestres(g)[1] == ["PLM", "ALG"]


def test_grafo_vacio():
    assert semestres_minimos(Grafo()) == ({}, 0)
    assert kahn(Grafo()) == ([], False)


def test_bfs_dfs_visitan_alcanzables():
    g = plan()
    assert set(bfs(g, "ALG")) == {"ALG", "MAS", "ED", "BD", "PAT", "FCC", "AA", "WEB", "ARQ"}
    assert set(dfs(g, "ALG")) == set(bfs(g, "ALG"))
    assert dfs(g, "ALG")[:3] == ["ALG", "MAS", "BD"]


@pytest.mark.parametrize("estructura", ["cola", "pila"])
def test_cruzada_networkx_50_dag(estructura):
    for semilla in range(50):
        g = dag_aleatorio(40, 90, semilla=semilla)
        G = nx.DiGraph()
        G.add_nodes_from(g.vertices())
        G.add_edges_from((u, v) for u, v, _ in g.aristas())
        orden, hay = kahn(g, estructura)
        assert not hay and es_orden_valido(g, orden)
        nivel, total = semestres_minimos(g)
        assert total == nx.dag_longest_path_length(G) + 1
        gen = {u: i + 1 for i, ge in enumerate(nx.topological_generations(G)) for u in ge}
        assert nivel == gen
        ruta = ruta_critica(g)
        assert len(ruta) == total
        assert all(g.existe_arista(a, b) for a, b in zip(ruta, ruta[1:]))


def test_ciclos_aleatorios_detectados():
    for semilla in range(30):
        g = con_ciclo(dag_aleatorio(30, 60, semilla=semilla))
        assert kahn(g)[1] and detectar_ciclo(g)
        c = encontrar_ciclo(g)
        assert c[0] == c[-1] and all(g.existe_arista(a, b) for a, b in zip(c, c[1:]))
        nx_g = nx.DiGraph([(u, v) for u, v, _ in g.aristas()])
        assert not nx.is_directed_acyclic_graph(nx_g)


def test_generador_m_excesivo():
    with pytest.raises(ValueError):
        dag_aleatorio(4, 7)
