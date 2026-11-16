"""Experimentos de la Entrega 3.  Desde la raíz del repositorio:

    python3 -m rendimiento.medir            # completo (hasta n = 128 000)
    python3 -m rendimiento.medir --rapido   # prueba corta (hasta n = 16 000)

Genera en rendimiento/: resultados.json, tres CSV y tres figuras PNG.
networkx se usa SOLO para validar y como referencia de tiempo."""
import json
import os
import platform
import random
import statistics
import sys
import time

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import networkx as nx
import numpy as np

from src.algoritmos import kahn, semestres_minimos, es_orden_valido, inversiones_de_nivel
from src.generador import dag_aleatorio

SALIDA = os.path.dirname(os.path.abspath(__file__))


def medir(funcion, *args, reps=5):
    """Una ejecución de calentamiento (se descarta) y `reps` mediciones."""
    funcion(*args)
    tiempos = []
    for _ in range(reps):
        t0 = time.perf_counter()
        funcion(*args)
        tiempos.append(time.perf_counter() - t0)
    return statistics.mean(tiempos), statistics.stdev(tiempos)


def pendiente(ns, ts):
    """Pendiente de la recta log T = b·log n + a."""
    b, _ = np.polyfit(np.log(ns), np.log(ts), 1)
    return float(b)


def a_nx(g):
    G = nx.DiGraph()
    G.add_nodes_from(g.vertices())
    G.add_edges_from((u, v) for u, v, _ in g.aristas())
    return G


def csv_escribir(nombre, filas):
    with open(os.path.join(SALIDA, nombre), "w", encoding="utf-8") as f:
        f.write("\n".join(filas) + "\n")


# --------------------------------------------------------------------------
def experimento_a(total=500, semilla=2026):
    """Validez y diferencias entre cola y pila en DAG aleatorios."""
    rnd = random.Random(semilla)
    factores = [1.5, 3, 5]
    ok = dict(cola=0, pila=0, distintos=0, mismos_sem=0, igual_nx=0)
    inv_c, inv_p = [], []
    por_m = {f: dict(dag=0, sem=[], inv_p=[], max_c=[], max_p=[]) for f in factores}
    for k in range(total):
        n = rnd.randint(20, 300)
        f = factores[k % 3]
        g = dag_aleatorio(n, int(f * n), semilla=semilla * 1000 + k)
        sc, sp = {}, {}
        oc, _ = kahn(g, "cola", stats=sc)
        op, _ = kahn(g, "pila", stats=sp)
        nivel, total_sem = semestres_minimos(g)
        ok["cola"] += es_orden_valido(g, oc)
        ok["pila"] += es_orden_valido(g, op)
        ok["distintos"] += oc != op
        # los semestres se recalculan recorriendo cada orden (deben coincidir)
        ok["mismos_sem"] += _sem_desde_orden(g, oc) == _sem_desde_orden(g, op) == nivel
        ok["igual_nx"] += total_sem == nx.dag_longest_path_length(a_nx(g)) + 1
        ic, ip = inversiones_de_nivel(oc, nivel), inversiones_de_nivel(op, nivel)
        inv_c.append(ic)
        inv_p.append(ip)
        d = por_m[f]
        d["dag"] += 1
        d["sem"].append(total_sem)
        d["inv_p"].append(ip / n)
        d["max_c"].append(sc["max_tam"])
        d["max_p"].append(sp["max_tam"])
    res = {"total": total, **ok,
           "inv_cola_max": max(inv_c),
           "inv_pila_media": statistics.mean(inv_p), "inv_pila_min": min(inv_p),
           "inv_pila_max": max(inv_p), "max_tam_cola_media": 0, "max_tam_pila_media": 0,
           "por_densidad": {}}
    todos_c = [x for d in por_m.values() for x in d["max_c"]]
    todos_p = [x for d in por_m.values() for x in d["max_p"]]
    res["max_tam_cola_media"] = statistics.mean(todos_c)
    res["max_tam_pila_media"] = statistics.mean(todos_p)
    for f, d in por_m.items():
        res["por_densidad"][str(f)] = {
            "dag": d["dag"], "sem_medios": statistics.mean(d["sem"]),
            "inv_pila_por_materia": statistics.mean(d["inv_p"]),
            "max_cola": statistics.mean(d["max_c"]), "max_pila": statistics.mean(d["max_p"])}
    filas = ["m_factor,dag,sem_medios,inv_pila_por_materia,max_cola,max_pila"]
    for f, v in res["por_densidad"].items():
        filas.append(f"{f},{v['dag']},{v['sem_medios']:.2f},{v['inv_pila_por_materia']:.3f},"
                     f"{v['max_cola']:.1f},{v['max_pila']:.1f}")
    csv_escribir("experimento_a.csv", filas)
    return res


