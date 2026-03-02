"""
My Lenguaje - Sistema de Caché (Fase 8)
Sistema de caché de alto rendimiento

Características:
- Caché en memoria
- Caché en disco
- Estrategias LRU, LFU, TTL
- Caché distribuida
- Invalidación automática
- Estadísticas de caché
"""

import time
import json
import hashlib
import threading
import os
from typing import Any, Dict, List, Optional, Callable, Type
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from collections import OrderedDict
from pathlib import Path
from functools import wraps


@dataclass
class EntradaCaché:
    """Representa una entrada en caché"""
    clave: str
    valor: Any
    tiempo_creacion: float = field(default_factory=time.time)
    tiempo_expiracion: float = None
    accesos: int = 0
    ultimo_acceso: float = field(default_factory=time.time)
    tamanio: int = 0
    
    def expirado(self) -> bool:
        """Verifica si ha expirado"""
        if self.tiempo_expiracion is None:
            return False
        return time.time() > self.tiempo_expiracion
    
    def tocar(self):
        """Actualiza el tiempo de acceso"""
        self.accesos += 1
        self.ultimo_acceso = time.time()


class EstrategiaEviccion:
    """Clase base para estrategias de evicción"""
    
    def seleccionar(self, entradas: Dict[str, EntradaCaché]) -> Optional[str]:
        """Selecciona una entrada para evicción"""
        raise NotImplementedError


class LRUStrategy(EstrategiaEviccion):
    """Estrategia Least Recently Used"""
    
    def seleccionar(self, entradas: Dict[str, EntradaCaché]) -> Optional[str]:
        if not entradas:
            return None
        
        # El menos recientemente usado
        return min(entradas.keys(), key=lambda k: entradas[k].ultimo_acceso)


class LFUStrategy(EstrategiaEviccion):
    """Estrategia Least Frequently Used"""
    
    def seleccionar(self, entradas: Dict[str, EntradaCaché]) -> Optional[str]:
        if not entradas:
            return None
        
        # El menos frecuentemente usado
        return min(entradas.keys(), key=lambda k: entradas[k].accesos)


class TTLEstrategy(EstrategiaEviccion):
    """Estrategia por tiempo de expiración"""
    
    def seleccionar(self, entradas: Dict[str, EntradaCaché]) -> Optional[str]:
        # Primero buscar expirados
        for clave, entrada in entradas.items():
            if entrada.expirado():
                return clave
        
        # Si no hay expirados, el que expire primero
        if entradas:
            return min(
                entradas.keys(),
                key=lambda k: entradas[k].tiempo_expiracion or float('inf')
            )
        return None


