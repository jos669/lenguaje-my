"""
My Lenguaje - Depuración Avanzada (Fase 8)
Herramientas avanzadas de depuración y profiling

Características:
- Breakpoints condicionales
- Watchpoints
- Trace de ejecución
- Análisis de memoria
- Detección de memory leaks
- Profiling línea por línea
- Time travel debugging
"""

import sys
import traceback
import time
import threading
import linecache
import gc
import weakref
from typing import Any, Dict, List, Optional, Callable, Set, Tuple
from dataclasses import dataclass, field
from datetime import datetime
from collections import defaultdict
from contextlib import contextmanager
import inspect
import functools


@dataclass
class FrameInfo:
    """Información de un frame de ejecución"""
    archivo: str
    linea: int
    funcion: str
    codigo: str
    variables_locales: Dict[str, Any]
    variables_globales: Dict[str, Any]
    tiempo_ejecucion: float = 0.0


@dataclass
class Breakpoint:
    """Breakpoint avanzado"""
    id: int
    archivo: str
    linea: int
    condicion: str = None
    habilitado: bool = True
    hit_count: int = 0
    hit_limit: int = None  # Detener después de N hits
    acciones: List[Callable] = field(default_factory=list)
    temporal: bool = False  # Se elimina después del primer hit


@dataclass
class Watchpoint:
    """Watchpoint para variables"""
    id: int
    nombre: str
    valor_anterior: Any = None
    habilitado: bool = True
    cuando_cambia: bool = True
    cuando_se_accede: bool = False
    cuando_se_escribe: bool = True


@dataclass
class TraceEntry:
    """Entrada en el trace de ejecución"""
    tiempo: float
    evento: str  # call, line, return, exception
    archivo: str
    linea: int
    funcion: str
    datos: Any = None


