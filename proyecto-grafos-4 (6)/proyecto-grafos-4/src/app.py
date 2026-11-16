"""Planificador de prerrequisitos · demo de consola.
Uso:  python -m src.app"""
import os
from .algoritmos import (kahn, formatear_traza, detectar_ciclo, encontrar_ciclo,
                         semestres_minimos, ruta_critica, plan_por_semestres,
                         es_orden_valido)
from .generador import dag_aleatorio, con_ciclo
from .persistencia import cargar_plan, cargar_plan_csv, guardar_prerrequisitos

DATOS = os.path.join(os.path.dirname(__file__), "..", "datos")
MENU = """
=== Planificador de prerrequisitos (Ingeniería de Sistemas) ===
 1. Ver materias y lista de adyacencia
 2. Orden de cursado (Kahn con cola)
 3. Orden de cursado (Kahn con pila)
 4. Semestres mínimos y plan por semestre
 5. Ruta crítica
 6. Traza paso a paso de Kahn
 7. Agregar prerrequisito (rechaza los que crean ciclo)
 8. Cargar plan con ciclo de ejemplo (ARQ -> ALG) y detectarlo
 9. Comparar cola vs pila
10. Generar DAG aleatorio y analizarlo
11. Guardar prerrequisitos actuales en CSV
12. Recargar plan original
13. Analizar otro plan de datos/planes (con o sin ciclos)
 0. Salir
"""


def nombre(info, c):
    return f"{c} ({info[c]['nombre']})" if c in info else str(c)


def cargar(archivo_prereq="prerrequisitos.csv"):
    return cargar_plan(os.path.join(DATOS, "materias.csv"),
                       os.path.join(DATOS, archivo_prereq))


def mostrar_orden(g, estructura):
    orden, hay = kahn(g, estructura)
    if hay:
        print("¡Hay ciclo! Materias sin ordenar:", ", ".join(detectar_ciclo(g)))
    else:
        print(f"Orden válido (Kahn con {estructura}):", " → ".join(orden))


def main():
    g, info = cargar()
    while True:
        print(MENU)
        try:
            op = input("Opción: ").strip()
        except EOFError:
            break
        try:
            if op == "0":
                break
            elif op == "1":
                for u in g.vertices():
                    suc = ", ".join(f"({v},{w})" for v, w in g.vecinos(u)) or "—"
                    print(f"  {nombre(info, u):<62} -> {suc}")
                print(f"|V| = {g.num_vertices()}  |E| = {g.num_aristas()}")
            elif op in ("2", "3"):
                mostrar_orden(g, "cola" if op == "2" else "pila")
            elif op == "4":
                for s, mats in plan_por_semestres(g).items():
                    print(f"  Semestre {s}: {', '.join(mats)}")
                print("Semestres mínimos:", semestres_minimos(g)[1])
            elif op == "5":
                print("Ruta crítica:", " → ".join(ruta_critica(g)))
            elif op == "6":
                est = input("Estructura (cola/pila): ").strip() or "cola"
                t = []
                kahn(g, est, traza=t)
                print(formatear_traza(t, est))
            elif op == "7":
                u = input("Prerrequisito (código): ").strip().upper()
                v = input("Materia que lo exige (código): ").strip().upper()
                if u not in info or v not in info:
                    print("Código desconocido.")
                    continue
                if u == v:
                    print("Una materia no puede ser prerrequisito de sí misma.")
                    continue
                if g.existe_arista(u, v):
                    print("Esa relación ya existe.")
                    continue
                g.agregar_arista(u, v, 1)
                if kahn(g)[1]:
                    print("Rechazado: crearía el ciclo",
                          " → ".join(encontrar_ciclo(g)))
                    g.quitar_arista(u, v)
                else:
                    print(f"Agregado {u} → {v}. Semestres mínimos ahora:",
                          semestres_minimos(g)[1])
            elif op == "8":
                gc, _ = cargar("prerrequisitos_ciclo.csv")
                print("Ciclo:", " → ".join(encontrar_ciclo(gc)))
                print("Materias sin ordenar:", ", ".join(detectar_ciclo(gc)))
            elif op == "9":
                oc, _ = kahn(g, "cola")
                op_, _ = kahn(g, "pila")
                print("Cola:", " → ".join(oc))
                print("Pila:", " → ".join(op_))
                print("Ambos válidos:", es_orden_valido(g, oc) and es_orden_valido(g, op_),
                      "| distintos:", oc != op_)
            elif op == "10":
                n = int(input("Vértices n: "))
                m = int(input("Aristas m: "))
                ga = dag_aleatorio(n, m, semilla=1)
                oc, _ = kahn(ga, "cola")
                op_, _ = kahn(ga, "pila")
                print("Semestres mínimos:", semestres_minimos(ga)[1],
                      "| órdenes válidos:", es_orden_valido(ga, oc), es_orden_valido(ga, op_))
                print("Con una arista de retorno, ¿hay ciclo?", kahn(con_ciclo(ga))[1])
            elif op == "11":
                ruta = os.path.join(DATOS, "prerrequisitos_guardado.csv")
                guardar_prerrequisitos(g, ruta)
                print("Guardado en", os.path.abspath(ruta))
            elif op == "12":
                g, info = cargar()
                print("Plan recargado.")
            elif op == "13":
                carpeta = os.path.join(DATOS, "planes")
                archivos = sorted(f for f in os.listdir(carpeta) if f.endswith(".csv"))
                for i, f in enumerate(archivos, 1):
                    print(f"  {i}. {f}")
                sel = input("Número o nombre del archivo: ").strip()
                nom = archivos[int(sel) - 1] if sel.isdigit() else sel
                gp, ip = cargar_plan_csv(os.path.join(carpeta, nom))
                print(f"Plan cargado: {gp.num_vertices()} materias y {gp.num_aristas()} prerrequisitos.")
                orden, hay = kahn(gp)
                if hay:
                    print("[!] Hay un ciclo de prerrequisitos:", " -> ".join(encontrar_ciclo(gp)))
                    bl = detectar_ciclo(gp)
                    print(f"Materias que no se pueden ordenar ({len(bl)}):", ", ".join(bl))
                else:
                    print("Orden válido:", " → ".join(orden))
                    print("Semestres mínimos:", semestres_minimos(gp)[1])
                    print("Ruta crítica:", " → ".join(ruta_critica(gp)))
            else:
                print("Opción no válida.")
        except (ValueError, KeyError, IndexError, FileNotFoundError) as e:
            print("Error:", e)


if __name__ == "__main__":
    main()
