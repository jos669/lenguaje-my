"""
My Lenguaje - Core (Fase 8 - Ultimate Edition)
Módulo principal con todas las características enterprise + IA/ML/NLP + Advanced Features
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

# Fase 7 - AI/ML/NLP
from .ai import (
    RedNeuronal, Neurona, Capa, FuncionActivacion,
    ClasificadorIA, AgenteIA,
    crear_red, cargar_modelo, entrenar_clasificador,
    red_neuronal, entrenar, predecir, guardar_modelo, cargar_modelo_ia,
    inicializar_ia
)
from .ml import (
    RegresionLineal, RegresionLogistica, KMeans, KNN,
    ArbolDecision, RandomForest,
    crear_regresion_lineal, crear_regresion_logistica,
    crear_kmeans, crear_knn, crear_arbol, crear_random_forest,
    evaluar_precision, evaluar_mse, dividir_datos
)
from .nlp import (
    Tokenizador, Stemmer, AnalizadorSentimiento,
    ExtractorPalabrasClave, ChatbotBasico, Token, Documento,
    STOPWORDS_ES,
    tokenizar, stemmear, analizar_sentimiento,
    extraer_palabras_clave, crear_chatbot, conversar
)

# Fase 8 - Advanced Features
from .database import (
    ORM, Conexion, QueryBuilder, Modelo, Campo,
    ModeloManager, ErrorBaseDeDatos,
    conectar_base_de_datos, crear_modelo, ejecutar_migraciones,
    modelo, campo
)
from .plugins import (
    GestorPlugins, PluginBase, MetadataPlugin, ErrorPlugin,
    inicializar_plugins, obtener_gestor, cargar_plugin, ejecutar_hook,
    hook, evento, PluginEjemplo
)
from .distributed import (
    Distribuidor, ColaTareas, Tarea, Worker, EstadoTarea,
    BalanceadorCarga,
    crear_distribuidor, ejecutar_paralelo, procesar_lote,
    mapear, reducir
)
from .cache import (
    Caché, CachéDisco, EntradaCaché,
    LRUStrategy, LFUStrategy, TTLEstrategy,
    en_caché, obtener_cache_global,
    cache_establecer, cache_obtener, cache_eliminar, cache_limpiar
)
from .advanced_debug import (
    DepuradorAvanzado, AnalizadorMemoria, FrameInfo,
    Breakpoint, Watchpoint, TraceEntry,
    tracear, medir_tiempo, detectar_recursion,
    perfilar, monitor_memoria,
    obtener_depurador, breakpoint, watch, obtener_trace
)


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
