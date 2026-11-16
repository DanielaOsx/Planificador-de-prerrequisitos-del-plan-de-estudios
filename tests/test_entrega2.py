"""Entrega 2: planes con ciclos, carga CSV, casos borde y validación cruzada."""
import os
import pytest
import networkx as nx
from src.algoritmos import (kahn, detectar_ciclo, encontrar_ciclo, semestres_minimos,
                            ruta_critica)
from src.estructuras import Cola
from src.generador import dag_aleatorio, con_ciclo
from src.grafo import Grafo
from src.persistencia import cargar_plan_csv, guardar_plan_csv

PLANES = os.path.join(os.path.dirname(__file__), "..", "datos", "planes")


def plan(nombre):
    return cargar_plan_csv(os.path.join(PLANES, nombre))


# ---- carga CSV ------------------------------------------------------------
def test_csv_equivale_a_lista_de_aristas():
    g, _ = plan("plan_ejemplo.csv")
    esperado = [("PLM", "CD"), ("CD", "CI"), ("ALG", "MAS"), ("ALG", "ED"), ("MAS", "BD"),
                ("MAS", "PAT"), ("ED", "FCC"), ("ED", "AA"), ("CI", "AA"), ("BD", "WEB"),
                ("PAT", "ARQ"), ("FCC", "AA"), ("WEB", "ARQ")]
    assert sorted((u, v) for u, v, _ in g.aristas()) == sorted(esperado)


def test_csv_ida_y_vuelta(tmp_path):
    g, info = plan("plan_ejemplo.csv")
    ruta = tmp_path / "copia.csv"
    guardar_plan_csv(g, info, str(ruta))
    g2, _ = cargar_plan_csv(str(ruta))
    assert g2.vertices() == g.vertices()
    assert sorted(g2.aristas()) == sorted(g.aristas())


def test_csv_auto_prerrequisito():
    with pytest.raises(ValueError, match="lazo"):
        plan("plan_auto_prerrequisito.csv")


def test_csv_prerrequisito_desconocido():
    with pytest.raises(ValueError, match="NOEXISTE"):
        plan("plan_prerrequisito_desconocido.csv")


def test_csv_codigo_repetido(tmp_path):
    f = tmp_path / "r.csv"
    f.write_text("codigo,nombre,prerrequisitos\nA,A,\nA,A otra,\n", encoding="utf-8")
    with pytest.raises(ValueError, match="repetido"):
        cargar_plan_csv(str(f))


# ---- planes con ciclos ----------------------------------------------------
def test_ciclo_largo():
    g, _ = plan("plan_ciclo_largo.csv")
    assert (g.num_vertices(), g.num_aristas()) == (12, 14)
    orden, hay = kahn(g)
    assert hay and orden == ["PLM", "CD", "CI"]
    assert sorted(detectar_ciclo(g)) == sorted(["ALG", "MAS", "ED", "BD", "PAT", "FCC",
                                                "AA", "WEB", "ARQ"])
    assert encontrar_ciclo(g) == ["ALG", "MAS", "BD", "WEB", "ARQ", "ALG"]


def test_ciclo_directo():
    g, _ = plan("plan_ciclo_directo.csv")
    assert (g.num_vertices(), g.num_aristas()) == (14, 15)
    orden, hay = kahn(g)
    assert hay and len(orden) == 12 and sorted(detectar_ciclo(g)) == ["XA", "XB"]
    assert encontrar_ciclo(g) == ["XA", "XB", "XA"]


def test_ciclo_aislado():
    g, _ = plan("plan_ciclo_aislado.csv")
    orden, hay = kahn(g)
    assert hay and orden == ["A1", "A2", "A3"]
    assert encontrar_ciclo(g) == ["C1", "C2", "C3", "C1"]


def test_semestres_y_ruta_lanzan_error_con_ciclo():
    g, _ = plan("plan_ciclo_largo.csv")
    with pytest.raises(ValueError):
        semestres_minimos(g)
    with pytest.raises(ValueError):
        ruta_critica(g)


# ---- casos borde ----------------------------------------------------------
def test_grafo_vacio():
    assert kahn(Grafo()) == ([], False)
    assert detectar_ciclo(Grafo()) == [] and encontrar_ciclo(Grafo()) == []


def test_materias_aisladas():
    g = Grafo()
    for c in "ABC":
        g.agregar_vertice(c)
    assert kahn(g) == (["A", "B", "C"], False)
    assert semestres_minimos(g) == ({"A": 1, "B": 1, "C": 1}, 1)


def test_prerrequisito_repetido_cuenta_dos_veces_pero_kahn_funciona():
    g = Grafo()
    g.agregar_arista("A", "B")
    g.agregar_arista("A", "B")
    assert g.num_aristas() == 2 and g.grados_entrada()["B"] == 2
    assert kahn(g) == (["A", "B"], False)


def test_cola_con_mil_elementos():
    c = Cola()
    for i in range(1000):
        c.encolar(i)
    assert len(c) == 1000 and [c.desencolar() for _ in range(1000)] == list(range(1000))


# ---- validación cruzada con networkx (solo para verificar) ----------------
def _nx(g):
    G = nx.DiGraph()
    G.add_nodes_from(g.vertices())
    G.add_edges_from((u, v) for u, v, _ in g.aristas())
    return G


def test_cruzada_200_dag():
    for semilla in range(200):
        g = dag_aleatorio(40, 90, semilla=semilla)
        orden, hay = kahn(g)
        pos = {u: i for i, u in enumerate(orden)}
        assert not hay and all(pos[u] < pos[v] for u, v, _ in g.aristas())
        _, total = semestres_minimos(g)
        assert total == nx.dag_longest_path_length(_nx(g)) + 1
        ruta = ruta_critica(g)
        assert len(ruta) == total and all(g.existe_arista(a, b) for a, b in zip(ruta, ruta[1:]))


def test_cruzada_200_grafos_con_ciclo():
    for semilla in range(200):
        g = con_ciclo(dag_aleatorio(40, 90, semilla=semilla))
        assert kahn(g)[1] and not nx.is_directed_acyclic_graph(_nx(g))
        c = encontrar_ciclo(g)
        assert c and c[0] == c[-1] and all(g.existe_arista(a, b) for a, b in zip(c, c[1:]))