def _sem_desde_orden(g, orden):
    nivel = {u: 1 for u in g.vertices()}
    for u in orden:
        for v, _ in g.vecinos(u):
            nivel[v] = max(nivel[v], nivel[u] + 1)
    return nivel


def grafica_escalera():
    """Semestre mínimo según la posición del orden (DAG de 40 vértices, 80 aristas)."""
    g = dag_aleatorio(40, 80, semilla=7)
    nivel, _ = semestres_minimos(g)
    oc, _ = kahn(g, "cola")
    op, _ = kahn(g, "pila")
    fig, ax = plt.subplots(figsize=(3.4, 2.1))
    ax.step(range(1, 41), [nivel[u] for u in oc], where="mid", label="cola", lw=1.6)
    ax.plot(range(1, 41), [nivel[u] for u in op], "-o", ms=2.5, lw=0.9, label="pila")
    ax.set_xlabel("posición en el orden", fontsize=7)
    ax.set_ylabel("semestre mínimo", fontsize=7)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=7)
    ax.grid(alpha=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, "escalera_cola_pila.png"), dpi=200)
    plt.close(fig)
    return {"inv_cola": inversiones_de_nivel(oc, nivel), "inv_pila": inversiones_de_nivel(op, nivel)}


# --------------------------------------------------------------------------
def experimento_b(ns, reps):
    filas = ["n,m,cola_ms,cola_sd,pila_ms,pila_sd,networkx_ms"]
    datos = []
    for n in ns:
        g = dag_aleatorio(n, 3 * n, semilla=n)
        G = a_nx(g)                                   # construcción fuera del tiempo medido
        mc, sc = medir(kahn, g, "cola", reps=reps)
        mp, sp = medir(kahn, g, "pila", reps=reps)
        mn, _ = medir(lambda: list(nx.topological_sort(G)), reps=reps)
        datos.append(dict(n=n, m=3 * n, cola=mc, cola_sd=sc, pila=mp, pila_sd=sp, nx=mn))
        filas.append(f"{n},{3*n},{mc*1e3:.3f},{sc*1e3:.3f},{mp*1e3:.3f},{sp*1e3:.3f},{mn*1e3:.3f}")
        print(f"B n={n:>7}  cola={mc*1e3:9.2f} ms  pila={mp*1e3:9.2f} ms  nx={mn*1e3:8.2f} ms", flush=True)
    csv_escribir("experimento_b.csv", filas)
    x = [d["n"] for d in datos]
    res = {"filas": datos,
           "pend_cola": pendiente(x, [d["cola"] for d in datos]),
           "pend_pila": pendiente(x, [d["pila"] for d in datos]),
           "pend_nx": pendiente(x, [d["nx"] for d in datos]),
           "us_por_elem_primero": datos[0]["cola"] / (datos[0]["n"] + datos[0]["m"]) * 1e6,
           "us_por_elem_ultimo": datos[-1]["cola"] / (datos[-1]["n"] + datos[-1]["m"]) * 1e6,
           "cociente_pila_cola_min": min(d["pila"] / d["cola"] for d in datos),
           "cociente_pila_cola_max": max(d["pila"] / d["cola"] for d in datos),
           "desv_rel_max": max(max(d["cola_sd"] / d["cola"], d["pila_sd"] / d["pila"]) for d in datos)}
    fig, ax = plt.subplots(figsize=(3.4, 2.5))
    for clave, et in (("cola", "cola"), ("pila", "pila"), ("nx", "networkx")):
        ax.loglog(x, [d[clave] for d in datos], "o-", ms=3, lw=1,
                  label=f"{et} (pend. ≈ {res['pend_' + clave]:.2f})")
    ax.set_xlabel("n (escala log)", fontsize=7)
    ax.set_ylabel("tiempo [s] (escala log)", fontsize=7)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6.5)
    ax.grid(True, which="both", alpha=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, "kahn_cola_vs_pila.png"), dpi=200)
    plt.close(fig)
    return res


