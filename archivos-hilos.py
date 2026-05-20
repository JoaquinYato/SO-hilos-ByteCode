import threading
import time
import random
from datetime import datetime

lock = threading.Lock()
FILE = "fat_db.txt"

# Bug fix: eliminado open("fat_db.txt","x") a nivel raíz — reventaba si el archivo
# ya existía. La creación del archivo se maneja en la inicialización del sistema (paso 2).


def escritura(id: int, nombre: str, tipo: str, padre: int, permisos: str, tamanio):
    # Bug fix: agregado campo 'tipo' (DIR/FILE) que exige la consigna.
    linea = f"{id} | {nombre} | {tipo} | {padre} | {permisos} | {tamanio}\n"
    # Bug fix: 'while lock' era loop infinito → reemplazado por 'with lock'.
    # Bug fix: encoding "Uft-8" → "utf-8".
    with lock:
        with open(FILE, "a", encoding="utf-8") as f:
            f.write(linea)


def ejecutar(fn, args: tuple):
    # Bug fix: fn y args ahora son parámetros explícitos en lugar de referencias rotas.
    resultado = {}
    hilo = threading.Thread(target=fn, args=(*args, resultado))
    hilo.start()
    hilo.join()
    return resultado


def _imprimir_resultado(resultado: dict):
    if "error" in resultado:
        print(f"  ✗ {resultado['error']}")
    elif "ok" in resultado:
        print(f"  ✓ {resultado['ok']}")
    elif "salida" in resultado:
        print(resultado["salida"])
