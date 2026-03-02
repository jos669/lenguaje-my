"""
My Lenguaje - Core (Fase 6)
Módulo principal con todas las características enterprise
"""

# Fase 1-5
from .translator_fase4 import TraductorFase4
from .translator_v2 import TranslatorError
from .optimizer import Optimizador
from .debugger import Debugger
from .profiler import Profiler
from .testing import Tester

# Importaciones con alias para evitar conflictos
from .translator_fase4 import traducir as _traducir_f4
from .profiler import profilear as _profilear_f5

# Fase 6
from .lsp import LSPServer, iniciar_lsp
from .packagemanager import GestorPaquetes
from .hotreload import HotReloader, ejecutar_con_hot_reload
from .docs import GeneradorDocumentacion, generar_documentacion
from .logging import Logger, configurar_logging, obtener_logger
from .logging import debug, info, advertencia, error, critico
from .web import AplicacionWeb, Solicitud, Respuesta, crear_aplicacion


class Traductor:
    """Traductor principal de My Lenguaje (Fase 6)"""
    
    def __init__(self):
        self.traductor = TraductorFase4()
        self.optimizador = Optimizador()
        self.debugger = Debugger()
        self.profiler = Profiler()
        self.tester = Tester()
    
    def traducir(self, codigo: str, optimizar: bool = True) -> str:
        return self.traductor.traducir(codigo, optimizar=optimizar)
    
    def traducir_archivo(self, input_path: str, output_path: str = None, optimizar: bool = True) -> str:
        return self.traductor.traducir_archivo(input_path, output_path, optimizar=optimizar)
    
    def analizar(self, codigo: str) -> dict:
        return self.traductor.analizar(codigo)
    
    def optimizar(self, codigo: str) -> str:
        return self.optimizador.optimizar(codigo)
    
    def debug(self, codigo: str, contexto: dict = None) -> dict:
        return self.debugger.ejecutar_con_debug(codigo, contexto)
    
    def profilear(self, codigo: str, contexto: dict = None) -> str:
        return _profilear_f5(codigo, contexto)
    
    def test(self, nombre_suite: str) -> Tester:
        self.tester.crear_suite(nombre_suite)
        return self.tester
    
    def ejecutar(self, codigo: str, contexto: dict = None, optimizar: bool = True):
        return self.traductor.ejecutar(codigo, contexto, optimizar=optimizar)
    
    def ejecutar_archivo(self, input_path: str, contexto: dict = None, optimizar: bool = True):
        return self.traductor.ejecutar_archivo(input_path, contexto, optimizar=optimizar)


# Funciones de conveniencia
def traducir(codigo: str, optimizar: bool = True) -> str:
    traductor = Traductor()
    return traductor.traducir(codigo, optimizar=optimizar)


def ejecutar(codigo: str, contexto: dict = None, optimizar: bool = True):
    traductor = Traductor()
    return traductor.ejecutar(codigo, contexto, optimizar=optimizar)


def analizar(codigo: str) -> dict:
    traductor = Traductor()
    return traductor.analizar(codigo)


def optimizar(codigo: str) -> str:
    traductor = Traductor()
    return traductor.optimizar(codigo)


def debug(codigo: str, contexto: dict = None):
    traductor = Traductor()
    return traductor.debug(codigo, contexto)


def profilear(codigo: str, contexto: dict = None) -> str:
    return _profilear_f5(codigo, contexto)


def test(nombre_suite: str) -> Tester:
    traductor = Traductor()
    return traductor.test(nombre_suite)
