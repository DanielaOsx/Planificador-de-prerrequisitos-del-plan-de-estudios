"""Algoritmos del proyecto 4: Kahn (cola o pila), ciclos, semestres mínimos,
ruta crítica y recorridos BFS/DFS con las estructuras propias."""
from .estructuras import Cola, Pila


def kahn(g, estructura="cola", traza=None, stats=None):
    """Ordenamiento topológico de Kahn: O(V + E).

    estructura: "cola" (FIFO) o "pila" (LIFO).
    traza: lista opcional; si se entrega, se llena con el paso a paso.
    stats: dict opcional; recibe "max_tam" (tamaño máximo de la estructura).
    Devuelve (orden, hay_ciclo); hay_ciclo <=> len(orden) < |V|.
    """
    if estructura not in ("cola", "pila"):
        raise ValueError(f"estructura inválida: {estructura!r} (use 'cola' o 'pila')")
    if estructura == "cola":
        aux = Cola()
        poner, sacar = aux.encolar, aux.desencolar
    else:
        aux = Pila()
        poner, sacar = aux.push, aux.pop

    grado = g.grados_entrada()
    for u in g.vertices():
        if grado[u] == 0:
            poner(u)
    max_tam = len(aux)
    if traza is not None:
        traza.append({"paso": 0, "sale": None, "bajan": [],
                      "contenido": aux.elementos(), "grados": dict(grado)})
    orden = []
    while not aux.vacia():
        u = sacar()
        orden.append(u)
        bajan = []
        for v, _ in g.vecinos(u):
            antes = grado[v]
            grado[v] -= 1
            bajan.append((v, antes, grado[v]))
            if grado[v] == 0:
                poner(v)
        if len(aux) > max_tam:
            max_tam = len(aux)
        if traza is not None:
            traza.append({"paso": len(orden), "sale": u, "bajan": bajan,
                          "contenido": aux.elementos(), "grados": dict(grado)})
    if stats is not None:
        stats["max_tam"] = max_tam
    return orden, len(orden) < g.num_vertices()


def formatear_traza(traza, estructura="cola"):
    """Texto de la traza (para consola o para copiar al informe)."""
    et = "Cola (frente → final)" if estructura == "cola" else "Pila (tope → fondo)"
    lineas = [f"{'Paso':<5}{'Sale':<6}{'Grados que bajan':<38}{et}"]
    for t in traza:
        if t["paso"] == 0:
            baja, sale = "Estado inicial (grado 0)", "—"
        else:
            sale = t["sale"]
            baja = "; ".join(f"{v}: {a}→{d}" for v, a, d in t["bajan"]) or "(sin sucesoras)"
        cont = ", ".join(map(str, t["contenido"])) or "(vacía)"
        lineas.append(f"{t['paso']:<5}{str(sale):<6}{baja:<38}{cont}")
    return "\n".join(lineas)


def detectar_ciclo(g):
    """Materias que Kahn no pudo ordenar (las del ciclo y sus dependientes).
    Lista vacía si el grafo es acíclico."""
    orden, hay = kahn(g)
    if hay:
        ordenados = set(orden)
        return [u for u in g.vertices() if u not in ordenados]
    return []


def encontrar_ciclo(g):
    """Un ciclo concreto [a, b, ..., a] o [] si es acíclico. O(V + E).
    DFS iterativo (marcas 0 nuevo / 1 en el camino / 2 cerrado) restringido a las
    materias que Kahn no ordenó; una arista hacia una materia del camino actual
    cierra el ciclo."""
    restantes = set(detectar_ciclo(g))
    if not restantes:
        return []
    estado = {u: 0 for u in restantes}
    for inicio in g.vertices():
        if inicio not in restantes or estado[inicio] != 0:
            continue
        estado[inicio] = 1
        camino = [inicio]
        listas = [[v for v, _ in g.vecinos(inicio) if v in restantes]]
        pos = [0]
        while camino:
            if pos[-1] < len(listas[-1]):
                v = listas[-1][pos[-1]]
                pos[-1] += 1
                if estado[v] == 1:                # arista de retorno: ciclo
                    return camino[camino.index(v):] + [v]
                if estado[v] == 0:
                    estado[v] = 1
                    camino.append(v)
                    listas.append([w for w, _ in g.vecinos(v) if w in restantes])
                    pos.append(0)
            else:
                estado[camino.pop()] = 2
                listas.pop()
                pos.pop()
    return []


def _niveles(g):
    orden, hay = kahn(g)
    if hay:
        raise ValueError("Ciclo de prerrequisitos detectado")
    nivel = {u: 1 for u in g.vertices()}
    previo = {u: None for u in g.vertices()}
    for u in orden:
        for v, _ in g.vecinos(u):
            if nivel[u] + 1 > nivel[v]:
                nivel[v] = nivel[u] + 1
                previo[v] = u
    return nivel, previo


def semestres_minimos(g):
    """Devuelve (nivel, total): nivel[u] = vértices de la ruta más larga que
    termina en u; total = semestres mínimos. O(V + E). ValueError si hay ciclo."""
    nivel, _ = _niveles(g)
    return nivel, (max(nivel.values()) if nivel else 0)


def ruta_critica(g):
    """Ruta más larga del DAG (cadena de materias que fija el mínimo)."""
    nivel, previo = _niveles(g)
    if not nivel:
        return []
    fin = max(g.vertices(), key=lambda u: nivel[u])   # primero en caso de empate
    ruta = []
    while fin is not None:
        ruta.append(fin)
        fin = previo[fin]
    return ruta[::-1]


def plan_por_semestres(g):
    """{semestre: [materias]} con cada materia en su semestre mínimo."""
    nivel, total = semestres_minimos(g)
    plan = {s: [] for s in range(1, total + 1)}
    for u in g.vertices():
        plan[nivel[u]].append(u)
    return plan


def inversiones_de_nivel(orden, nivel):
    """Veces que el semestre baja de una materia a la siguiente en el orden. O(V).
    Con cola siempre es 0 (el orden sale agrupado por semestres)."""
    return sum(1 for a, b in zip(orden, orden[1:]) if nivel[b] < nivel[a])


def es_orden_valido(g, orden):
    """True si el orden contiene todos los vértices y respeta cada arista."""
    pos = {u: i for i, u in enumerate(orden)}
    if len(pos) != g.num_vertices() or len(orden) != len(pos):
        return False
    return all(pos[u] < pos[v] for u, v, _ in g.aristas())


def bfs(g, s):
    """Recorrido en anchura con la Cola propia: O(V + E)."""
    visitado, orden, cola = {s}, [], Cola()
    cola.encolar(s)
    while not cola.vacia():
        u = cola.desencolar()
        orden.append(u)
        for v, _ in g.vecinos(u):
            if v not in visitado:
                visitado.add(v)
                cola.encolar(v)
    return orden


def dfs(g, s):
    """Recorrido en profundidad iterativo con la Pila propia: O(V + E)."""
    visitado, orden, pila = set(), [], Pila()
    pila.push(s)
    while not pila.vacia():
        u = pila.pop()
        if u in visitado:
            continue
        visitado.add(u)
        orden.append(u)
        for v, _ in reversed(g.vecinos(u)):
            if v not in visitado:
                pila.push(v)
    return orden
