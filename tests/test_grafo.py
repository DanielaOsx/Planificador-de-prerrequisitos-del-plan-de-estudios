import os
import pytest
from src.grafo import Grafo
from src.persistencia import cargar_plan, cargar_plan_csv

DATOS = os.path.join(os.path.dirname(__file__), "..", "datos")


def plan(ciclo=False):
    return cargar_plan(os.path.join(DATOS, "materias.csv"),
                       os.path.join(DATOS, "prerrequisitos_ciclo.csv" if ciclo
                                    else "prerrequisitos.csv"))[0]


def test_instancia_tamano():
    g = plan()
    assert g.num_vertices() == 12 and g.num_aristas() == 13


def test_lazo_no_permitido():
    with pytest.raises(ValueError):
        Grafo().agregar_arista("A", "A")


def test_vecinos_vertice_inexistente():
    with pytest.raises(KeyError):
        Grafo().vecinos("X")


def test_existe_arista_y_grados():
    g = plan()
    assert g.existe_arista("ALG", "MAS") and not g.existe_arista("MAS", "ALG")
    gin = g.grados_entrada()
    assert gin["AA"] == 3 and gin["ARQ"] == 2 and gin["PLM"] == 0
    assert g.grado_salida("ALG") == 2


def test_matriz_equivale_a_lista():
    g = plan()
    m = g.a_matriz()
    assert sorted(m.aristas()) == sorted(g.aristas())
    assert m.grados_entrada() == g.grados_entrada()
    assert m.celdas() == 144
    for u in g.vertices():
        assert sorted(m.vecinos(u)) == sorted(g.vecinos(u))


def test_quitar_arista():
    g = plan()
    assert g.quitar_arista("ALG", "MAS") and not g.existe_arista("ALG", "MAS")
    assert not g.quitar_arista("ALG", "MAS")


def test_csv_compacto():
    g, info = cargar_plan_csv(os.path.join(DATOS, "planes", "plan_ejemplo.csv"))
    assert g.num_vertices() == 12 and g.existe_arista("FCC", "AA")


def test_csv_materia_desconocida(tmp_path):
    f = tmp_path / "p.csv"
    f.write_text("prerrequisito,materia\nXXX,ALG\n", encoding="utf-8")
    with pytest.raises(ValueError):
        cargar_plan(os.path.join(DATOS, "materias.csv"), str(f))
