"""Figura del plan con la arista ARQ -> ALG (Entrega 2).
    python3 -m rendimiento.figura_ciclo"""
import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, Circle
from src.algoritmos import kahn, encontrar_ciclo
from src.persistencia import cargar_plan_csv

SALIDA = os.path.dirname(os.path.abspath(__file__))
POS = {"PLM": (1, 3.2), "ALG": (1, 1.2), "CD": (2, 3.6), "MAS": (2, 1.9), "ED": (2, 0.8),
       "CI": (3, 3.6), "BD": (3, 2.5), "PAT": (3, 1.4), "FCC": (3, 0.5),
       "WEB": (4, 2.5), "AA": (4, 1.0), "ARQ": (5, 1.8)}


def main():
    g, _ = cargar_plan_csv(os.path.join(SALIDA, "..", "datos", "planes", "plan_ciclo_largo.csv"))
    ordenadas, _ = kahn(g)
    ciclo = encontrar_ciclo(g)
    en_ciclo = set(ciclo)
    aristas_ciclo = set(zip(ciclo, ciclo[1:]))
    fig, ax = plt.subplots(figsize=(3.4, 2.9))
    r = 0.27
    for u, v, _ in g.aristas():
        x1, y1 = POS[u]
        x2, y2 = POS[v]
        color = "#d62728" if (u, v) in aristas_ciclo else "#666666"
        rad = -0.85 if (u, v) == ("ARQ", "ALG") else 0.0
        ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=7,
                                     lw=1.3 if color != "#666666" else 0.8, color=color,
                                     connectionstyle=f"arc3,rad={rad}", shrinkA=9, shrinkB=9,
                                     zorder=1))
    for u, (x, y) in POS.items():
        c = "#d62728" if u in en_ciclo else ("#ff9f43" if u not in ordenadas else "#cfcfcf")
        ax.add_patch(Circle((x, y), r, fc=c, ec="black", lw=0.6, zorder=3))
        ax.text(x, y, u, ha="center", va="center", fontsize=5.6, zorder=4,
                color="white" if u in en_ciclo else "black", weight="bold")
    for s in range(1, 6):
        ax.text(s, 4.35, f"sem. {s}", ha="center", fontsize=6)
    ax.set_xlim(0.4, 5.6); ax.set_ylim(-1.1, 4.6); ax.set_aspect("equal"); ax.axis("off")
    fig.tight_layout(pad=0.2)
    fig.savefig(os.path.join(SALIDA, "plan_con_ciclo.png"), dpi=220)


if __name__ == "__main__":
    main()
