"""
My Lenguaje - Traductor Simple (Fase 1)
Traductor basado en reemplazos de palabras clave español → Python
"""

import re
import uuid
from typing import List, Tuple, Dict


class TranslatorError(Exception):
    """Excepción personalizada para errores del traductor"""
    pass


class SimpleTranslator:
    """
    Traductor simple basado en reemplazos de strings.
    Convierte código en español (.my) a Python válido.
    """
    
    # Mapeo de palabras clave español → Python
    KEYWORDS_MAP = {
        # Declaraciones
        'clase': 'class',
        'función': 'def',
        'retornar': 'return',
        
        # Condicionales
        'si': 'if',
        'sino si': 'elif',
        'sino': 'else',
        
        # Bucles
        'para': 'for',
        'en': 'in',
        'mientras': 'while',
        'rango': 'range',
        
        # Excepciones
        'intentar': 'try',
        'excepto': 'except',
        'finalmente': 'finally',
        
        # Importaciones
        'importar': 'import',
        'como': 'as',
        
        # Operadores lógicos
        'y': 'and',
        'o': 'or',
        'no': 'not',
        'verdadero': 'True',
        'falso': 'False',
        'nulo': 'None',
        
        # Builtins
        'imprimir': 'print',
        'entrada': 'input',
        'entero': 'int',
        'flotante': 'float',
        'cadena': 'str',
        'lista': 'list',
        'diccionario': 'dict',
        'longitud': 'len',
    }
    
    def __init__(self):
        self.replacements: List[Tuple[str, str]] = []
        self._build_replacements()
        self.placeholder_prefix = f"_MY_PROT_{uuid.uuid4().hex[:8]}_"
    
    def _build_replacements(self):
        """Construye la lista de reemplazos ordenada por longitud"""
        
        # 1. Manejo especial para 'definir'
        self.replacements.append((r'\bdefinir\s+(\w+)\s*\(', 'def \\1('))
        self.replacements.append((r'\bdefinir\s+(?=[a-zA-Z_]\w*)', ''))
        
        # 2. Palabras clave generales
        sorted_keywords = sorted(
            self.KEYWORDS_MAP.items(),
            key=lambda x: len(x[0]),
            reverse=True
        )
        
        for spanish, python in sorted_keywords:
            if spanish in ('y', 'o', 'no'):
                # Para operadores de una sola letra (y, o), intentamos distinguir 
                # su uso como operador del uso como variable.
                # Como operador, suele estar rodeado de espacios o expresiones.
                # Como variable, suele estar en asignaciones (y = ...) o como argumento (f(y)).
                # Heurística: No reemplazar si le sigue '=' o si está al final de un argumento (seguido de , o ))
                # o si le precede un '.'
                pattern = r'(?<!\.)\b' + re.escape(spanish) + r'\b(?!\s*[=,\)])(?!\.)'
            else:
                pattern = r'\b' + re.escape(spanish) + r'\b'
            
            self.replacements.append((pattern, python))
    
    def _protect_strings_and_comments(self, code: str) -> tuple[str, Dict[str, str]]:
        placeholders = {}
        counter = 0
        patterns = [
            r'""".*?"""', r"'''.*?'''",
            r'"[^"\\]*(?:\\.[^"\\]*)*"', r"'[^'\\]*(?:\\.[^'\\]*)*'",
            r'#[^\n]*'
        ]
        combined_pattern = f"({'|'.join(patterns)})"
        
        def replace_callback(match):
            nonlocal counter
            content = match.group(0)
            placeholder = f"{self.placeholder_prefix}{counter}__"
            placeholders[placeholder] = content
            counter += 1
            return placeholder

        protected_code = re.sub(combined_pattern, replace_callback, code, flags=re.DOTALL)
        return protected_code, placeholders
    
    def _restore_strings_and_comments(self, code: str, placeholders: Dict[str, str]) -> str:
        if not placeholders:
            return code
            
        pattern = re.escape(self.placeholder_prefix) + r'\d+__'
        
        def restore_callback(match):
            token = match.group(0)
            return placeholders.get(token, token)

        return re.sub(pattern, restore_callback, code)

    def translate(self, code: str) -> str:
        if not code:
            return code

        protected_code, placeholders = self._protect_strings_and_comments(code)

        result = protected_code
        for pattern, replacement in self.replacements:
            result = re.sub(pattern, replacement, result)

        result = self._restore_strings_and_comments(result, placeholders)
        return result
    
    def translate_file(self, input_path: str, output_path: str = None) -> str:
        try:
            with open(input_path, 'r', encoding='utf-8') as f:
                code = f.read()
        except FileNotFoundError:
            raise TranslatorError(f"Archivo no encontrado: {input_path}")
        except IOError as e:
            raise TranslatorError(f"Error leyendo archivo: {e}")
        
        translated = self.translate(code)
        
        if output_path:
            try:
                with open(output_path, 'w', encoding='utf-8') as f:
                    f.write(translated)
            except IOError as e:
                raise TranslatorError(f"Error escribiendo archivo: {e}")
        
        return translated
    
    def get_supported_keywords(self) -> dict:
        return self.KEYWORDS_MAP.copy()


def translate(code: str) -> str:
    translator = SimpleTranslator()
    return translator.translate(code)
