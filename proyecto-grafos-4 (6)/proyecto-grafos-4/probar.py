"""Ejecuta todas las pruebas (pytest). VS Code: abrir este archivo y pulsar ▶."""
import sys

try:
    import pytest
except ImportError:
    sys.exit("Falta pytest: ejecute  python3 -m pip install -r requirements.txt")

if __name__ == "__main__":
    sys.exit(pytest.main(["-v"]))