def experimento_c(ns, reps):
    filas = ["n,lista_ms,matriz_ms,razon"]
    datos = []
    for n in ns:
        g = dag_aleatorio(n, 3 * n, semilla=n)
        gm = g.a_matriz()
        ml, _ = medir(kahn, g, "cola", reps=reps)
        mm, _ = medir(kahn, gm, "cola", reps=reps)
        datos.append(dict(n=n, lista=ml, matriz=mm, razon=mm / ml))
        filas.append(f"{n},{ml*1e3:.3f},{mm*1e3:.3f},{mm/ml:.1f}")
        print(f"C n={n:>5}  lista={ml*1e3:8.2f} ms  matriz={mm*1e3:9.2f} ms  x{mm/ml:.0f}", flush=True)
        del gm
    csv_escribir("experimento_c.csv", filas)
    x = [d["n"] for d in datos]
    res = {"filas": datos, "pend_lista": pendiente(x, [d["lista"] for d in datos]),
           "pend_matriz": pendiente(x, [d["matriz"] for d in datos])}
    fig, ax = plt.subplots(figsize=(3.4, 2.5))
    ax.loglog(x, [d["lista"] for d in datos], "o-", ms=3, lw=1,
              label=f"lista (pend. ≈ {res['pend_lista']:.2f})")
    ax.loglog(x, [d["matriz"] for d in datos], "s-", ms=3, lw=1,
              label=f"matriz (pend. ≈ {res['pend_matriz']:.2f})")
    ax.set_xticks(x)
    ax.set_xticklabels([str(v) for v in x])
    ax.minorticks_off()
    ax.set_xlabel("n (escala log)", fontsize=7)
    ax.set_ylabel("tiempo [s] (escala log)", fontsize=7)
    ax.tick_params(labelsize=7)
    ax.legend(fontsize=6.5)
    ax.grid(True, which="major", alpha=.3)
    fig.tight_layout()
    fig.savefig(os.path.join(SALIDA, "lista_vs_matriz.png"), dpi=200)
    plt.close(fig)
    return res


def main():
    rapido = "--rapido" in sys.argv
    ns_b = [1000 * 2 ** i for i in range(5 if rapido else 8)]      # 1 000 ... 128 000
    ns_c = [200 * 2 ** i for i in range(3 if rapido else 5)]       # 200 ... 3 200
    reps = 3 if rapido else 5
    entorno = {"python": platform.python_version(), "sistema": f"{platform.system()} {platform.release()}",
               "procesador": platform.machine(), "nucleos": os.cpu_count()}
    print("Entorno:", entorno)
    res = {"entorno": entorno, "rapido": rapido}
    res["A"] = experimento_a(100 if rapido else 500)
    res["escalera"] = grafica_escalera()
    print("A:", {k: v for k, v in res["A"].items() if k != "por_densidad"}, flush=True)
    res["B"] = experimento_b(ns_b, reps)
    res["C"] = experimento_c(ns_c, reps)
    with open(os.path.join(SALIDA, "resultados.json"), "w", encoding="utf-8") as f:
        json.dump(res, f, indent=2)
    print("Listo: resultados.json, CSV y figuras en rendimiento/")


if __name__ == "__main__":
    main()
