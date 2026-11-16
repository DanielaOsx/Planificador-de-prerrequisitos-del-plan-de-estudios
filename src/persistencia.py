"""Carga y guardado del plan de estudios desde CSV."""
import csv
from .grafo import Grafo


def cargar_plan(ruta_materias, ruta_prereq):
    """materias.csv: codigo,nombre,periodo · prerrequisitos.csv: prerrequisito,materia.
    Devuelve (grafo, info) con info[codigo] = {'nombre', 'periodo'}."""
    g, info = Grafo(), {}
    with open(ruta_materias, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            cod = fila["codigo"].strip()
            if cod in info:
                raise ValueError(f"código repetido: {cod}")
            info[cod] = {"nombre": fila["nombre"].strip(),
                         "periodo": int(fila["periodo"])}
            g.agregar_vertice(cod)
    with open(ruta_prereq, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            u, v = fila["prerrequisito"].strip(), fila["materia"].strip()
            for c in (u, v):
                if c not in info:
                    raise ValueError(f"materia desconocida en prerrequisitos: {c}")
            g.agregar_arista(u, v, 1)
    return g, info


def cargar_plan_csv(ruta):
    """Formato de la guía, un solo archivo: codigo,nombre,prerrequisitos
    (separados por ';', vacío si no hay). Dos pasadas: primero los vértices en
    el orden del archivo y luego las aristas prerrequisito -> materia.
    ValueError si hay código repetido, prerrequisito desconocido o lazo."""
    g, info, pendientes = Grafo(), {}, []
    with open(ruta, newline="", encoding="utf-8") as f:
        for fila in csv.DictReader(f):
            cod = fila["codigo"].strip()
            if cod in info:
                raise ValueError(f"código repetido: {cod}")
            info[cod] = {"nombre": fila["nombre"].strip(), "periodo": None}
            g.agregar_vertice(cod)
            for p in filter(None, (x.strip() for x in fila["prerrequisitos"].split(";"))):
                pendientes.append((p, cod))
    for u, v in pendientes:
        if u not in info:
            raise ValueError(f"{v} tiene un prerrequisito desconocido: {u}")
        g.agregar_arista(u, v, 1)          # ValueError si u == v (lazo)
    return g, info


def guardar_plan_csv(g, info, ruta):
    """Escribe el plan en el formato de cargar_plan_csv (ida y vuelta)."""
    pre = {u: [] for u in g.vertices()}
    for u, v, _ in g.aristas():
        pre[v].append(u)
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["codigo", "nombre", "prerrequisitos"])
        for u in g.vertices():
            w.writerow([u, info[u]["nombre"] if u in info else u, ";".join(pre[u])])


def guardar_prerrequisitos(g, ruta):
    with open(ruta, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["prerrequisito", "materia"])
        for u, v, _ in g.aristas():
            w.writerow([u, v])
