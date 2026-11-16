# Proyecto 4 · Planificador de prerrequisitos del plan de estudios

Estructura de Datos · Ingeniería de Sistemas · Universidad Piloto de Colombia (Seccional del Alto Magdalena) · 2026-II
Integrantes: Nikole Daniela Ospina Mayorga · Isabella Ortega Torrado

Modela las asignaturas y sus prerrequisitos como un **DAG**, genera un orden válido de
cursado con el **algoritmo de Kahn** (cola o pila propias), detecta ciclos y calcula los
**semestres mínimos** y la **ruta crítica**.

## Cómo ejecutar (solo requiere Python 3.11 o superior)
La aplicación **no necesita instalar nada más**: usa solo la biblioteca estándar.

**VS Code (Windows, Mac o Linux):** `Archivo > Abrir carpeta` → elegir `proyecto-grafos-4`,
abrir `main.py` y pulsar el botón ▶ (arriba a la derecha). El menú aparece en la terminal
integrada; escribir un número y Enter.

**Por terminal** (dentro de la carpeta del proyecto):
```
python3 main.py        (Mac / Linux)
py main.py             (Windows; si falla, usar: python main.py)
```
En Windows también sirve hacer doble clic en `ejecutar_windows.bat`.

**Pruebas automáticas** (instalan pytest y networkx, solo para validar):
```
python3 -m pip install -r requirements.txt
python3 probar.py           # o: python3 -m pytest -v   (54 pruebas)
```
(`probar.py` también se ejecuta con el botón ▶ de VS Code.)

**Experimentos de rendimiento** (requieren `pip install -r requirements.txt`):
```
python3 -m rendimiento.medir            # completo, hasta n = 128 000 (~30 s)
python3 -m rendimiento.medir --rapido   # prueba corta, hasta n = 16 000
python3 -m rendimiento.figura_ciclo     # figura del plan con ciclo
```
Genera `resultados.json`, `experimento_a/b/c.csv` y las figuras PNG en `rendimiento/`.
Los tiempos dependen del equipo: al repetirlos en otro computador, actualizar el informe.

## Estructura
```
main.py, probar.py   atajos para el botón ▶ (menú / pruebas)
src/estructuras.py   Nodo, NodoDoble, Cola, Pila, MonticuloMin (sin deque ni heapq)
src/grafo.py         Grafo (lista de adyacencia) y GrafoMatriz
src/algoritmos.py    kahn(cola|pila), detectar_ciclo, encontrar_ciclo, semestres_minimos,
                     ruta_critica, plan_por_semestres, inversiones_de_nivel, bfs, dfs
src/persistencia.py  cargar_plan (2 CSV), cargar_plan_csv (1 CSV), guardar_plan_csv
src/generador.py     DAG aleatorios (permutación + aristas hacia adelante)
src/app.py           menú de consola
datos/               materias.csv, prerrequisitos.csv y datos/planes/ (6 planes de prueba)
tests/               pytest (incluye validación cruzada contra networkx)
rendimiento/         medir.py, figura_ciclo.py, CSV, JSON y figuras
```
Regla del curso: sin `collections.deque`, `heapq` ni `networkx` en `src/`
(networkx se usa solo en `tests/` y `rendimiento/` para validar, graficar y comparar tiempos).

## Formato de datos
- `datos/planes/*.csv` (un archivo): `codigo,nombre,prerrequisitos` con prerrequisitos
  separados por `;` (vacío si no hay). Incluye un plan válido, tres con ciclos
  (largo, directo, aislado) y dos con datos inválidos (auto-prerrequisito y materia desconocida).
- `materias.csv` (`codigo,nombre,periodo`) + `prerrequisitos.csv` (`prerrequisito,materia`).
Los prerrequisitos de la instancia son un supuesto didáctico; se pueden reemplazar por
los del reglamento oficial sin tocar el código.
