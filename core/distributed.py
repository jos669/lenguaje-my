"""
My Lenguaje - Computación Distribuida (Fase 8)
Soporte para procesamiento distribuido y paralelo

Características:
- Tareas distribuidas
- Workers remotos
- Balanceo de carga
- Colas de tareas
- Resultados asíncronos
- Tolerancia a fallos
"""

import threading
import multiprocessing
import queue
import time
import json
import hashlib
from typing import Any, Dict, List, Optional, Callable, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, Future
from enum import Enum
import traceback


class EstadoTarea(Enum):
    """Estados de una tarea"""
    PENDIENTE = "pendiente"
    EN_PROGRESO = "en_progreso"
    COMPLETADA = "completada"
    FALLIDA = "fallida"
    CANCELADA = "cancelada"


@dataclass
class Tarea:
    """Representa una tarea distribuida"""
    id: str
    funcion: Callable
    args: tuple = field(default_factory=tuple)
    kwargs: dict = field(default_factory=dict)
    estado: EstadoTarea = EstadoTarea.PENDIENTE
    resultado: Any = None
    error: str = None
    prioridad: int = 0
    tiempo_creacion: str = field(default_factory=lambda: datetime.now().isoformat())
    tiempo_inicio: str = None
    tiempo_fin: str = None
    worker_id: str = None
    reintentos: int = 0
    max_reintentos: int = 3
    
    def ejecutar(self) -> Any:
        """Ejecuta la tarea"""
        try:
            self.estado = EstadoTarea.EN_PROGRESO
            self.tiempo_inicio = datetime.now().isoformat()
            self.resultado = self.funcion(*self.args, **self.kwargs)
            self.estado = EstadoTarea.COMPLETADA
            self.tiempo_fin = datetime.now().isoformat()
            return self.resultado
        except Exception as e:
            self.estado = EstadoTarea.FALLIDA
            self.error = str(e)
            self.tiempo_fin = datetime.now().isoformat()
            raise
    
    def a_dict(self) -> dict:
        """Convierte a diccionario (sin la función)"""
        return {
            "id": self.id,
            "args": self.args,
            "kwargs": self.kwargs,
            "estado": self.estado.value,
            "resultado": self.resultado,
            "error": self.error,
            "prioridad": self.prioridad,
            "tiempo_creacion": self.tiempo_creacion,
            "tiempo_inicio": self.tiempo_inicio,
            "tiempo_fin": self.tiempo_fin,
            "worker_id": self.worker_id,
            "reintentos": self.reintentos
        }


@dataclass
class Worker:
    """Representa un worker/procesador"""
    id: str
    tipo: str = "thread"  # thread, process, remote
    estado: str = "activo"  # activo, ocupado, inactivo
    tareas_completadas: int = 0
    tareas_fallidas: int = 0
    ultima_actividad: str = field(default_factory=lambda: datetime.now().isoformat())
    carga_actual: int = 0
    capacidad_maxima: int = 10
    
    def disponible(self) -> bool:
        """Verifica si está disponible"""
        return self.estado == "activo" and self.carga_actual < self.capacidad_maxima


class ColaTareas:
    """
    Cola de tareas con prioridades
    
    Ejemplo:
        cola = ColaTareas()
        cola.encolar(tarea)
        tarea = cola.desencolar()
    """
    
    def __init__(self, capacidad_maxima: int = 1000):
        self.cola: queue.PriorityQueue = queue.PriorityQueue(maxsize=capacidad_maxima)
        self.capacidad = capacidad_maxima
        self.tareas_procesadas = 0
    
    def encolar(self, tarea: Tarea):
        """Encola una tarea"""
        # Prioridad negativa para que las de mayor prioridad salgan primero
        self.cola.put((-tarea.prioridad, time.time(), tarea))
    
    def desencolar(self, timeout: float = 1.0) -> Optional[Tarea]:
        """Desencola una tarea"""
        try:
            _, _, tarea = self.cola.get(timeout=timeout)
            return tarea
        except queue.Empty:
            return None
    
    def vacia(self) -> bool:
        """Verifica si está vacía"""
        return self.cola.empty()
    
    def tamanio(self) -> int:
        """Obtiene el tamaño de la cola"""
        return self.cola.qsize()
    
    def vaciar(self):
        """Vacía la cola"""
        while not self.cola.empty():
            try:
                self.cola.get_nowait()
            except queue.Empty:
                break


