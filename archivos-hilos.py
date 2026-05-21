import threading
import time
import random
from datetime import datetime
import os

lock = threading.Lock()
FILE = "fat_db.txt"

GPWD = 0

def cargarRegistro() -> list[dict]:
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


def guardarRegistro(registros: list[dict]) -> None:
    with lock:
        with open(FILE, "w", encoding="utf-8") as f:
            for r in registros:
                linea = (f"{r['id']} | {r['nombre']} | {r['tipo']} | "
                         f"{r['padre']} | {r['permisos']} | {r['tamanio']}\n")
                f.write(linea)


def siguienteID() -> int:
    registros = cargarRegistro()
    if not registros:
        return 1
    return max(r["id"] for r in registros) + 1


def inicializar_fat() -> None:
    if not os.path.exists(FILE) or os.path.getsize(FILE) == 0:
        with open(FILE, "w", encoding="utf-8") as f:
            f.write("0 | / | DIR | -1 | rwx | -\n")


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


def ImprimirResultado(resultado: dict):
    if "error" in resultado:
        print(f"  ✗ {resultado['error']}")
    elif "ok" in resultado:
        print(f"  ✓ {resultado['ok']}")
    elif "salida" in resultado:
        print(resultado["salida"])



def cmd_mkdir(nombre: str) -> None:
    global GPWD
    registros = cargarRegistro()
    
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD and r["tipo"] == "DIR":
            print(f"Error: el directorio '{nombre}' ya existe.")
            return
    nuevo_id = siguienteID()
    escritura(nuevo_id, nombre, "DIR", GPWD, "rwx", "-")
    print(f"Directorio '{nombre}' creado correctamente.")

def cmd_cd(destino: str) -> None:
    global GPWD
    registros = cargarRegistro()

    if destino == "..":
        if GPWD == 0:
            print("Ya estás en el directorio raíz.")
            return
        actual = next((r for r in registros if r["id"] == GPWD), None)
        if actual:
            GPWD = actual["padre"]
            ruta = rutaActual(registros)
            print(f"Directorio actual cambiado a: {ruta}")
        return

    
    for r in registros:
        if r["nombre"] == destino and r["padre"] == GPWD and r["tipo"] == "DIR":
            GPWD = r["id"]
            ruta = rutaActual(registros)
            print(f"Directorio actual cambiado a: {ruta}")
            return

    print(f"Error: directorio '{destino}' no encontrado.")


def cmd_touch(nombre: str) -> None:
    global GPWD
    registros = cargarRegistro()
    
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD and r["tipo"] == "FILE":
            print(f"Error: el archivo '{nombre}' ya existe.")
            return
    nuevo_id = siguienteID()
    escritura(nuevo_id, nombre, "FILE", GPWD, "rw-", "0")
    print(f"Archivo '{nombre}' creado correctamente.")


def rutaActual(registros: list[dict]) -> str:
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


def cmd_ls(detallado: bool = False) -> None:
    registros = cargarRegistro()
    hijos = [r for r in registros if r["padre"] == GPWD]
    if not hijos:
        print("(directorio vacío)")
        return
    if detallado:
        print(f"{'ID':<4} | {'TIPO':<4} | {'PERMISOS':<8} | {'TAMAÑO':<6} | NOMBRE")
        for r in hijos:
            print(f"{r['id']:<4} | {r['tipo']:<4} | {r['permisos']:<8} | {r['tamanio']:<6} | {r['nombre']}")
    else:
        for r in hijos:
            print(r["nombre"])

def cmd_chmod(permisos: str, nombre: str) -> None:
    if len(permisos) != 3 or not all(c in "rwx-" for c in permisos):
        print("Error: permisos inválidos. Formato esperado: rwx, r--, rw-, etc.")
        return
    registros = cargarRegistro()
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD:
            r["permisos"] = permisos
            guardarRegistro(registros)
            print(f"Permisos de '{nombre}' cambiados a {permisos}.")
            return
    print(f"Error: '{nombre}' no encontrado en el directorio actual.")

def cmd_rm(nombre: str) -> None:
    registros = cargarRegistro()
    for r in registros:
        if r["nombre"] == nombre and r["padre"] == GPWD and r["tipo"] == "FILE":
            registros.remove(r)
            guardarRegistro(registros)
            print(f"Archivo '{nombre}' eliminado correctamente.")
            return
    print(f"Error: archivo '{nombre}' no encontrado en el directorio actual.")

def crearArchivoHilo(n: int) -> None:
    nombre = f"hilo_{n}.txt"
    print(f"Hilo {n} creando archivo {nombre}")
    nuevo_id = siguienteID()
    escritura(nuevo_id, nombre, "FILE", GPWD, "rw-", "0")

def cmd_test_hilos() -> None:
    print("Iniciando prueba concurrente con hilos...")
    hilos = [threading.Thread(target=crearArchivoHilo, args=(i,)) for i in range(1, 6)]
    for h in hilos:
        h.start()
    for h in hilos:
        h.join()
    print("Todos los hilos finalizaron correctamente.")

def mostrarCabecera() -> None:
    print("========================================")
    print("       SIMULADOR FAT EN PYTHON          ")
    print("========================================")
    print("Sistema FAT inicializado correctamente.")
    registros = cargarRegistro()
    print(f"Directorio actual: {rutaActual(registros)}")
    print("Comandos disponibles:")
    print("  mkdir <nombre>   cd <nombre>   cd ..")
    print("  touch <nombre>   ls            ls -l")
    print("  chmod <permisos> <nombre>      rm <nombre>")
    print("  test_hilos       exit")

def main() -> None:
    inicializar_fat()
    mostrarCabecera()

    while True:
        registros = cargarRegistro()
        ruta = rutaActual(registros)
        try:
            entrada = input(f"\n[{ruta}]> ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nSaliendo del simulador FAT...")
            break

        if not entrada:
            continue

        partes = entrada.split()
        cmd = partes[0]

        if cmd == "exit":
            print("Saliendo del simulador FAT...")
            break
        elif cmd == "mkdir" and len(partes) == 2:
            cmd_mkdir(partes[1])
        elif cmd == "cd" and len(partes) == 2:
            cmd_cd(partes[1])
        elif cmd == "touch" and len(partes) == 2:
            cmd_touch(partes[1])
        elif cmd == "ls" and len(partes) == 1:
            cmd_ls()
        elif cmd == "ls" and len(partes) == 2 and partes[1] == "-l":
            cmd_ls(detallado=True)
        elif cmd == "chmod" and len(partes) == 3:
            cmd_chmod(partes[1], partes[2])
        elif cmd == "rm" and len(partes) == 2:
            cmd_rm(partes[1])
        elif cmd == "test_hilos":
            cmd_test_hilos()
        else:
            print(f"Comando no reconocido: '{entrada}'")

if __name__ == "__main__":
    main()
