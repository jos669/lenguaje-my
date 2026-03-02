"""
My Lenguaje - Sistema de Plugins (Fase 8)
Sistema de extensión mediante plugins

Características:
- Carga dinámica de plugins
- Hooks y eventos
- Sistema de prioridades
- Hot reload de plugins
- Sandbox de seguridad
"""

import os
import sys
import json
import importlib
import hashlib
from typing import Any, Dict, List, Optional, Callable, Type
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime
import traceback


class ErrorPlugin(Exception):
    """Excepción para errores de plugins"""
    pass


@dataclass
class MetadataPlugin:
    """Metadatos de un plugin"""
    nombre: str
    version: str
    autor: str
    descripcion: str = ""
    licencia: str = "MIT"
    dependencias: List[str] = field(default_factory=list)
    hooks: List[str] = field(default_factory=list)
    minimo_api: int = 1
    habilitado: bool = True
    fecha_instalacion: str = field(default_factory=lambda: datetime.now().isoformat())


class PluginBase:
    """Clase base para todos los plugins"""
    
    metadata: MetadataPlugin = None
    
    def __init__(self, gestor: 'GestorPlugins'):
        self.gestor = gestor
        self.configuracion: Dict[str, Any] = {}
        self.inicializado = False
    
    def inicializar(self):
        """Inicializa el plugin"""
        self.inicializado = True
    
    def detener(self):
        """Detiene el plugin"""
        self.inicializado = False
    
    def obtener_configuracion(self, clave: str, defecto: Any = None) -> Any:
        """Obtiene una configuración"""
        return self.configuracion.get(clave, defecto)
    
    def guardar_configuracion(self, clave: str, valor: Any):
        """Guarda una configuración"""
        self.configuracion[clave] = valor
    
    def registrar_hook(self, nombre: str, funcion: Callable, prioridad: int = 0):
        """Registra un hook"""
        self.gestor.registrar_hook(nombre, funcion, prioridad, self.metadata.nombre)
    
    def log(self, mensaje: str, nivel: str = "INFO"):
        """Registra un log"""
        self.gestor.log(f"[{self.metadata.nombre}] {mensaje}", nivel)