class Caché:
    """
    Sistema de caché en memoria
    
    Ejemplo:
        cache = Caché(capacidad=100, ttl=3600)
        cache.establecer("clave", "valor")
        valor = cache.obtener("clave")
    """
    
    def __init__(self, capacidad: int = 1000, ttl: int = None,
                 estrategia: str = "lru"):
        self.capacidad = capacidad
        self.ttl = ttl  # Tiempo de vida en segundos
        self.entradas: OrderedDict[str, EntradaCaché] = OrderedDict()
        self.bloqueo = threading.RLock()
        
        # Estrategia de evicción
        estrategias = {
            "lru": LRUStrategy(),
            "lfu": LFUStrategy(),
            "ttl": TTLEstrategy()
        }
        self.estrategia = estrategias.get(estrategia, LRUStrategy())
        
        # Estadísticas
        self.estadisticas = {
            "aciertos": 0,
            "fallos": 0,
            "evicciones": 0,
            "expiraciones": 0
        }
    
    def establecer(self, clave: str, valor: Any, ttl: int = None):
        """Establece un valor en caché"""
        with self.bloqueo:
            tiempo_exp = None
            if ttl is not None:
                tiempo_exp = time.time() + ttl
            elif self.ttl:
                tiempo_exp = time.time() + self.ttl
            
            # Calcular tamaño aproximado
            tamanio = len(str(valor).encode('utf-8'))
            
            entrada = EntradaCaché(
                clave=clave,
                valor=valor,
                tiempo_expiracion=tiempo_exp,
                tamanio=tamanio
            )
            
            # Si ya existe, actualizar
            if clave in self.entradas:
                self.entradas[clave] = entrada
                self.entradas.move_to_end(clave)
                return
            
            # Evicción si está lleno
            while len(self.entradas) >= self.capacidad:
                self._eviccionar()
            
            self.entradas[clave] = entrada
    
    def obtener(self, clave: str, defecto: Any = None) -> Any:
        """Obtiene un valor de caché"""
        with self.bloqueo:
            if clave not in self.entradas:
                self.estadisticas["fallos"] += 1
                return defecto
            
            entrada = self.entradas[clave]
            
            # Verificar expiración
            if entrada.expirado():
                self.eliminar(clave)
                self.estadisticas["expiraciones"] += 1
                self.estadisticas["fallos"] += 1
                return defecto
            
            # Actualizar acceso
            entrada.tocar()
            self.entradas.move_to_end(clave)
            
            self.estadisticas["aciertos"] += 1
            return entrada.valor
    
    def eliminar(self, clave: str) -> bool:
        """Elimina una entrada"""
        with self.bloqueo:
            if clave in self.entradas:
                del self.entradas[clave]
                return True
            return False
    
    def _eviccionar(self):
        """Evicciona una entrada"""
        clave = self.estrategia.seleccionar(self.entradas)
        if clave:
            del self.entradas[clave]
            self.estadisticas["evicciones"] += 1
    
    def limpiar(self):
        """Limpia toda la caché"""
        with self.bloqueo:
            self.entradas.clear()
    
    def limpiar_expirados(self):
        """Limpia entradas expiradas"""
        with self.bloqueo:
            expirados = [k for k, e in self.entradas.items() if e.expirado()]
            for clave in expirados:
                del self.entradas[clave]
                self.estadisticas["expiraciones"] += 1
    
    def contiene(self, clave: str) -> bool:
        """Verifica si existe"""
        with self.bloqueo:
            if clave not in self.entradas:
                return False
            return not self.entradas[clave].expirado()
    
    def tamanio(self) -> int:
        """Obtiene el número de entradas"""
        return len(self.entradas)
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas"""
        with self.bloqueo:
            total = self.estadisticas["aciertos"] + self.estadisticas["fallos"]
            tasa_acierto = (
                self.estadisticas["aciertos"] / total * 100
                if total > 0 else 0
            )
            
            return {
                **self.estadisticas,
                "total_operaciones": total,
                "tasa_acierto": f"{tasa_acierto:.2f}%",
                "entradas": len(self.entradas),
                "capacidad": self.capacidad,
                "uso": f"{len(self.entradas) / self.capacidad * 100:.1f}%"
            }
    
    def obtener_todas_claves(self) -> List[str]:
        """Obtiene todas las claves"""
        return list(self.entradas.keys())
    
    def obtener_multiple(self, claves: List[str]) -> Dict[str, Any]:
        """Obtiene múltiples valores"""
        resultado = {}
        for clave in claves:
            valor = self.obtener(clave)
            if valor is not None:
                resultado[clave] = valor
        return resultado


class CachéDisco:
    """
    Caché persistente en disco
    
    Ejemplo:
        cache = CachéDisco("cache_dir/")
        cache.establecer("clave", datos)
    """
    
    def __init__(self, directorio: str, capacidad_mb: int = 100):
        self.directorio = Path(directorio)
        self.directorio.mkdir(parents=True, exist_ok=True)
        self.capacidad_bytes = capacidad_mb * 1024 * 1024
        self.indice: Dict[str, Dict] = {}
        self.bloqueo = threading.RLock()
        
        # Cargar índice existente
        self._cargar_indice()
    
    def _cargar_indice(self):
        """Carga el índice desde disco"""
        archivo_indice = self.directorio / "indice.json"
        if archivo_indice.exists():
            with open(archivo_indice, 'r') as f:
                self.indice = json.load(f)
    
    def _guardar_indice(self):
        """Guarda el índice a disco"""
        archivo_indice = self.directorio / "indice.json"
        with open(archivo_indice, 'w') as f:
            json.dump(self.indice, f, indent=2)
    
    def _archivo_clave(self, clave: str) -> Path:
        """Obtiene la ruta del archivo para una clave"""
        hash_clave = hashlib.md5(clave.encode()).hexdigest()
        return self.directorio / f"{hash_clave}.cache"
    
    def establecer(self, clave: str, valor: Any, ttl: int = None):
        """Establece un valor en caché"""
        with self.bloqueo:
            archivo = self._archivo_clave(clave)
            
            datos = {
                "clave": clave,
                "valor": valor,
                "tiempo_creacion": time.time(),
                "tiempo_expiracion": time.time() + ttl if ttl else None
            }
            
            with open(archivo, 'w') as f:
                json.dump(datos, f)
            
            self.indice[clave] = {
                "archivo": str(archivo),
                "tiempo_creacion": datos["tiempo_creacion"],
                "tiempo_expiracion": datos["tiempo_expiracion"]
            }
            
            self._guardar_indice()
            self._limpiar_exceso()
    
    def obtener(self, clave: str, defecto: Any = None) -> Any:
        """Obtiene un valor de caché"""
        with self.bloqueo:
            if clave not in self.indice:
                return defecto
            
            info = self.indice[clave]
            
            # Verificar expiración
            if info.get("tiempo_expiracion") and time.time() > info["tiempo_expiracion"]:
                self.eliminar(clave)
                return defecto
            
            archivo = Path(info["archivo"])
            if not archivo.exists():
                del self.indice[clave]
                return defecto
            
            try:
                with open(archivo, 'r') as f:
                    datos = json.load(f)
                return datos.get("valor", defecto)
            except:
                return defecto
    
    def eliminar(self, clave: str):
        """Elimina una entrada"""
        with self.bloqueo:
            if clave in self.indice:
                info = self.indice[clave]
                archivo = Path(info["archivo"])
                if archivo.exists():
                    archivo.unlink()
                del self.indice[clave]
                self._guardar_indice()
    
    def _limpiar_exceso(self):
        """Limpia caché si excede capacidad"""
        total = sum(
            Path(info["archivo"]).stat().st_size
            for info in self.indice.values()
            if Path(info["archivo"]).exists()
        )
        
        while total > self.capacidad_bytes and self.indice:
            # Eliminar el más antiguo
            clave_antigua = min(
                self.indice.keys(),
                key=lambda k: self.indice[k]["tiempo_creacion"]
            )
            archivo = Path(self.indice[clave_antigua]["archivo"])
            if archivo.exists():
                total -= archivo.stat().st_size
                archivo.unlink()
            del self.indice[clave_antigua]
        
        self._guardar_indice()
    
    def limpiar(self):
        """Limpia toda la caché"""
        with self.bloqueo:
            for archivo in self.directorio.glob("*.cache"):
                archivo.unlink()
            self.indice = {}
            self._guardar_indice()


# Decorador para caché de funciones
def en_caché(ttl: int = None, clave_prefijo: str = ""):
    """
    Decorador para cachear resultados de funciones
    
    Ejemplo:
        @en_caché(ttl=3600)
        def funcion_costosa(x):
            return x * 2
    """
    cache_memoria = Caché(capacidad=1000, ttl=ttl)
    
    def decorador(func: Callable):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generar clave única
            clave_args = str(args) + str(sorted(kwargs.items()))
            clave = f"{clave_prefijo}{func.__name__}:{hashlib.md5(clave_args.encode()).hexdigest()}"
            
            # Intentar obtener de caché
            resultado = cache_memoria.obtener(clave)
            if resultado is not None:
                return resultado
            
            # Ejecutar función
            resultado = func(*args, **kwargs)
            
            # Guardar en caché
            cache_memoria.establecer(clave, resultado, ttl)
            
            return resultado
        
        wrapper.limpiar_caché = lambda: cache_memoria.limpiar()
        wrapper.obtener_estadisticas = lambda: cache_memoria.obtener_estadisticas()
        
        return wrapper
    
    return decorador


# Caché global
cache_global: Optional[Caché] = None


def obtener_cache_global(capacidad: int = 1000, ttl: int = None) -> Caché:
    """Obtiene la caché global"""
    global cache_global
    if not cache_global:
        cache_global = Caché(capacidad, ttl)
    return cache_global


def cache_establecer(clave: str, valor: Any, ttl: int = None):
    """Establece un valor en caché global"""
    obtener_cache_global().establecer(clave, valor, ttl)


def cache_obtener(clave: str, defecto: Any = None) -> Any:
    """Obtiene un valor de caché global"""
    return obtener_cache_global().obtener(clave, defecto)


def cache_eliminar(clave: str):
    """Elimina un valor de caché global"""
    obtener_cache_global().eliminar(clave)


def cache_limpiar():
    """Limpia la caché global"""
    obtener_cache_global().limpiar()