class Distribuidor:
    """
    Distribuidor de tareas para procesamiento paralelo/distribuido
    
    Ejemplo:
        dist = Distribuidor(workers=4)
        resultado = dist.ejecutar(funcion, args)
    """
    
    def __init__(self, workers: int = 4, tipo: str = "thread"):
        self.num_workers = workers
        self.tipo = tipo  # thread, process, hybrid
        self.workers: List[Worker] = []
        self.cola = ColaTareas()
        self.tareas: Dict[str, Tarea] = {}
        self.ejecutandose = False
        self.hilos: List[threading.Thread] = []
        self.pool_executor = None
        self.futuros: Dict[str, Future] = {}
        
        self._inicializar_workers()
    
    def _inicializar_workers(self):
        """Inicializa los workers"""
        for i in range(self.num_workers):
            worker = Worker(
                id=f"worker_{i}",
                tipo=self.tipo
            )
            self.workers.append(worker)
    
    def iniciar(self):
        """Inicia el distribuidor"""
        self.ejecutandose = True
        
        if self.tipo == "process":
            self.pool_executor = ProcessPoolExecutor(max_workers=self.num_workers)
        else:
            self.pool_executor = ThreadPoolExecutor(max_workers=self.num_workers)
        
        # Iniciar hilos de workers
        for worker in self.workers:
            hilo = threading.Thread(target=self._loop_worker, args=(worker,), daemon=True)
            hilo.start()
            self.hilos.append(hilo)
    
    def detener(self, esperar: bool = True):
        """Detiene el distribuidor"""
        self.ejecutandose = False
        
        if self.pool_executor:
            self.pool_executor.shutdown(wait=esperar)
        
        for hilo in self.hilos:
            if esperar:
                hilo.join(timeout=2.0)
    
    def _loop_worker(self, worker: Worker):
        """Loop principal de un worker"""
        while self.ejecutandose:
            if not worker.disponible():
                time.sleep(0.1)
                continue
            
            tarea = self.cola.desencolar(timeout=0.5)
            if not tarea:
                continue
            
            worker.estado = "ocupado"
            worker.carga_actual += 1
            tarea.worker_id = worker.id
            
            try:
                tarea.ejecutar()
                worker.tareas_completadas += 1
            except Exception as e:
                tarea.reintentos += 1
                worker.tareas_fallidas += 1
                
                if tarea.reintentos < tarea.max_reintentos:
                    # Reencolar para reintento
                    tarea.estado = EstadoTarea.PENDIENTE
                    self.cola.encolar(tarea)
                else:
                    tarea.error = str(e)
            
            finally:
                worker.carga_actual -= 1
                worker.estado = "activo"
                worker.ultima_actividad = datetime.now().isoformat()
    
    def ejecutar(self, funcion: Callable, *args, prioridad: int = 0, **kwargs) -> str:
        """
        Ejecuta una tarea asíncronamente
        
        Returns:
            ID de la tarea
        """
        id_tarea = hashlib.md5(
            f"{funcion.__name__}{args}{kwargs}{time.time()}".encode()
        ).hexdigest()[:12]
        
        tarea = Tarea(
            id=id_tarea,
            funcion=funcion,
            args=args,
            kwargs=kwargs,
            prioridad=prioridad
        )
        
        self.tareas[id_tarea] = tarea
        self.cola.encolar(tarea)
        
        return id_tarea
    
    def ejecutar_y_esperar(self, funcion: Callable, *args, timeout: float = None, **kwargs) -> Any:
        """Ejecuta y espera el resultado"""
        if self.pool_executor:
            futuro = self.pool_executor.submit(funcion, *args, **kwargs)
            return futuro.result(timeout=timeout)
        else:
            # Ejecución sincrónica
            return funcion(*args, **kwargs)
    
    def ejecutar_multiple(self, funcion: Callable, lista_args: List[tuple]) -> List[str]:
        """Ejecuta múltiples tareas"""
        ids = []
        for args in lista_args:
            id_tarea = self.ejecutar(funcion, *args)
            ids.append(id_tarea)
        return ids
    
    def obtener_resultado(self, id_tarea: str, timeout: float = None) -> Any:
        """Obtiene el resultado de una tarea"""
        tarea = self.tareas.get(id_tarea)
        if not tarea:
            raise ValueError(f"Tarea {id_tarea} no encontrada")
        
        inicio = time.time()
        while tarea.estado not in [EstadoTarea.COMPLETADA, EstadoTarea.FALLIDA]:
            if timeout and (time.time() - inicio) > timeout:
                raise TimeoutError(f"Timeout esperando tarea {id_tarea}")
            time.sleep(0.1)
        
        if tarea.estado == EstadoTarea.FALLIDA:
            raise Exception(f"Tarea fallida: {tarea.error}")
        
        return tarea.resultado
    
    def obtener_estado(self, id_tarea: str) -> EstadoTarea:
        """Obtiene el estado de una tarea"""
        tarea = self.tareas.get(id_tarea)
        return tarea.estado if tarea else None
    
    def cancelar(self, id_tarea: str) -> bool:
        """Cancela una tarea"""
        tarea = self.tareas.get(id_tarea)
        if tarea and tarea.estado == EstadoTarea.PENDIENTE:
            tarea.estado = EstadoTarea.CANCELADA
            return True
        return False
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del distribuidor"""
        return {
            "total_tareas": len(self.tareas),
            "pendientes": self.cola.tamanio(),
            "completadas": sum(1 for t in self.tareas.values() if t.estado == EstadoTarea.COMPLETADA),
            "fallidas": sum(1 for t in self.tareas.values() if t.estado == EstadoTarea.FALLIDA),
            "workers": {
                "total": len(self.workers),
                "activos": sum(1 for w in self.workers if w.disponible()),
                "ocupados": sum(1 for w in self.workers if w.estado == "ocupado")
            }
        }
    
    def mapear(self, funcion: Callable, iterable: List) -> List[Any]:
        """Ejecuta función en paralelo sobre un iterable"""
        if self.pool_executor:
            return list(self.pool_executor.map(funcion, iterable))
        else:
            return [funcion(item) for item in iterable]
    
    def reducir(self, funcion: Callable, iterable: List, inicial: Any = None) -> Any:
        """Reduce un iterable usando función"""
        if inicial is None:
            resultado = iterable[0]
            iterable = iterable[1:]
        else:
            resultado = inicial
        
        for item in iterable:
            resultado = funcion(resultado, item)
        
        return resultado
    
    def mapear_reducir(self, map_func: Callable, reduce_func: Callable, 
                       iterable: List, inicial: Any = None) -> Any:
        """Patrón Map-Reduce"""
        # Fase Map (paralela)
        resultados_map = self.mapear(map_func, iterable)
        
        # Fase Reduce
        return self.reducir(reduce_func, resultados_map, inicial)


class BalanceadorCarga:
    """
    Balanceador de carga para distribución de trabajo
    
    Ejemplo:
        balanceador = BalanceadorCarga()
        worker = balanceador.seleccionar_worker()
    """
    
    def __init__(self, estrategia: str = "round_robin"):
        self.estrategia = estrategia  # round_robin, least_connections, weighted
        self.workers: List[Worker] = []
        self.indice_rr = 0
        self.pesos: Dict[str, int] = {}
    
    def agregar_worker(self, worker: Worker, peso: int = 1):
        """Agrega un worker"""
        self.workers.append(worker)
        self.pesos[worker.id] = peso
    
    def seleccionar_worker(self) -> Optional[Worker]:
        """Selecciona un worker según la estrategia"""
        disponibles = [w for w in self.workers if w.disponible()]
        
        if not disponibles:
            return None
        
        if self.estrategia == "round_robin":
            worker = disponibles[self.indice_rr % len(disponibles)]
            self.indice_rr += 1
            return worker
        
        elif self.estrategia == "least_connections":
            return min(disponibles, key=lambda w: w.carga_actual)
        
        elif self.estrategia == "weighted":
            # Selección ponderada
            total_peso = sum(self.pesos.get(w.id, 1) for w in disponibles)
            import random
            aleatorio = random.uniform(0, total_peso)
            acumulado = 0
            
            for worker in disponibles:
                acumulado += self.pesos.get(worker.id, 1)
                if aleatorio <= acumulado:
                    return worker
        
        return disponibles[0]


# Funciones de conveniencia en español
def crear_distribuidor(workers: int = 4, tipo: str = "thread") -> Distribuidor:
    """Crea un distribuidor de tareas"""
    return Distribuidor(workers, tipo)


def ejecutar_paralelo(funcion: Callable, lista_args: List[tuple],
                      workers: int = 4) -> List[Any]:
    """Ejecuta función en paralelo"""
    dist = Distribuidor(workers)
    dist.iniciar()

    try:
        ids = dist.ejecutar_multiple(funcion, lista_args)
        resultados = []

        for id_tarea in ids:
            resultado = dist.obtener_resultado(id_tarea, timeout=30)
            resultados.append(resultado)

        return resultados
    finally:
        dist.detener()


def procesar_lote(funcion: Callable, datos: List, tamanio_lote: int = 10,
                  workers: int = 4) -> List[Any]:
    """Procesa datos en lotes"""
    lotes = [datos[i:i+tamanio_lote] for i in range(0, len(datos), tamanio_lote)]

    def procesar_lote(lote):
        return [funcion(item) for item in lote]

    return ejecutar_paralelo(procesar_lote, [(lote,) for lote in lotes], workers)


def mapear(funcion: Callable, iterable: List, workers: int = 4) -> List[Any]:
    """Mapea función sobre iterable"""
    dist = Distribuidor(workers)
    dist.iniciar()
    try:
        return dist.mapear(funcion, iterable)
    finally:
        dist.detener()


def reducir(funcion: Callable, iterable: List, inicial: Any = None) -> Any:
    """Reduce iterable con función"""
    dist = Distribuidor(1)
    return dist.reducir(funcion, iterable, inicial)
