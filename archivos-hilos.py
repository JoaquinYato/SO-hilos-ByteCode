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

# Comandos de navegación y creación
def cmd_mkdir(nombre: str) -> None:
    global GPWD
    registros = _cargar_registros()
    # Verificar que no exista ya un directorio con ese nombre en el directorio actual
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD and r["tipo"] == "DIR":
            print(f"Error: el directorio '{nombre}' ya existe.")
            return
    nuevo_id = _siguiente_id()
    escritura(nuevo_id, nombre, "DIR", GPWD, "rwx", "-")
    print(f"Directorio '{nombre}' creado correctamente.")

def cmd_cd(destino: str) -> None:
    global GPWD
    registros = _cargar_registros()

    if destino == "..":
        if GPWD == 0:
            print("Ya estás en el directorio raíz.")
            return
        actual = next((r for r in registros if r["id"] == GPWD), None)
        if actual:
            GPWD = actual["padre"]
            ruta = _ruta_actual(registros)
            print(f"Directorio actual cambiado a: {ruta}")
        return

    # Buscar el directorio destino dentro del directorio actual
    for r in registros:
        if r["nombre"] == destino and r["padre"] == GPWD and r["tipo"] == "DIR":
            GPWD = r["id"]
            ruta = _ruta_actual(registros)
            print(f"Directorio actual cambiado a: {ruta}")
            return

    print(f"Error: directorio '{destino}' no encontrado.")


def cmd_touch(nombre: str) -> None:
    global GPWD
    registros = _cargar_registros()
    # Verificar que no exista ya un archivo con ese nombre en el directorio actual
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD and r["tipo"] == "FILE":
            print(f"Error: el archivo '{nombre}' ya existe.")
            return
    nuevo_id = _siguiente_id()
    escritura(nuevo_id, nombre, "FILE", GPWD, "rw-", "0")
    print(f"Archivo '{nombre}' creado correctamente.")


def _ruta_actual(registros: list[dict]) -> str:
    """Construye la ruta absoluta del directorio actual recorriendo padres."""
    partes = []
    nodo = GPWD
    while nodo != 0:
        r = next((x for x in registros if x["id"] == nodo), None)
        if not r:
            break
        partes.append(r["nombre"])
        nodo = r["padre"]
    partes.reverse()
    return "/" + "/".join(partes) if partes else "/"

#Prueba de funcionamientos basicos
if __name__ == "__main__":
    inicializar_fat()
    print("=== Test ===")
    cmd_mkdir("DIR3")
    cmd_cd("DIR3")
    cmd_touch("a.txt")
    cmd_touch("b.txt")
    cmd_touch("a.txt")   # debe mostrar error
    cmd_cd("..")
    cmd_cd("noexiste")   # debe mostrar error
    print(f"Siguiente ID disponible: {_siguiente_id()}")
