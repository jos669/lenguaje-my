"""
My Lenguaje - Traductor Fase 3
Combina traductor mejorado con nuevas características de Fase 3
"""

import re
import ast as py_ast
from typing import Dict, Optional

from .translator_v2 import TraductorMejorado, TranslatorError


class TraductorFase3:
    """
    Traductor de Fase 3 con:
    - Traductor mejorado como base
    - Errores detallados en español
    - Soporte para tipos opcionales
    - Análisis estático de código
    """
    
    def __init__(self):
        self.traductor_base = TraductorMejorado()
    
    def traducir(self, codigo: str) -> str:
        """Traduce código My a Python"""
        return self.traductor_base.traducir(codigo)
    
    def analizar(self, codigo: str) -> dict:
        """
        Analiza el código y retorna información detallada
        
        Returns:
            Diccionario con información del análisis
        """
        resultado = {
            'valido': False,
            'errores': [],
            'estadisticas': {},
            'tipos': {}
        }
        
        # Intentar traducir para validar
        try:
            self.traducir(codigo)
            resultado['valido'] = True
        except TranslatorError as e:
            resultado['errores'].append({
                'tipo': 'traduccion',
                'mensaje': str(e)
            })
            return resultado
        
        # Analizar estadísticas
        lineas = codigo.split('\n')
        resultado['estadisticas'] = {
            'lineas_totales': len(lineas),
            'lineas_codigo': sum(1 for l in lineas if l.strip() and not l.strip().startswith('#')),
            'lineas_comentarios': sum(1 for l in lineas if l.strip().startswith('#')),
            'lineas_vacias': sum(1 for l in lineas if not l.strip())
        }
        
        # Detectar tipos usados (Fase 3)
        patron_tipo = r':\s*(entero|flotante|cadena|booleano|lista|dict)\b'
        matches = re.findall(patron_tipo, codigo)
        resultado['tipos'] = {tipo: matches.count(tipo) for tipo in set(matches)}
        
        return resultado
    
    def traducir_archivo(self, input_path: str, output_path: str = None) -> str:
        """Traduce un archivo .my"""
        return self.traductor_base.traducir_archivo(input_path, output_path)
    
    def ejecutar(self, codigo: str, contexto: dict = None):
        """Ejecuta código My directamente"""
        codigo_python = self.traducir(codigo)
        
        if contexto is None:
            contexto = {'__name__': '__main__'}
        
        exec(codigo_python, contexto)
        return contexto
    
    def ejecutar_archivo(self, input_path: str, contexto: dict = None):
        """Ejecuta un archivo .my"""
        with open(input_path, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        return self.ejecutar(codigo, contexto)


# Funciones de conveniencia
def traducir(codigo: str) -> str:
    """Traduce código My a Python"""
    traductor = TraductorFase3()
    return traductor.traducir(codigo)


def analizar(codigo: str) -> dict:
    """Analiza código My y retorna información"""
    traductor = TraductorFase3()
    return traductor.analizar(codigo)


def ejecutar(codigo: str, contexto: dict = None):
    """Ejecuta código My directamente"""
    traductor = TraductorFase3()
    return traductor.ejecutar(codigo, contexto)
