import threading
import time
import random
from datetime import datetime
import os

lock = threading.Lock()
FILE = "fat_db.txt"

# directorio actual (0 = raíz)
GPWD = 0

def _cargar_registros() -> list[dict]:
    """Lee fat_db.txt y devuelve todos los registros como lista de dicts."""
    registros = []
    with lock:
        with open(FILE, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                partes = [p.strip() for p in linea.split("|")]
                if len(partes) != 6:
                    continue
                registros.append({
                    "id":       int(partes[0]),
                    "nombre":   partes[1],
                    "tipo":     partes[2],
                    "padre":    int(partes[3]),
                    "permisos": partes[4],
                    "tamanio":  partes[5],
                })
    return registros


def _guardar_registros(registros: list[dict]) -> None:
    """Sobreescribe fat_db.txt con la lista de registros dada."""
    with lock:
        with open(FILE, "w", encoding="utf-8") as f:
            for r in registros:
                linea = (f"{r['id']} | {r['nombre']} | {r['tipo']} | "
                         f"{r['padre']} | {r['permisos']} | {r['tamanio']}\n")
                f.write(linea)


def _siguiente_id() -> int:
    """Devuelve el próximo ID disponible (max actual + 1)."""
    registros = _cargar_registros()
    if not registros:
        return 1
    return max(r["id"] for r in registros) + 1


# Inicialización del sistema FAT
def inicializar_fat() -> None:
    """Crea fat_db.txt con el directorio raíz si no existe o está vacío."""
    if not os.path.exists(FILE) or os.path.getsize(FILE) == 0:
        with open(FILE, "w", encoding="utf-8") as f:
            f.write("0 | / | DIR | -1 | rwx | -\n")


# Funciones de escritura 
def escritura(id: int, nombre: str, tipo: str, padre: int, permisos: str, tamanio):
    linea = f"{id} | {nombre} | {tipo} | {padre} | {permisos} | {tamanio}\n"
    with lock:
        with open(FILE, "a", encoding="utf-8") as f:
            f.write(linea)


def ejecutar(fn, args: tuple):
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



if __name__ == "__main__":
    inicializar_fat()
    registros = _cargar_registros()
    print("fat_db.txt inicializado. Registros cargados:")
    for r in registros:
        print(r)
    print(f"GPWD = {GPWD}")
    print(f"Siguiente ID disponible: {_siguiente_id()}")
