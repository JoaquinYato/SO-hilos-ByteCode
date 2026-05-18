import threading
import time
import random
from datetime import datetime

lock = threading.Lock()
FILE = "fat_db.txt"

f = open("fat_db.txt","x")

#Ejemplificacion de la parte de la escritura para el documento

def escritura (id: int, nombre:str, padre:int, permisos:str, tamanio:int):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S.%f")[:-3]
    linea = f"{id} | {nombre} | {padre} | {permisos} | {tamanio} | [{timestamp}] "
    while lock:
        with open(FILE, "a", encoding="Uft-8") as f:
            f.write(linea)

#ejecucion de los hilos

def ejecutar (nombre:str, datos:dict):
    resultado = {}
    hilo = threading.Thread(target=fn, args=(*args, resultado))
    hilo.start()
    hilo.join()  # el programa espera al hilo antes de continuar
    return resultado
        
# Impresion de los los resultados de operaciones por si se ejecutaron o no
        
def _imprimir_resultado(resultado: dict):
    if "error" in resultado:
        print(f"  ✗ {resultado['error']}")
    elif "ok" in resultado:
        print(f"  ✓ {resultado['ok']}")
    elif "salida" in resultado:
        print(resultado["salida"])    