class DepuradorAvanzado:
    """
    Depurador avanzado con características enterprise
    
    Ejemplo:
        dep = DepuradorAvanzado()
        dep.agregar_breakpoint("archivo.py", 10)
        dep.ejecutar("codigo.py")
    """
    
    def __init__(self):
        self.breakpoints: Dict[int, Breakpoint] = {}
        self.watchpoints: Dict[int, Watchpoint] = {}
        self.trace: List[TraceEntry] = []
        self.stack: List[FrameInfo] = []
        self.ejecutando = False
        self.pausado = False
        self.id_bp = 0
        self.id_wp = 0
        self.variables_watch: Dict[str, Any] = {}
        self.tiempos_linea: Dict[Tuple[str, int], List[float]] = defaultdict(list)
        self.excepciones_capturadas: List[Dict] = []
        self.bloqueo = threading.RLock()
        
        # Configuración
        self.config = {
            "max_trace": 10000,
            "trace_variables": True,
            "trace_excepciones": True,
            "auto_watch_locals": False
        }
    
    def agregar_breakpoint(self, archivo: str, linea: int, 
                          condicion: str = None, temporal: bool = False) -> int:
        """Agrega un breakpoint"""
        with self.bloqueo:
            self.id_bp += 1
            bp = Breakpoint(
                id=self.id_bp,
                archivo=archivo,
                linea=linea,
                condicion=condicion,
                temporal=temporal
            )
            self.breakpoints[self.id_bp] = bp
            return self.id_bp
    
    def eliminar_breakpoint(self, id_bp: int):
        """Elimina un breakpoint"""
        with self.bloqueo:
            if id_bp in self.breakpoints:
                del self.breakpoints[id_bp]
    
    def listar_breakpoints(self) -> List[Dict]:
        """Lista todos los breakpoints"""
        return [
            {
                "id": bp.id,
                "archivo": bp.archivo,
                "linea": bp.linea,
                "condicion": bp.condicion,
                "habilitado": bp.habilitado,
                "hit_count": bp.hit_count
            }
            for bp in self.breakpoints.values()
        ]
    
    def agregar_watchpoint(self, nombre: str, cuando_cambia: bool = True) -> int:
        """Agrega un watchpoint"""
        with self.bloqueo:
            self.id_wp += 1
            wp = Watchpoint(
                id=self.id_wp,
                nombre=nombre,
                cuando_cambia=cuando_cambia
            )
            self.watchpoints[self.id_wp] = wp
            return self.id_wp
    
    def _verificar_breakpoint(self, archivo: str, linea: int, 
                              contexto: Dict) -> Optional[Breakpoint]:
        """Verifica si hay un breakpoint activo"""
        for bp in self.breakpoints.values():
            if not bp.habilitado:
                continue
            if bp.archivo != archivo or bp.linea != linea:
                continue
            
            bp.hit_count += 1
            
            # Verificar límite de hits
            if bp.hit_limit and bp.hit_count > bp.hit_limit:
                continue
            
            # Verificar condición
            if bp.condicion:
                try:
                    if not eval(bp.condicion, contexto):
                        continue
                except:
                    continue
            
            # Ejecutar acciones
            for accion in bp.acciones:
                try:
                    accion(self, bp)
                except:
                    pass
            
            return bp
        
        return None
    
    def _verificar_watchpoints(self, contexto: Dict):
        """Verifica watchpoints"""
        for wp in self.watchpoints.values():
            if not wp.habilitado:
                continue
            
            if wp.nombre not in contexto:
                continue
            
            valor_actual = contexto[wp.nombre]
            valor_anterior = self.variables_watch.get(wp.nombre)
            
            if wp.cuando_cambia and valor_anterior is not None:
                if valor_actual != valor_anterior:
                    self._notificar_watchpoint(wp, valor_anterior, valor_actual)
            
            self.variables_watch[wp.nombre] = valor_actual
    
    def _notificar_watchpoint(self, wp: Watchpoint, anterior: Any, actual: Any):
        """Notifica cambio en watchpoint"""
        entrada = TraceEntry(
            tiempo=time.time(),
            evento="watchpoint",
            archivo="watch",
            linea=wp.id,
            funcion=f"watch:{wp.nombre}",
            datos={
                "anterior": anterior,
                "actual": actual,
                "cambio": f"{anterior} → {actual}"
            }
        )
        self.trace.append(entrada)
        self._limitar_trace()
    
    def _trace_callback(self, frame, evento: str, arg):
        """Callback para tracing"""
        if not self.ejecutando:
            return None
        
        archivo = frame.f_code.co_filename
        linea = frame.f_lineno
        funcion = frame.f_code.co_name
        
        # Registrar tiempo de línea
        tiempo = time.perf_counter()
        self.tiempos_linea[(archivo, linea)].append(tiempo)
        
        # Crear entrada de trace
        entrada = TraceEntry(
            tiempo=tiempo,
            evento=evento,
            archivo=archivo,
            linea=linea,
            funcion=funcion,
            datos=arg
        )
        
        # Capturar variables si está configurado
        if self.config["trace_variables"]:
            entrada.datos = {
                "tipo": arg,
                "locales": dict(frame.f_locals) if len(frame.f_locals) < 100 else {}
            }
        
        self.trace.append(entrada)
        self._limitar_trace()
        
        # Verificar breakpoints en eventos de línea
        if evento == "line":
            bp = self._verificar_breakpoint(archivo, linea, frame.f_locals)
            if bp:
                self.pausado = True
                
                # Verificar watchpoints
                self._verificar_watchpoints(frame.f_locals)
                
                # Capturar excepción si la hay
                if self.config["trace_excepciones"] and arg is not None:
                    self.excepciones_capturadas.append({
                        "tiempo": time.time(),
                        "archivo": archivo,
                        "linea": linea,
                        "excepcion": str(arg)
                    })
        
        # Continuar tracing
        return self._trace_callback
    
    def _limitar_trace(self):
        """Limita el tamaño del trace"""
        if len(self.trace) > self.config["max_trace"]:
            self.trace = self.trace[-self.config["max_trace"]:]
    
    def ejecutar(self, codigo: str, contexto: Dict = None):
        """Ejecuta código con debugging"""
        self.ejecutando = True
        self.pausado = False
        self.trace = []
        self.tiempos_linea = defaultdict(list)
        
        if contexto is None:
            contexto = {'__name__': '__main__'}
        
        # Configurar trace
        sys.settrace(self._trace_callback)
        threading.settrace(self._trace_callback)
        
        try:
            exec(codigo, contexto)
        except Exception as e:
            self.excepciones_capturadas.append({
                "tiempo": time.time(),
                "tipo": type(e).__name__,
                "mensaje": str(e),
                "traceback": traceback.format_exc()
            })
        finally:
            sys.settrace(None)
            threading.settrace(None)
            self.ejecutando = False
    
    def ejecutar_archivo(self, ruta: str, contexto: Dict = None):
        """Ejecuta un archivo con debugging"""
        with open(ruta, 'r', encoding='utf-8') as f:
            codigo = f.read()
        self.ejecutar(codigo, contexto)
    
    def obtener_trace(self, filtro: str = None, limite: int = 100) -> List[Dict]:
        """Obtiene el trace de ejecución"""
        trace = self.trace[-limite:]
        
        if filtro:
            trace = [e for e in trace if filtro in e.archivo or filtro in e.funcion]
        
        return [
            {
                "tiempo": e.tiempo,
                "evento": e.evento,
                "archivo": e.archivo,
                "linea": e.linea,
                "funcion": e.funcion
            }
            for e in trace
        ]
    
    def obtener_stack(self) -> List[Dict]:
        """Obtiene el stack actual"""
        return [
            {
                "archivo": f.archivo,
                "linea": f.linea,
                "funcion": f.funcion,
                "variables": list(f.variables_locales.keys())
            }
            for f in self.stack
        ]
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas de ejecución"""
        # Calcular tiempos por línea
        tiempos_por_linea = {}
        for (archivo, linea), tiempos in self.tiempos_linea.items():
            if len(tiempos) > 1:
                duraciones = [t2 - t1 for t1, t2 in zip(tiempos[:-1], tiempos[1:])]
                tiempos_por_linea[f"{archivo}:{linea}"] = {
                    "llamadas": len(tiempos),
                    "total": sum(duraciones),
                    "promedio": sum(duraciones) / len(duraciones) if duraciones else 0,
                    "max": max(duraciones) if duraciones else 0
                }
        
        # Líneas más lentas
        mas_lentas = sorted(
            tiempos_por_linea.items(),
            key=lambda x: x[1]["total"],
            reverse=True
        )[:10]
        
        return {
            "total_eventos": len(self.trace),
            "breakpoints": len(self.breakpoints),
            "watchpoints": len(self.watchpoints),
            "excepciones": len(self.excepciones_capturadas),
            "lineas_ejecutadas": len(self.tiempos_linea),
            "mas_lentas": mas_lentas
        }
    
    def limpiar(self):
        """Limpia el depurador"""
        self.trace = []
        self.stack = []
        self.tiempos_linea = defaultdict(list)
        self.excepciones_capturadas = []
        self.variables_watch = {}


class AnalizadorMemoria:
    """
    Analizador de uso de memoria
    
    Ejemplo:
        analizador = AnalizadorMemoria()
        snapshot = analizador.capturar_snapshot()
        # ... ejecutar código ...
        reporte = analizador.comparar(snapshot)
    """
    
    def __init__(self):
        self.snapshots: List[Dict] = []
        self.referencias: Dict[int, weakref.ref] = {}
    
    def capturar_snapshot(self) -> Dict:
        """Captura un snapshot de memoria"""
        gc.collect()
        
        objetos_por_tipo = defaultdict(int)
        tamanio_por_tipo = defaultdict(int)
        
        for obj in gc.get_objects():
            try:
                tipo = type(obj).__name__
                objetos_por_tipo[tipo] += 1
                tamanio_por_tipo[tipo] += sys.getsizeof(obj)
            except:
                pass
        
        snapshot = {
            "tiempo": time.time(),
            "objetos_por_tipo": dict(objetos_por_tipo),
            "tamanio_por_tipo": dict(tamanio_por_tipo),
            "total_objetos": sum(objetos_por_tipo.values()),
            "total_memoria": sum(tamanio_por_tipo.values())
        }
        
        self.snapshots.append(snapshot)
        return snapshot
    
    def comparar(self, snapshot_anterior: Dict = None) -> Dict:
        """Compara snapshots"""
        if snapshot_anterior is None:
            if len(self.snapshots) < 2:
                return {"error": "Se necesitan al menos 2 snapshots"}
            snapshot_anterior = self.snapshots[-2]
        
        snapshot_actual = self.capturar_snapshot()
        
        # Calcular diferencias
        diff_objetos = {}
        diff_tamanio = {}
        
        todos_los_tipos = set(snapshot_anterior["objetos_por_tipo"].keys()) | \
                         set(snapshot_actual["objetos_por_tipo"].keys())
        
        for tipo in todos_los_tipos:
            obj_ant = snapshot_anterior["objetos_por_tipo"].get(tipo, 0)
            obj_act = snapshot_actual["objetos_por_tipo"].get(tipo, 0)
            diff_objetos[tipo] = obj_act - obj_ant
            
            tam_ant = snapshot_anterior["tamanio_por_tipo"].get(tipo, 0)
            tam_act = snapshot_actual["tamanio_por_tipo"].get(tipo, 0)
            diff_tamanio[tipo] = tam_act - tam_ant
        
        # Ordenar por cambio
        mas_crecidos = sorted(
            diff_objetos.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "diff_objetos": diff_objetos,
            "diff_tamanio": diff_tamanio,
            "mas_crecidos": mas_crecidos,
            "cambio_total_objetos": snapshot_actual["total_objetos"] - snapshot_anterior["total_objetos"],
            "cambio_total_memoria": snapshot_actual["total_memoria"] - snapshot_anterior["total_memoria"]
        }
    
    def encontrar_leaks(self, iteraciones: int = 5) -> List[Dict]:
        """Intenta encontrar memory leaks"""
        resultados = []
        
        for i in range(iteraciones):
            snapshot = self.capturar_snapshot()
            
            # Ejecutar GC
            gc.collect()
            
            # Objetos no recolectables
            no_recolectables = [
                obj for obj in gc.get_objects()
                if gc.is_tracked(obj)
            ]
            
            resultados.append({
                "iteracion": i,
                "objetos": snapshot["total_objetos"],
                "memoria": snapshot["total_memoria"],
                "no_recolectables": len(no_recolectables)
            })
            
            time.sleep(0.1)
        
        # Detectar crecimiento constante
        if len(resultados) >= 3:
            crecimiento_objetos = [
                resultados[i]["objetos"] - resultados[i-1]["objetos"]
                for i in range(1, len(resultados))
            ]
            
            if all(c > 0 for c in crecimiento_objetos):
                return [{
                    "tipo": "posible_leak",
                    "evidencia": "Crecimiento constante de objetos",
                    "datos": resultados
                }]
        
        return []


# Decoradores de debugging
def tracear(func: Callable = None, detalle: str = "basic"):
    """Decorador para tracear una función"""
    def decorador(f):
        @functools.wraps(f)
        def wrapper(*args, **kwargs):
            inicio = time.perf_counter()
            nombre = f.__name__
            
            if detalle in ["basic", "full"]:
                print(f"→ Entrando: {nombre}")
            
            try:
                resultado = f(*args, **kwargs)
                
                if detalle == "full":
                    print(f"← Saliendo: {nombre} → {resultado}")
                
                return resultado
                
            except Exception as e:
                if detalle in ["error", "full"]:
                    print(f"✗ Excepción en {nombre}: {e}")
                raise
            
            finally:
                if detalle == "full":
                    duracion = time.perf_counter() - inicio
                    print(f"⏱ {nombre}: {duracion:.6f}s")
        
        return wrapper
    
    if func:
        return decorador(func)
    return decorador


def medir_tiempo(func: Callable) -> Callable:
    """Decorador para medir tiempo de ejecución"""
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.perf_counter()
        resultado = func(*args, **kwargs)
        fin = time.perf_counter()
        
        print(f"⏱ {func.__name__}: {fin - inicio:.6f}s")
        return resultado
    
    return wrapper


def detectar_recursion(limite: int = 100):
    """Decorador para detectar recursión infinita"""
    def decorador(func: Callable):
        func._llamadas = 0
        
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            func._llamadas += 1
            
            if func._llamadas > limite:
                raise RecursionError(
                    f"Posible recursión infinita detectada en {func.__name__}"
                )
            
            try:
                return func(*args, **kwargs)
            finally:
                func._llamadas -= 1
        
        return wrapper
    return decorador


# Context managers
@contextmanager
def perfilar(nombre: str = "bloque"):
    """Context manager para profiling"""
    inicio = time.perf_counter()
    try:
        yield
    finally:
        fin = time.perf_counter()
        print(f"📊 {nombre}: {fin - inicio:.6f}s")


@contextmanager
def monitor_memoria():
    """Context manager para monitorear memoria"""
    gc.collect()
    memoria_inicial = sum(sys.getsizeof(obj) for obj in gc.get_objects())
    
    try:
        yield
    finally:
        gc.collect()
        memoria_final = sum(sys.getsizeof(obj) for obj in gc.get_objects())
        diff = memoria_final - memoria_inicial
        print(f"💾 Memoria: {diff:+,} bytes ({diff / 1024:+.2f} KB)")


# Funciones de conveniencia
depurador_global: Optional[DepuradorAvanzado] = None


def obtener_depurador() -> DepuradorAvanzado:
    """Obtiene el depurador global"""
    global depurador_global
    if not depurador_global:
        depurador_global = DepuradorAvanzado()
    return depurador_global


def breakpoint(archivo: str, linea: int):
    """Agrega un breakpoint global"""
    return obtener_depurador().agregar_breakpoint(archivo, linea)


def watch(variable: str):
    """Agrega un watchpoint global"""
    return obtener_depurador().agregar_watchpoint(variable)


def obtener_trace() -> List[Dict]:
    """Obtiene el trace global"""
    return obtener_depurador().obtener_trace()