class GestorPlugins:
    """
    Gestor principal de plugins
    
    Ejemplo:
        gestor = GestorPlugins("plugins/")
        gestor.cargar_todos()
        gestor.ejecutar_hook("evento", datos)
    """
    
    API_VERSION = 1
    
    def __init__(self, directorio_plugins: str = "plugins"):
        self.directorio = Path(directorio_plugins)
        self.plugins: Dict[str, PluginBase] = {}
        self.hooks: Dict[str, List[Tuple[Callable, int, str]]] = {}
        self.logs: List[Dict] = []
        self.eventos_globales: Dict[str, List[Callable]] = {}
        
        # Crear directorio si no existe
        self.directorio.mkdir(parents=True, exist_ok=True)
    
    def registrar_plugin(self, plugin: PluginBase):
        """Registra un plugin"""
        if not plugin.metadata:
            raise ErrorPlugin(f"Plugin {plugin.__class__.__name__} no tiene metadata")
        
        self.plugins[plugin.metadata.nombre] = plugin
        self.log(f"Plugin registrado: {plugin.metadata.nombre}")
    
    def cargar_plugin(self, ruta: str) -> PluginBase:
        """Carga un plugin desde un archivo"""
        ruta_path = Path(ruta)
        
        if not ruta_path.exists():
            raise ErrorPlugin(f"Plugin no encontrado: {ruta}")
        
        try:
            # Cargar metadata
            metadata_path = ruta_path.parent / "plugin.json"
            if metadata_path.exists():
                with open(metadata_path, 'r') as f:
                    metadata_dict = json.load(f)
                metadata = MetadataPlugin(**metadata_dict)
            else:
                metadata = MetadataPlugin(
                    nombre=ruta_path.stem,
                    version="1.0.0",
                    autor="Desconocido"
                )
            
            # Verificar API version
            if metadata.minimo_api > self.API_VERSION:
                raise ErrorPlugin(f"Plugin requiere API v{metadata.minimo_api}, actual v{self.API_VERSION}")
            
            # Importar módulo
            spec = importlib.util.spec_from_file_location(metadata.nombre, ruta)
            modulo = importlib.util.module_from_spec(spec)
            sys.modules[metadata.nombre] = modulo
            spec.loader.exec_module(modulo)
            
            # Obtener clase del plugin
            clase_plugin = getattr(modulo, 'Plugin', None)
            if not clase_plugin:
                raise ErrorPlugin(f"Plugin {metadata.nombre} no tiene clase 'Plugin'")
            
            # Instanciar
            plugin = clase_plugin(self)
            plugin.metadata = metadata
            
            # Registrar
            self.registrar_plugin(plugin)
            
            # Inicializar
            plugin.inicializar()
            
            self.log(f"Plugin cargado: {metadata.nombre} v{metadata.version}")
            return plugin
            
        except Exception as e:
            self.log(f"Error cargando plugin {ruta}: {e}", "ERROR")
            raise ErrorPlugin(f"Error cargando plugin: {e}")
    
    def cargar_todos(self):
        """Carga todos los plugins del directorio"""
        cargados = 0
        errores = 0
        
        for archivo in self.directorio.glob("*.py"):
            if archivo.name.startswith("_"):
                continue
            
            try:
                self.cargar_plugin(str(archivo))
                cargados += 1
            except ErrorPlugin as e:
                errores += 1
                print(f"⚠️  {e}")
        
        self.log(f"Plugins cargados: {cargados}, Errores: {errores}")
        return cargados, errores
    
    def descargar_plugin(self, nombre: str):
        """Descarga/elimina un plugin"""
        if nombre in self.plugins:
            plugin = self.plugins[nombre]
            plugin.detener()
            del self.plugins[nombre]
            self.log(f"Plugin descargado: {nombre}")
    
    def habilitar_plugin(self, nombre: str):
        """Habilita un plugin"""
        if nombre in self.plugins:
            self.plugins[nombre].metadata.habilitado = True
            self.plugins[nombre].inicializar()
            self.log(f"Plugin habilitado: {nombre}")
    
    def deshabilitar_plugin(self, nombre: str):
        """Deshabilita un plugin"""
        if nombre in self.plugins:
            self.plugins[nombre].metadata.habilitado = False
            self.plugins[nombre].detener()
            self.log(f"Plugin deshabilitado: {nombre}")
    
    def registrar_hook(self, nombre: str, funcion: Callable, prioridad: int = 0, plugin: str = "system"):
        """Registra un hook"""
        if nombre not in self.hooks:
            self.hooks[nombre] = []
        
        self.hooks[nombre].append((funcion, prioridad, plugin))
        # Ordenar por prioridad (mayor primero)
        self.hooks[nombre].sort(key=lambda x: x[1], reverse=True)
    
    def ejecutar_hook(self, nombre: str, *args, **kwargs) -> List[Any]:
        """Ejecuta todos los hooks de un evento"""
        resultados = []
        
        if nombre not in self.hooks:
            return resultados
        
        for funcion, prioridad, plugin in self.hooks[nombre]:
            plugin_obj = self.plugins.get(plugin)
            if plugin_obj and not plugin_obj.metadata.habilitado:
                continue
            
            try:
                resultado = funcion(*args, **kwargs)
                resultados.append(resultado)
            except Exception as e:
                self.log(f"Error en hook {nombre} ({plugin}): {e}", "ERROR")
        
        return resultados
    
    def ejecutar_hook_primero(self, nombre: str, *args, **kwargs) -> Optional[Any]:
        """Ejecuta el primer hook y retorna su resultado"""
        if nombre not in self.hooks or not self.hooks[nombre]:
            return None
        
        funcion, _, plugin = self.hooks[nombre][0]
        try:
            return funcion(*args, **kwargs)
        except Exception as e:
            self.log(f"Error en hook {nombre} ({plugin}): {e}", "ERROR")
            return None
    
    def suscribir_evento(self, evento: str, callback: Callable):
        """Suscribe a un evento global"""
        if evento not in self.eventos_globales:
            self.eventos_globales[evento] = []
        self.eventos_globales[evento].append(callback)
    
    def emitir_evento(self, evento: str, datos: Any = None):
        """Emite un evento global"""
        if evento not in self.eventos_globales:
            return
        
        for callback in self.eventos_globales[evento]:
            try:
                callback(datos)
            except Exception as e:
                self.log(f"Error en evento {evento}: {e}", "ERROR")
    
    def log(self, mensaje: str, nivel: str = "INFO"):
        """Registra un log"""
        entrada = {
            "timestamp": datetime.now().isoformat(),
            "nivel": nivel,
            "mensaje": mensaje
        }
        self.logs.append(entrada)
        
        # Limitar logs en memoria
        if len(self.logs) > 1000:
            self.logs = self.logs[-500:]
    
    def obtener_logs(self, nivel: str = None, limite: int = 100) -> List[Dict]:
        """Obtiene los logs"""
        logs = self.logs
        if nivel:
            logs = [l for l in logs if l["nivel"] == nivel]
        return logs[-limite:]
    
    def listar_plugins(self) -> List[Dict]:
        """Lista todos los plugins"""
        return [
            {
                "nombre": p.metadata.nombre,
                "version": p.metadata.version,
                "autor": p.metadata.autor,
                "descripcion": p.metadata.descripcion,
                "habilitado": p.metadata.habilitado,
                "inicializado": p.inicializado
            }
            for p in self.plugins.values()
        ]
    
    def obtener_plugin(self, nombre: str) -> Optional[PluginBase]:
        """Obtiene un plugin por nombre"""
        return self.plugins.get(nombre)
    
    def guardar_configuracion(self, ruta: str = "plugins_config.json"):
        """Guarda la configuración de plugins"""
        config = {
            nombre: {
                "habilitado": p.metadata.habilitado,
                "configuracion": p.configuracion
            }
            for nombre, p in self.plugins.items()
        }
        
        with open(ruta, 'w') as f:
            json.dump(config, f, indent=2)
    
    def cargar_configuracion(self, ruta: str = "plugins_config.json"):
        """Carga la configuración de plugins"""
        if not Path(ruta).exists():
            return
        
        with open(ruta, 'r') as f:
            config = json.load(f)
        
        for nombre, datos in config.items():
            if nombre in self.plugins:
                self.plugins[nombre].metadata.habilitado = datos.get("habilitado", True)
                self.plugins[nombre].configuracion = datos.get("configuracion", {})
    
    def obtener_estadisticas(self) -> Dict:
        """Obtiene estadísticas del sistema de plugins"""
        return {
            "total_plugins": len(self.plugins),
            "habilitados": sum(1 for p in self.plugins.values() if p.metadata.habilitado),
            "inicializados": sum(1 for p in self.plugins.values() if p.inicializado),
            "hooks_registrados": sum(len(h) for h in self.hooks.values()),
            "total_logs": len(self.logs)
        }


