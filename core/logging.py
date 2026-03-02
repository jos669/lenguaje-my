"""
My Lenguaje - Logging Integrado (Fase 6)
Sistema de logging profesional
"""

import sys
import time
from datetime import datetime
from enum import Enum
from typing import Optional


class NivelLog(Enum):
    """Niveles de logging"""
    DEBUG = 10
    INFO = 20
    ADVERTENCIA = 30
    ERROR = 40
    CRITICO = 50


class Logger:
    """
    Sistema de logging para My Lenguaje
    """
    
    COLORES = {
        'DEBUG': '\033[36m',
        'INFO': '\033[32m',
        'ADVERTENCIA': '\033[33m',
        'ERROR': '\033[31m',
        'CRITICO': '\033[35m',
        'RESET': '\033[0m'
    }
    
    def __init__(self, nombre: str = "my", nivel: NivelLog = NivelLog.INFO):
        self.nombre = nombre
        self.nivel = nivel
        self.handlers = []
        self.formato = "%(fecha)s - %(nombre)s - %(nivel)s: %(mensaje)s"
    
    def configurar(self, nivel: str = "INFO", archivo: str = None, formato: str = None):
        """Configura el logger"""
        self.nivel = NivelLog[nivel.upper()]
        if formato:
            self.formato = formato
        if archivo:
            self.agregar_handler_archivo(archivo)
        else:
            self.agregar_handler_consola()
    
    def agregar_handler_consola(self):
        self.handlers.append(('consola', None))
    
    def agregar_handler_archivo(self, archivo: str):
        self.handlers.append(('archivo', archivo))
    
    def _formatear(self, nivel: str, mensaje: str) -> str:
        fecha = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        formato_str = self.formato
        formato_str = formato_str.replace('%(fecha)s', fecha)
        formato_str = formato_str.replace('%(nombre)s', self.nombre)
        formato_str = formato_str.replace('%(nivel)s', nivel)
        formato_str = formato_str.replace('%(mensaje)s', mensaje)
        return formato_str
    
    def _escribir(self, nivel: str, mensaje: str):
        mensaje_formateado = self._formatear(nivel, mensaje)
        for tipo, destino in self.handlers:
            if tipo == 'consola':
                color = self.COLORES.get(nivel, '')
                reset = self.COLORES['RESET']
                print(f"{color}{mensaje_formateado}{reset}")
            elif tipo == 'archivo':
                try:
                    with open(destino, 'a', encoding='utf-8') as f:
                        f.write(mensaje_formateado + '\n')
                except:
                    pass
    
    def debug(self, mensaje: str):
        if self.nivel.value <= NivelLog.DEBUG.value:
            self._escribir('DEBUG', mensaje)
    
    def info(self, mensaje: str):
        if self.nivel.value <= NivelLog.INFO.value:
            self._escribir('INFO', mensaje)
    
    def advertencia(self, mensaje: str):
        if self.nivel.value <= NivelLog.ADVERTENCIA.value:
            self._escribir('ADVERTENCIA', mensaje)
    
    def error(self, mensaje: str):
        if self.nivel.value <= NivelLog.ERROR.value:
            self._escribir('ERROR', mensaje)
    
    def critico(self, mensaje: str):
        if self.nivel.value <= NivelLog.CRITICO.value:
            self._escribir('CRITICO', mensaje)


# Logger global
_logger_global: Optional[Logger] = None


def configurar_logging(nivel: str = "INFO", archivo: str = None):
    """Configura el logging global"""
    global _logger_global
    _logger_global = Logger("my")
    _logger_global.configurar(nivel, archivo)
    return _logger_global


def obtener_logger() -> Logger:
    """Obtiene el logger global"""
    global _logger_global
    if _logger_global is None:
        _logger_global = Logger("my")
        _logger_global.configurar()
    return _logger_global


def debug(mensaje: str):
    obtener_logger().debug(mensaje)


def info(mensaje: str):
    obtener_logger().info(mensaje)


def advertencia(mensaje: str):
    obtener_logger().advertencia(mensaje)


def error(mensaje: str):
    obtener_logger().error(mensaje)


def critico(mensaje: str):
    obtener_logger().critico(mensaje)
