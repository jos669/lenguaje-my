"""
My Lenguaje - Traductor Mejorado (Fase 1.5)
Traductor que protege strings/comentarios y evita bugs de Fase 1

Mejoras:
- Sin colisiones de placeholders (usa UUID único)
- No traduce keywords dentro de strings/comentarios
- Manejo correcto de 'y', 'o', 'no' como variables
- Validación del código Python generado
"""

import re
import uuid
import ast as py_ast
from typing import Dict


class TranslatorError(Exception):
    """Excepción para errores del traductor"""
    pass


class TraductorMejorado:
    """
    Traductor mejorado que protege strings y comentarios
    """
    
    # Keywords que se traducen (mapeo español → python)
    KEYWORD_MAP = {
        'sino si': 'elif',
        'clase': 'class',
        'función': 'def',
        'retornar': 'return',
        'sino': 'else',
        'si': 'if',
        'para': 'for',
        'en': 'in',
        'mientras': 'while',
        'rango': 'range',
        'intentar': 'try',
        'excepto': 'except',
        'finalmente': 'finally',
        'importar': 'import',
        'como': 'as',
        'verdadero': 'True',
        'falso': 'False',
        'nulo': 'None',
        'imprimir': 'print',
        'entrada': 'input',
        'entero': 'int',
        'flotante': 'float',
        'cadena': 'str',
        'lista': 'list',
        'diccionario': 'dict',
        'longitud': 'len',
        # Fase 4
        'asíncrono': 'async',
        'esperar': 'await',
        'con': 'with',
    }
    
    def __init__(self):
        self.placeholders: Dict[str, str] = {}
    
    def traducir(self, codigo: str) -> str:
        """Traduce código My a Python"""
        self.placeholders = {}
        
        # Fase 1: Proteger strings y comentarios con UUIDs únicos
        codigo_protegido = self._proteger(codigo)
        
        # Fase 2: Aplicar traducciones
        codigo_traducido = self._traducir_keywords(codigo_protegido)
        
        # Fase 2.5: Traducir tipos a Python
        codigo_traducido = self._traducir_tipos(codigo_traducido)
        
        # Fase 3: Restaurar strings y comentarios
        codigo_final = self._restaurar(codigo_traducido)
        
        # Fase 4: Validar Python generado
        self._validar_python(codigo_final)
        
        return codigo_final
    
    def _proteger(self, codigo: str) -> str:
        """Protege strings y comentarios reemplazándolos con placeholders"""
        result = codigo
        
        # Proteger strings de triple comilla primero
        def save_triple_double(m):
            key = f"__MYSTR_{uuid.uuid4().hex[:8]}__"
            self.placeholders[key] = m.group(0)
            return key
        
        def save_triple_single(m):
            key = f"__MYSTR_{uuid.uuid4().hex[:8]}__"
            self.placeholders[key] = m.group(0)
            return key
        
        result = re.sub(r'""".*?"""', save_triple_double, result, flags=re.DOTALL)
        result = re.sub(r"'''.*?'''", save_triple_single, result, flags=re.DOTALL)
        
        # Proteger strings normales
        def save_string_doble(m):
            key = f"__MYSTR_{uuid.uuid4().hex[:8]}__"
            self.placeholders[key] = m.group(0)
            return key
        
        def save_string_simple(m):
            key = f"__MYSTR_{uuid.uuid4().hex[:8]}__"
            self.placeholders[key] = m.group(0)
            return key
        
        result = re.sub(r'"[^"\n]*"', save_string_doble, result)
        result = re.sub(r"'[^'\n]*'", save_string_simple, result)
        
        # Proteger comentarios
        def save_comment(m):
            key = f"__MYSTR_{uuid.uuid4().hex[:8]}__"
            self.placeholders[key] = m.group(0)
            return key
        
        result = re.sub(r'#[^\n]*', save_comment, result)
        
        return result
    
    def _restaurar(self, codigo: str) -> str:
        """Restaura strings y comentarios desde placeholders"""
        result = codigo
        for placeholder, original in self.placeholders.items():
            result = result.replace(placeholder, original, 1)
        return result
    
    def _traducir_keywords(self, codigo: str) -> str:
        """Traduce keywords"""
        result = codigo
        
        # Traducir keywords (ordenadas por longitud para evitar conflictos)
        for spanish, python in sorted(self.KEYWORD_MAP.items(), key=lambda x: -len(x[0])):
            pattern = r'\b' + re.escape(spanish) + r'\b'
            result = re.sub(pattern, python, result)
        
        # Manejo especial para 'definir'
        result = re.sub(r'\bdefinir\s+(\w+)\s*\(', r'def \1(', result)
        result = re.sub(r'\bdefinir\s+', '', result)
        
        # Operadores lógicos: y, o, no
        # Solo traducir en contexto de expresión (no como variables)
        for spanish, python in [('y', 'and'), ('o', 'or'), ('no', 'not')]:
            if spanish == 'no':
                # 'no' se traduce si precede a una expresión
                pattern = r'\bno\b(?=\s*(?:verdadero|falso|nulo|[a-zA-Z_]))'
                result = re.sub(pattern, python, result)
            else:
                # 'y' y 'o' se traducen solo si están entre expresiones
                # Incluye ), ], identificadores, números, y también ( para casos como ") o ("
                pattern = r'([\w\)])\s+' + re.escape(spanish) + r'\s+([\w\(])'
                result = re.sub(pattern, r'\1 ' + python + r' \2', result)
        
        return result
    
    def _traducir_tipos(self, codigo: str) -> str:
        """Traduce tipos de español a Python"""
        tipos_map = {
            'booleano': 'bool',
            'entero': 'int',
            'flotante': 'float',
            'cadena': 'str',
            'lista': 'list',
            'dict': 'dict',
        }

        resultado = codigo
        for esp, py in tipos_map.items():
            # Traducir en contexto de tipo (después de : o ->)
            pattern = r'(:|->)\s*' + esp + r'\b'
            resultado = re.sub(pattern, r'\1 ' + py, resultado)

        return resultado
    
    def _validar_python(self, codigo: str):
        """Valida que el código generado sea Python válido"""
        try:
            py_ast.parse(codigo)
        except SyntaxError as e:
            raise TranslatorError(f"Código Python inválido: {e}")
    
    def traducir_archivo(self, input_path: str, output_path: str = None) -> str:
        """Traduce un archivo .my"""
        with open(input_path, 'r', encoding='utf-8') as f:
            codigo = f.read()
        
        traducido = self.traducir(codigo)
        
        if output_path:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(traducido)
        
        return traducido


# Función de conveniencia
def traducir(codigo: str) -> str:
    """Traduce código My a Python"""
    traductor = TraductorMejorado()
    return traductor.traducir(codigo)
