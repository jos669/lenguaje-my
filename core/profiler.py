"""
My Lenguaje - Profiler de Rendimiento (Fase 5)
Analiza el rendimiento del código y genera reportes
"""

import time
import cProfile
import pstats
import io
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, field
from contextlib import contextmanager


@dataclass
class FuncionStats:
    """Estadísticas de una función"""
    nombre: str
    llamadas: int = 0
    tiempo_total: float = 0.0
    tiempo_promedio: float = 0.0
    min: float = float('inf')
    max: float = 0.0


class Profiler:
    """
    Profiler de rendimiento para My Lenguaje
    
    Características:
    - Profiling por función
    - Tiempo de ejecución total
    - Contador de llamadas
    - Reportes detallados
    """
    
    def __init__(self):
        self.funciones: Dict[str, FuncionStats] = {}
        self.tiempo_inicio: float = 0
        self.tiempo_fin: float = 0
        self.activo: bool = False
        self._reporte_cprofile: str = ""
    
    def iniciar(self):
        """Inicia el profiling"""
        self.tiempo_inicio = time.perf_counter()
        self.activo = True
    
    def detener(self):
        """Detiene el profiling"""
        self.tiempo_fin = time.perf_counter()
        self.activo = False
    
    def registrar_funcion(self, nombre: str, tiempo: float):
        """Registra estadísticas de una función"""
        if nombre not in self.funciones:
            self.funciones[nombre] = FuncionStats(nombre=nombre)
        
        stats = self.funciones[nombre]
        stats.llamadas += 1
        stats.tiempo_total += tiempo
        stats.tiempo_promedio = stats.tiempo_total / stats.llamadas
        stats.min = min(stats.min, tiempo)
        stats.max = max(stats.max, tiempo)
    
    def get_reporte(self) -> str:
        """Genera reporte de profiling"""
        if not self.funciones:
            return "No hay datos de profiling"
        
        lineas = []
        lineas.append("=" * 60)
        lineas.append("📊 REPORTE DE PROFILING")
        lineas.append("=" * 60)
        
        tiempo_total = self.tiempo_fin - self.tiempo_inicio
        lineas.append(f"\n⏱️  Tiempo total: {tiempo_total:.4f} segundos")
        lineas.append(f"📈 Funciones analizadas: {len(self.funciones)}")
        lineas.append("")
        
        # Ordenar por tiempo total
        funciones_ordenadas = sorted(
            self.funciones.values(),
            key=lambda x: x.tiempo_total,
            reverse=True
        )
        
        lineas.append("📋 Funciones (ordenadas por tiempo total):")
        lineas.append("-" * 60)
        lineas.append(f"{'Función':<30} {'Llamadas':>8} {'Total(s)':>10} {'Prom(s)':>10}")
        lineas.append("-" * 60)
        
        for func in funciones_ordenadas:
            lineas.append(
                f"{func.nombre:<30} {func.llamadas:>8} {func.tiempo_total:>10.4f} {func.tiempo_promedio:>10.4f}"
            )
        
        lineas.append("-" * 60)
        lineas.append("")
        
        return "\n".join(lineas)
    
    def profilear(self, func: Callable, *args, **kwargs) -> Any:
        """
        Profilea una función específica
        
        Args:
            func: Función a profilear
            *args: Argumentos para la función
            **kwargs: Keyword arguments para la función
            
        Returns:
            Resultado de la función
        """
        self.iniciar()
        
        # Usar cProfile para profiling detallado
        profiler = cProfile.Profile()
        profiler.enable()
        
        try:
            resultado = func(*args, **kwargs)
        finally:
            profiler.disable()
            self.detener()
        
        # Generar stats
        stream = io.StringIO()
        stats = pstats.Stats(profiler, stream=stream)
        stats.sort_stats('cumulative')
        stats.print_stats(20)  # Top 20 funciones
        
        self._reporte_cprofile = stream.getvalue()
        
        return resultado
    
    def get_reporte_cprofile(self) -> str:
        """Retorna reporte de cProfile"""
        return self._reporte_cprofile if self._reporte_cprofile else 'No hay datos de cProfile'


class FuncionProfileada:
    """Decorador para profilear funciones automáticamente"""
    
    def __init__(self, func: Callable, profiler: Profiler = None):
        self.func = func
        self.profiler = profiler or Profiler()
        self.__name__ = func.__name__
    
    def __call__(self, *args, **kwargs):
        inicio = time.perf_counter()
        try:
            return self.func(*args, **kwargs)
        finally:
            fin = time.perf_counter()
            self.profiler.registrar_funcion(
                self.func.__name__,
                fin - inicio
            )


def profile(func: Callable) -> FuncionProfileada:
    """Decorador para profilear funciones"""
    return FuncionProfileada(func)


@contextmanager
def profiling():
    """Context manager para profiling"""
    profiler = Profiler()
    profiler.iniciar()
    try:
        yield profiler
    finally:
        profiler.detener()


# Función de conveniencia
def profilear(codigo: str, contexto: dict = None) -> str:
    """
    Profilea la ejecución de código
    
    Args:
        codigo: Código a ejecutar (debe ser Python válido)
        contexto: Contexto de ejecución
        
    Returns:
        Reporte de profiling
    """
    profiler = Profiler()
    
    profiler.iniciar()
    
    if contexto is None:
        contexto = {'__name__': '__main__'}
    
    try:
        exec(codigo, contexto)
    finally:
        profiler.detener()
    
    return profiler.get_reporte()
