"""
My Lenguaje - Sistema de Testing (Fase 5)
Framework de testing integrado para My Lenguaje
"""

import re
import sys
from typing import Any, Callable, Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum


class EstadoTest(Enum):
    """Estado de un test"""
    PENDIENTE = "pendiente"
    PASSED = "✓ passed"
    FAILED = "✗ failed"
    ERROR = "✗ error"


@dataclass
class ResultadoTest:
    """Resultado de un test"""
    nombre: str
    estado: EstadoTest
    mensaje: str = ""
    tiempo: float = 0.0
    linea: int = 0


@dataclass
class SuiteTest:
    """Colección de tests"""
    nombre: str
    tests: List[ResultadoTest] = field(default_factory=list)
    pasados: int = 0
    fallidos: int = 0
    errores: int = 0


class Tester:
    """
    Framework de testing para My Lenguaje
    
    Características:
    - Assertions en español
    - Reporte detallado
    - Setup y teardown
    - Tests parametrizados
    """
    
    def __init__(self):
        self.suites: Dict[str, SuiteTest] = {}
        self.suite_actual: Optional[str] = None
        self.setup_func: Optional[Callable] = None
        self.teardown_func: Optional[Callable] = None
    
    def crear_suite(self, nombre: str):
        """Crea una nueva suite de tests"""
        self.suites[nombre] = SuiteTest(nombre=nombre)
        self.suite_actual = nombre
    
    def agregar_test(self, nombre: str, estado: EstadoTest, mensaje: str = "", tiempo: float = 0.0):
        """Agrega un resultado de test"""
        if self.suite_actual and self.suite_actual in self.suites:
            resultado = ResultadoTest(
                nombre=nombre,
                estado=estado,
                mensaje=mensaje,
                tiempo=tiempo
            )
            self.suites[self.suite_actual].tests.append(resultado)
            
            if estado == EstadoTest.PASSED:
                self.suites[self.suite_actual].pasados += 1
            elif estado == EstadoTest.FAILED:
                self.suites[self.suite_actual].fallidos += 1
            else:
                self.suites[self.suite_actual].errores += 1
    
    def ejecutar_test(self, nombre: str, func: Callable):
        """Ejecuta un test y registra el resultado"""
        import time
        
        inicio = time.perf_counter()
        
        try:
            # Setup
            if self.setup_func:
                self.setup_func()
            
            # Ejecutar test
            func()
            
            # Teardown
            if self.teardown_func:
                self.teardown_func()
            
            tiempo = time.perf_counter() - inicio
            self.agregar_test(nombre, EstadoTest.PASSED, tiempo=tiempo)
            print(f"  ✓ {nombre}")
            
        except AssertionError as e:
            tiempo = time.perf_counter() - inicio
            self.agregar_test(nombre, EstadoTest.FAILED, str(e), tiempo)
            print(f"  ✗ {nombre}: {e}")
            
        except Exception as e:
            tiempo = time.perf_counter() - inicio
            self.agregar_test(nombre, EstadoTest.ERROR, str(e), tiempo)
            print(f"  ✗ {nombre}: ERROR - {e}")
    
    def get_reporte(self) -> str:
        """Genera reporte de tests"""
        lineas = []
        lineas.append("=" * 60)
        lineas.append("🧪 REPORTE DE TESTS")
        lineas.append("=" * 60)
        
        total_tests = 0
        total_pasados = 0
        total_fallidos = 0
        total_errores = 0
        
        for nombre_suite, suite in self.suites.items():
            lineas.append(f"\n📁 Suite: {nombre_suite}")
            lineas.append("-" * 40)
            
            for test in suite.tests:
                estado_icon = "✓" if test.estado == EstadoTest.PASSED else "✗"
                lineas.append(f"  {estado_icon} {test.nombre} ({test.tiempo:.4f}s)")
                
                if test.mensaje and test.estado != EstadoTest.PASSED:
                    lineas.append(f"      {test.mensaje}")
            
            lineas.append("")
            lineas.append(f"  Resultados: {suite.pasados} passed, {suite.fallidos} failed, {suite.errores} errors")
            
            total_tests += len(suite.tests)
            total_pasados += suite.pasados
            total_fallidos += suite.fallidos
            total_errores += suite.errores
        
        lineas.append("")
        lineas.append("=" * 60)
        lineas.append(f"TOTAL: {total_tests} tests, {total_pasados} passed, {total_fallidos} failed, {total_errores} errors")
        lineas.append("=" * 60)
        
        if total_fallidos == 0 and total_errores == 0:
            lineas.append("🎉 ¡Todos los tests pasaron!")
        else:
            lineas.append("⚠️  Algunos tests fallaron")
        
        return "\n".join(lineas)


