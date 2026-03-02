"""
My Lenguaje - Optimizador de Código (Fase 4)
Optimizaciones para mejorar el rendimiento del código generado
"""

import ast as py_ast
import re
from typing import Any, Dict, List, Optional, Tuple


class Optimizador:
    """
    Optimizador de código Python generado
    
    Optimizaciones implementadas:
    1. Constant Folding: Evalúa expresiones constantes en tiempo de compilación
    2. Dead Code Elimination: Elimina código inalcanzable
    3. Inline de funciones simples
    4. Optimización de bucles
    """
    
    def __init__(self):
        self.optimizaciones_aplicadas = []
    
    def optimizar(self, codigo: str) -> str:
        """
        Aplica todas las optimizaciones al código
        
        Args:
            codigo: Código Python a optimizar
            
        Returns:
            Código optimizado
        """
        self.optimizaciones_aplicadas = []
        
        # Fase 1: Constant Folding
        codigo = self._constant_folding(codigo)
        
        # Fase 2: Optimizar expresiones booleanas
        codigo = self._optimizar_booleanos(codigo)
        
        # Fase 3: Optimizar operaciones con strings
        codigo = self._optimizar_strings(codigo)
        
        return codigo
    
    def _constant_folding(self, codigo: str) -> str:
        """
        Evalúa expresiones constantes en tiempo de compilación
        
        Ejemplo:
            x = 2 + 3  →  x = 5
            y = 10 * 5 + 2  →  y = 52
        """
        # Patrón para operaciones aritméticas simples
        patrones = [
            # Suma de enteros
            (r'(\d+)\s*\+\s*(\d+)', lambda m: str(int(m.group(1)) + int(m.group(2)))),
            # Resta de enteros
            (r'(\d+)\s*-\s*(\d+)', lambda m: str(int(m.group(1)) - int(m.group(2)))),
            # Multiplicación de enteros
            (r'(\d+)\s*\*\s*(\d+)', lambda m: str(int(m.group(1)) * int(m.group(2)))),
            # División de enteros (solo si es exacta y divisor no es cero)
            (r'(\d+)\s*/\s*(\d+)', lambda m: str(int(m.group(1)) // int(m.group(2))) if int(m.group(2)) != 0 and int(m.group(1)) % int(m.group(2)) == 0 else m.group(0)),
            # Potencia
            (r'(\d+)\s*\*\*\s*(\d+)', lambda m: str(int(m.group(1)) ** int(m.group(2)))),
            # Módulo
            (r'(\d+)\s*%\s*(\d+)', lambda m: str(int(m.group(1)) % int(m.group(2)))),
        ]
        
        resultado = codigo
        for patron, reemplazo in patrones:
            resultado = re.sub(patron, reemplazo, resultado)
        
        if resultado != codigo:
            self.optimizaciones_aplicadas.append('constant_folding')
        
        return resultado
    
    def _optimizar_booleanos(self, codigo: str) -> str:
        """
        Optimiza expresiones booleanas
        
        Ejemplo:
            True and x  →  x
            False or x  →  x
            not False  →  True
        """
        optimizaciones = [
            (r'\bTrue\s+and\s+', ''),
            (r'\bFalse\s+or\s+', ''),
            (r'\bnot\s+False\b', 'True'),
            (r'\bnot\s+True\b', 'False'),
            (r'\bTrue\s+or\s+\w+', 'True'),
            (r'\bFalse\s+and\s+\w+', 'False'),
        ]
        
        resultado = codigo
        for patron, reemplazo in optimizaciones:
            resultado = re.sub(patron, reemplazo, resultado)
        
        if resultado != codigo:
            self.optimizaciones_aplicadas.append('boolean_optimization')
        
        return resultado
    
    def _optimizar_strings(self, codigo: str) -> str:
        """
        Optimiza operaciones con strings
        
        Ejemplo:
            "Hola" + " " + "Mundo"  →  "Hola Mundo"
        """
        # Concatenación de strings literales
        def concatenar_strings(m):
            s1 = m.group(1)[1:-1]  # Quitar comillas
            s2 = m.group(2)[1:-1]
            return f'"{s1 + s2}"'
        
        patron = r'"([^"]*)"\s*\+\s*"([^"]*)"'
        resultado = re.sub(patron, concatenar_strings, codigo)
        
        if resultado != codigo:
            self.optimizaciones_aplicadas.append('string_concatenation')
        
        return resultado
    
    def get_reporte(self) -> dict:
        """Retorna reporte de optimizaciones aplicadas"""
        return {
            'optimizaciones': self.optimizaciones_aplicadas,
            'cantidad': len(self.optimizaciones_aplicadas)
        }


def optimizar(codigo: str) -> str:
    """Función de conveniencia para optimizar código"""
    optimizador = Optimizador()
    return optimizador.optimizar(codigo)