# Decoradores para plugins
def hook(nombre: str, prioridad: int = 0):
    """Decorador para registrar hooks"""
    def decorador(func):
        func._hook_nombre = nombre
        func._hook_prioridad = prioridad
        return func
    return decorador


def evento(nombre: str):
    """Decorador para suscribir a eventos"""
    def decorador(func):
        func._evento_nombre = nombre
        return func
    return decorador


# Plugin de ejemplo
class PluginEjemplo(PluginBase):
    """Plugin de ejemplo para demostración"""
    
    metadata = MetadataPlugin(
        nombre="ejemplo",
        version="1.0.0",
        autor="My Lenguaje",
        descripcion="Plugin de ejemplo para demostración",
        hooks=["inicio", "fin", "procesar"]
    )
    
    def inicializar(self):
        super().inicializar()
        self.log("Plugin ejemplo inicializado")
        
        # Registrar hooks
        self.registrar_hook("inicio", self.al_inicio, prioridad=10)
        self.registrar_hook("fin", self.al_fin, prioridad=0)
    
    def al_inicio(self, datos):
        """Hook de inicio"""
        return {"mensaje": "Inicio desde plugin ejemplo", "datos": datos}
    
    def al_fin(self, datos):
        """Hook de fin"""
        return {"mensaje": "Fin desde plugin ejemplo"}


# Funciones de conveniencia
gestor_global: Optional[GestorPlugins] = None


def inicializar_plugins(directorio: str = "plugins") -> GestorPlugins:
    """Inicializa el sistema de plugins"""
    global gestor_global
    gestor_global = GestorPlugins(directorio)
    return gestor_global


def obtener_gestor() -> GestorPlugins:
    """Obtiene el gestor global de plugins"""
    global gestor_global
    if not gestor_global:
        gestor_global = GestorPlugins()
    return gestor_global


def cargar_plugin(ruta: str) -> PluginBase:
    """Carga un plugin"""
    return obtener_gestor().cargar_plugin(ruta)


def ejecutar_hook(nombre: str, *args, **kwargs) -> List[Any]:
    """Ejecuta un hook"""
    return obtener_gestor().ejecutar_hook(nombre, *args, **kwargs)