class Assertions:
    """Assertions para tests"""
    
    @staticmethod
    def afirmar(condicion: bool, mensaje: str = "Aserción fallida"):
        """Afirma que una condición es verdadera"""
        if not condicion:
            raise AssertionError(mensaje)
    
    @staticmethod
    def afirmar_igual(a: Any, b: Any, mensaje: str = None):
        """Afirma que dos valores son iguales"""
        if a != b:
            msg = mensaje or f"Se esperaba {a!r}, pero obtuvo {b!r}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_diferente(a: Any, b: Any, mensaje: str = None):
        """Afirma que dos valores son diferentes"""
        if a == b:
            msg = mensaje or f"Se esperaba valores diferentes, pero ambos son {a!r}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_verdadero(valor: Any, mensaje: str = None):
        """Afirma que un valor es verdadero"""
        if not valor:
            msg = mensaje or f"Se esperaba True, pero obtuvo {valor!r}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_falso(valor: Any, mensaje: str = None):
        """Afirma que un valor es falso"""
        if valor:
            msg = mensaje or f"Se esperaba False, pero obtuvo {valor!r}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_nulo(valor: Any, mensaje: str = None):
        """Afirma que un valor es None"""
        if valor is not None:
            msg = mensaje or f"Se esperaba None, pero obtuvo {valor!r}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_no_nulo(valor: Any, mensaje: str = None):
        """Afirma que un valor no es None"""
        if valor is None:
            msg = mensaje or "Se esperaba un valor no nulo"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_en(contenido: Any, contenedor: Any, mensaje: str = None):
        """Afirma que un contenido está en un contenedor"""
        if contenido not in contenedor:
            msg = mensaje or f"Se esperaba {contenido!r} en {contenedor!r}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_no_en(contenido: Any, contenedor: Any, mensaje: str = None):
        """Afirma que un contenido no está en un contenedor"""
        if contenido in contenedor:
            msg = mensaje or f"Se esperaba {contenido!r} no estuviera en {contenedor!r}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_tipo(valor: Any, tipo: type, mensaje: str = None):
        """Afirma que un valor es de un tipo específico"""
        if not isinstance(valor, tipo):
            msg = mensaje or f"Se esperaba tipo {tipo.__name__}, pero obtuvo {type(valor).__name__}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_longitud(contenedor: Any, longitud: int, mensaje: str = None):
        """Afirma que un contenedor tiene una longitud específica"""
        actual = len(contenedor)
        if actual != longitud:
            msg = mensaje or f"Se esperaba longitud {longitud}, pero obtuvo {actual}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_mayor(a: Any, b: Any, mensaje: str = None):
        """Afirma que a es mayor que b"""
        if not a > b:
            msg = mensaje or f"Se esperaba {a!r} > {b!r}"
            raise AssertionError(msg)
    
    @staticmethod
    def afirmar_menor(a: Any, b: Any, mensaje: str = None):
        """Afirma que a es menor que b"""
        if not a < b:
            msg = mensaje or f"Se esperaba {a!r} < {b!r}"
            raise AssertionError(msg)


# Funciones de conveniencia
def afirmar(condicion: bool, mensaje: str = "Aserción fallida"):
    """Afirma que una condición es verdadera"""
    Assertions.afirmar(condicion, mensaje)


def afirmar_igual(a: Any, b: Any, mensaje: str = None):
    """Afirma que dos valores son iguales"""
    Assertions.afirmar_igual(a, b, mensaje)


def afirmar_diferente(a: Any, b: Any, mensaje: str = None):
    """Afirma que dos valores son diferentes"""
    Assertions.afirmar_diferente(a, b, mensaje)


def afirmar_verdadero(valor: Any, mensaje: str = None):
    """Afirma que un valor es verdadero"""
    Assertions.afirmar_verdadero(valor, mensaje)


def afirmar_falso(valor: Any, mensaje: str = None):
    """Afirma que un valor es falso"""
    Assertions.afirmar_falso(valor, mensaje)


def afirmar_en(contenido: Any, contenedor: Any, mensaje: str = None):
    """Afirma que un contenido está en un contenedor"""
    Assertions.afirmar_en(contenido, contenedor, mensaje)


def afirmar_tipo(valor: Any, tipo: type, mensaje: str = None):
    """Afirma que un valor es de un tipo específico"""
    Assertions.afirmar_tipo(valor, tipo, mensaje)


# Decoradores
def test(func: Callable):
    """Decorador para marcar una función como test"""
    func._es_test = True
    return func


def suite(nombre: str):
    """Decorador para crear una suite de tests"""
    def decorator(cls):
        cls._nombre_suite = nombre
        return cls
    return decorator
