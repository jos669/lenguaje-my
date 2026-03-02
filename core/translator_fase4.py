"""
My Lenguaje - Traductor Fase 4
Con optimizaciones y características avanzadas
"""

import re
from typing import Dict, Optional

from .translator_v2 import TraductorMejorado, TranslatorError
from .optimizer import Optimizador


class TraductorFase4:
    """
    Traductor de Fase 4 con:
    - Todas las características de Fase 3
    - Optimizaciones de código
    - Decoradores
    - Context managers
    - F-strings
    - Async/await
    """
    
    def __init__(self):
        self.traductor_base = TraductorMejorado()
        self.optimizador = Optimizador()
    
    def traducir(self, codigo: str, optimizar: bool = True) -> str:
        """
        Traduce código My a Python con optimizaciones opcionales
        
        Args:
            codigo: Código fuente en español
            optimizar: Si True, aplica optimizaciones
            
        Returns:
            Código Python (optimizado si se solicita)
        """
        # Fase 1: Traducir
        codigo_python = self.traductor_base.traducir(codigo)
        
        # Fase 2: Características avanzadas de Fase 4
        codigo_python = self._traducir_caracteristicas_fase4(codigo_python, codigo)
        
        # Fase 3: Optimizar (opcional)
        if optimizar:
            codigo_python = self.optimizador.optimizar(codigo_python)
        
        return codigo_python
    
    def _traducir_caracteristicas_fase4(self, codigo_python: str, codigo_original: str) -> str:
        """Traduce características avanzadas de Fase 4"""
        
        # 1. Decoradores (@decorador)
        codigo_python = self._traducir_decoradores(codigo_python)
        
        # 2. Context managers (con ... como ...)
        codigo_python = self._traducir_context_managers(codigo_python)
        
        # 3. F-strings (f"..." o F"...")
        codigo_python = self._traducir_fstrings(codigo_python, codigo_original)
        
        # 4. Async/await (asíncrono/esperar)
        codigo_python = self._traducir_async_await(codigo_python)
        
        return codigo_python
    
    def _traducir_decoradores(self, codigo: str) -> str:
        """
        Los decoradores ya se traducen directamente porque usamos '@'
        pero podemos añadir aliases en español
        """
        # No se necesita traducción especial, '@' es universal
        return codigo
    
    def _traducir_context_managers(self, codigo: str) -> str:
        """
        Traduce 'con ... como ...' a 'with ... as ...'
        
        Ejemplo:
            con abrir("archivo.txt") como f:
                contenido = f.leer()
            
            →
            
            with open("archivo.txt") as f:
                content = f.read()
        """
        # 'con' → 'with' (solo cuando es statement, no en otras contextos)
        # Patrón: 'con' seguido de expresión y 'como'
        patron = r'\bcon\b(?=\s+.+\s+como\s+)'
        codigo = re.sub(patron, 'with', codigo)
        
        # 'como' → 'as' (solo en contexto de 'with')
        # Esto ya se maneja en el traductor base
        
        return codigo
    
    def _traducir_fstrings(self, codigo_python: str, codigo_original: str) -> str:
        """
        Soporta f-strings en el código original
        
        El código Python ya soporta f-strings nativamente,
        así que solo necesitamos asegurar que se preserven.
        """
        # No se necesita traducción especial
        return codigo_python
    
    def _traducir_async_await(self, codigo: str) -> str:
        """
        Traduce 'asíncrono' y 'esperar' a 'async' y 'await'
        
        Ejemplo:
            asíncrono función obtener_datos():
                datos = esperar leer_archivo()
            
            →
            
            async def obtener_datos():
                datos = await leer_archivo()
        """
        # 'asíncrono' → 'async'
        codigo = re.sub(r'\basíncrono\b', 'async', codigo)
        
        # 'esperar' → 'await'
        codigo = re.sub(r'\besperar\b', 'await', codigo)
        
        return codigo
    
    def analizar(self, codigo: str) -> dict:
        """
        Analiza el código y retorna información detallada
        
        Incluye información de optimizaciones aplicables
        """
        from .translator_fase3 import TraductorFase3
        
        resultado = TraductorFase3().analizar(codigo)
        
        # Añadir información de optimizaciones potenciales
        resultado['optimizaciones'] = {
            'constant_folding': self._detectar_constant_folding(codigo),
            'string_concat': self._detectar_string_concat(codigo),
            'boolean_opt': self._detectar_boolean_opt(codigo)
        }
        
        return resultado
    
    def _detectar_constant_folding(self, codigo: str) -> bool:
        """Detecta si hay expresiones constantes plegables"""
        patron = r'\d+\s*[\+\-\*/]\s*\d+'
        return bool(re.search(patron, codigo))
    
    def _detectar_string_concat(self, codigo: str) -> bool:
        """Detecta si hay concatenación de strings"""
        patron = r'"[^"]*"\s*\+\s*"[^"]*"'
        return bool(re.search(patron, codigo))
    
    def _detectar_boolean_opt(self, codigo: str) -> bool:
        """Detecta si hay expresiones booleanas optimizables"""
        patron = r'\b(True|False)\s+(and|or)\s+'
        return bool(re.search(patron, codigo))
    
    def traducir_archivo(self, input_path: str, output_path: str = None, optimizar: bool = True) -> str:
        """Traduce un archivo .my con optimización opcional"""
        with open(input_path, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        traducido = self.traducir(codigo, optimizar=optimizar)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(traducido)
        
        return traducido
    
    def ejecutar(self, codigo: str, contexto: dict = None, optimizar: bool = True):
        """Ejecuta código My con optimización opcional"""
        codigo_python = self.traducir(codigo, optimizar=optimizar)
        
        if contexto is None:
            contexto = {'__name__': '__main__'}
        
        exec(codigo_python, contexto)
        return contexto
    
    def ejecutar_archivo(self, input_path: str, contexto: dict = None, optimizar: bool = True):
        """Ejecuta un archivo .my con optimización opcional"""
        with open(input_path, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        return self.ejecutar(codigo, contexto, optimizar=optimizar)


# Funciones de conveniencia
def traducir(codigo: str, optimizar: bool = True) -> str:
    """Traduce código My a Python"""
    traductor = TraductorFase4()
    return traductor.traducir(codigo, optimizar=optimizar)


def analizar(codigo: str) -> dict:
    """Analiza código My"""
    traductor = TraductorFase4()
    return traductor.analizar(codigo)


def ejecutar(codigo: str, contexto: dict = None, optimizar: bool = True):
    """Ejecuta código My"""
    traductor = TraductorFase4()
    return traductor.ejecutar(codigo, contexto, optimizar=optimizar)
