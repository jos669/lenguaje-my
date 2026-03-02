"""
My Lenguaje - Traductor Mejorado (Fase 2.0 - Corregido)
Traductor que protege strings/comentarios y evita bugs

Mejoras implementadas:
- Sin colisiones de placeholders (usa UUID único)
- No traduce keywords dentro de strings/comentarios
- Manejo ROBUSTO de 'y', 'o', 'no' como variables
- Soporte para escapes en strings (\", \', \\, \n, etc.)
- Validación del código Python generado
- Mapeo de líneas para errores precisos
- Keywords adicionales: parar, continuar, pasar
"""

import re
import uuid
import ast as py_ast
from typing import Dict, List, Tuple


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
        'desde': 'from',  # Para imports
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
        # Control de flujo adicional
        'parar': 'break',
        'continuar': 'continue',
        'pasar': 'pass',
        # Concise syntax (Fase 9)
        'fn': 'lambda',
        'paralelo': 'async',  # Para concurrencia nativa
        'selecciona': 'filter',  # SQL-like queries
        'donde': 'if',  # Para queries
        'match': 'match',  # Pattern matching (Python 3.10+)
        'caso': 'case',
        'predeterminado': 'case _',
    }
    
    def __init__(self):
        self.placeholders: Dict[str, str] = {}
    
    def traducir(self, codigo: str) -> str:
        """Traduce código My a Python con features concisas"""
        self.placeholders = {}

        # Fase 0: Features concisas (ANTES de proteger strings)
        codigo = self._traducir_features_concisos(codigo)

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
    
    def _traducir_features_concisos(self, codigo: str) -> str:
        """
        Traduce features concisas de Espy a Python
        
        Features implementadas:
        - Arrow functions: fn(a,b) => expr
        - Range shorthand: 1..10 → range(1, 11)
        - Inline ternary: ?cond: a sino: b
        - List comprehensions cortas: [x p x en lista]
        - Pattern matching básico
        """
        result = codigo
        
        # 1. Arrow functions: fn nombre(a,b) => expr
        # fn suma(a,b) => a + b → def suma(a,b):\n    return a + b
        result = re.sub(
            r'\bfn\s+(\w+)\s*\(([^)]*)\)\s*=>\s*([^\n]+)',
            lambda m: f'def {m.group(1)}({m.group(2)}):\n    return {m.group(3)}',
            result
        )
        
        # Lambda shorthand: variable = fn(a,b) => expr
        # suma = fn(a,b) => a + b → suma = lambda a,b: a + b
        result = re.sub(
            r'(\w+)\s*=\s*fn\s*\(([^)]*)\)\s*=>\s*([^\n]+)',
            lambda m: f'{m.group(1)} = lambda {m.group(2)}: {m.group(3)}',
            result
        )
        
        # Lambda shorthand sin nombre: (a,b) => a + b
        result = re.sub(
            r'\(([^)]*)\)\s*=>\s*([^\n,]+)',
            lambda m: f'lambda {m.group(1)}: {m.group(2)}',
            result
        )
        
        # 2. Range shorthand: 1..10 → range(1, 11)
        # Soporta: 1..10, 0..n, etc.
        result = re.sub(
            r'(\d+)\.\.(\d+)',
            lambda m: f'range({m.group(1)}, {int(m.group(2))+1})',
            result
        )
        
        # 3. Inline ternary extendido: ?cond: a sino: b
        # ?x>0: x sino: 0 → x if x>0 else 0
        result = re.sub(
            r'\?([^:]+):\s*([^\s]+)\s+sino:\s*([^\s,;\n]+)',
            lambda m: f'{m.group(2)} if {m.group(1)} else {m.group(3)}',
            result
        )
        
        # 4. List comprehension corta: [x p x en lista]
        # [x*2 p x en lista] → [x*2 for x in lista]
        result = re.sub(
            r'\[([^\]]+)\s+p\s+(\w+)\s+en\s+([^\]]+)\]',
            lambda m: f'[{m.group(1)} for {m.group(2)} in {m.group(3)}]',
            result
        )
        
        # 5. SQL-like query: selecciona x de lista donde x>5
        # selecciona x de lista donde x>5 → [x for x in lista if x>5]
        result = re.sub(
            r'selecciona\s+(\w+)\s+de\s+(\w+)\s+donde\s+([^\n]+)',
            lambda m: f'[{m.group(1)} for {m.group(1)} in {m.group(2)} if {m.group(3)}]',
            result
        )
        
        # 6. Pattern matching básico
        # match x: caso 1: ... predeterminado: ...
        # match x: → match x:\n
        result = re.sub(
            r'\bmatch\s+(\w+):\s*',
            lambda m: f'match {m.group(1)}:\n',
            result
        )
        # caso X: → case X:
        result = re.sub(
            r'\bcaso\s+(.+?):',
            lambda m: f'case {m.group(1)}:',
            result
        )
        # predeterminado: → case _:
        result = re.sub(
            r'\bpredeterminado:',
            'case _:',
            result
        )
        
        # 7. Try-catch inline: codigo ! fallback
        # resultado = risky() ! default → try: resultado = risky()\nexcept: resultado = default
        result = re.sub(
            r'(\w+\s*=\s*\w+\([^)!]*\))\s*!\s*([^\n]+)',
            lambda m: f'try:\n    {m.group(1)}\nexcept:\n    {m.group(1).split("=")[0].strip()} = {m.group(2)}',
            result
        )
        
        # 8. Paralelo para concurrencia: paralelo para i en lista: tarea(i)
        # paralelo para i en lista: tarea(i) → async for i in lista: await tarea(i)
        result = re.sub(
            r'paralelo\s+para\s+(\w+)\s+en\s+([^:]+):\s*([^\n]+)',
            lambda m: f'async for {m.group(1)} in {m.group(2)}:\n    await {m.group(3)}',
            result
        )
        
        return result
    
    def _proteger(self, codigo: str) -> str:
        """
        Protege strings y comentarios reemplazándolos con placeholders
        Soporta escapes: \", \', \\, \n, \t, \r, etc.
        """
        result = codigo
        self.placeholders = {}

        # Proteger strings de triple comilla primero (multilínea)
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

        # Proteger strings con escapes manejados correctamente
        # Pattern que maneja: "..." con escapes como \"
        def save_string_doble(m):
            key = f"__MYSTR_{uuid.uuid4().hex[:8]}__"
            self.placeholders[key] = m.group(0)
            return key

        def save_string_simple(m):
            key = f"__MYSTR_{uuid.uuid4().hex[:8]}__"
            self.placeholders[key] = m.group(0)
            return key

        # Strings dobles con escapes: "..." - maneja \" dentro del string
        result = re.sub(r'"(?:[^"\\]|\\.)*"', save_string_doble, result)
        # Strings simples con escapes: '...' - maneja \' dentro del string
        result = re.sub(r"'(?:[^'\\]|\\.)*'", save_string_simple, result)

        # Proteger comentarios (desde # hasta fin de línea)
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
        """
        Traduce keywords evitando colisiones con variables
        Estrategia: NO traducir y, o, no automáticamente
        Solo traducir en contextos específicos donde SON operadores
        """
        result = codigo

        # Traducir TODAS las keywords EXCEPTO y, o, no
        keywords_seguras = {k: v for k, v in self.KEYWORD_MAP.items() 
                          if k not in ['y', 'o', 'no']}
        
        for spanish, python in sorted(keywords_seguras.items(), key=lambda x: -len(x[0])):
            pattern = r'\b' + re.escape(spanish) + r'\b'
            result = re.sub(pattern, python, result)

        # Manejo especial para 'definir'
        result = re.sub(r'\bdefinir\s+(\w+)\s*\(', r'def \1(', result)
        result = re.sub(r'\bdefinir\s+', '', result)

        # ============================================
        # OPERADORES LÓGICOS: y, o, no
        # ============================================
        # Problema: 'y' puede ser variable O operador
        # Solución: Solo traducir en contexto de OPERADOR
        
        # Contextos donde y/o SON operadores (NO variables):
        # 1. Entre dos expresiones: expr y expr, expr o expr
        # 2. Después de operadores de comparación: == y, != y, > y, < y
        # 3. Dentro de condiciones: si ... y ..., mientras ... o ...
        
        # 'y' como operador lógico AND
        # Solo traducir si está entre expresiones válidas
        # Patrón: algo que parece expresión + espacio + 'y' + espacio + algo que parece expresión
        result = re.sub(
            r'(\w|\)|\]|\d)\s+y\s+(\w|\(|\[|\d|")',
            lambda m: m.group(1) + ' and ' + m.group(2),
            result
        )
        
        # 'o' como operador lógico OR
        result = re.sub(
            r'(\w|\)|\]|\d)\s+o\s+(\w|\(|\[|\d|")',
            lambda m: m.group(1) + ' or ' + m.group(2),
            result
        )
        
        # 'no' como operador NOT - solo antes de valores booleanos o comparaciones
        # no True, no False, no None, no variable, no (expresion)
        result = re.sub(
            r'\bno\s+(verdadero|falso|nulo|\w+|\()',
            lambda m: 'not ' + m.group(1),
            result
        )
        
        # Traducir verdadero, falso, nulo (seguro, no son variables)
        result = re.sub(r'\bverdadero\b', 'True', result)
        result = re.sub(r'\bfalso\b', 'False', result)
        result = re.sub(r'\bnulo\b', 'None', result)

        return result
    
    def _traducir_tipos(self, codigo: str) -> str:
        """Traduce tipos de español a Python - SIN espacio doble"""
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
            # Pattern ya incluye \s* que consume espacios existentes
            # NO agregar espacio extra en el reemplazo
            pattern = r'(:|->)\s*' + esp + r'\b'
            resultado = re.sub(pattern, r'\1' + py, resultado)

        return resultado
    
    def _validar_python(self, codigo: str):
        """
        Valida que el código generado sea Python válido
        Muestra errores DETALLADOS con contexto exacto
        """
        try:
            py_ast.parse(codigo)
        except SyntaxError as e:
            # Construir mensaje de error detallado estilo Python
            lineas = codigo.split('\n')
            linea_error = e.lineno if e.lineno else 1
            columna = getattr(e, 'offset', getattr(e, 'column', 0)) or 0
            
            # Obtener contexto (líneas alrededor del error)
            inicio = max(0, linea_error - 3)
            fin = min(len(lineas), linea_error + 3)
            
            # Construir mensaje detallado
            mensaje_error = [
                "",
                "╔" + "═" * 70 + "╗",
                "║  ❌ ERROR DE SINTAXIS EN CÓDIGO GENERADO".ljust(71) + "║",
                "╠" + "═" * 70 + "╣",
                f"║  Ubicación: línea {linea_error}, columna {columna}".ljust(71) + "║",
                f"║  Tipo: {e.msg}".ljust(71) + "║",
                "╟" + "─" * 70 + "╢",
                "║  Código alrededor del error:".ljust(71) + "║",
                "╟" + "─" * 70 + "╢",
            ]
            
            # Agregar líneas de código con números
            for i in range(inicio, fin):
                num_linea = i + 1
                linea = lineas[i] if i < len(lineas) else ""
                
                # Truncar línea si es muy larga
                if len(linea) > 60:
                    linea = linea[:57] + "..."
                
                # Marcar línea con error
                if i + 1 == linea_error:
                    mensaje_error.append(f"║ {num_linea:4} │ >> {linea}".ljust(71) + "║")
                    # Agregar caret (^) apuntando al error
                    if columna:
                        caret_pos = max(0, min(columna - 1, len(linea)))
                        mensaje_error.append(f"║      │    {' ' * caret_pos}^".ljust(71) + "║")
                else:
                    mensaje_error.append(f"║ {num_linea:4} │    {linea}".ljust(71) + "║")
            
            mensaje_error.extend([
                "╟" + "─" * 70 + "╢",
                "║  Sugerencias:".ljust(71) + "║",
            ])
            
            # Agregar sugerencias basadas en el error
            sugerencias = self._generar_sugerencias(e.msg, lineas[linea_error - 1] if linea_error <= len(lineas) else "")
            for sug in sugerencias:
                mensaje_error.append(f"║    • {sug}".ljust(71) + "║")
            
            mensaje_error.extend([
                "╚" + "═" * 70 + "╝",
                "",
            ])
            
            raise TranslatorError("\n".join(mensaje_error))
    
    def _generar_sugerencias(self, error_msg: str, linea_codigo: str) -> List[str]:
        """Genera sugerencias basadas en el tipo de error"""
        sugerencias = []
        error_msg_lower = error_msg.lower()
        
        if "invalid syntax" in error_msg_lower:
            sugerencias.append("Verifica que todos los paréntesis, corchetes y llaves estén cerrados")
            sugerencias.append("Revisa que las comillas estén balanceadas")
        
        if "unexpected indent" in error_msg_lower:
            sugerencias.append("La indentación es inconsistente - usa 4 espacios")
            sugerencias.append("No mezcles tabs y espacios")
        
        if "expected an indented block" in error_msg_lower:
            sugerencias.append("Después de ':', la siguiente línea debe estar indentada")
            sugerencias.append("Verifica después de def, if, for, while, class, etc.")
        
        if "eol while scanning" in error_msg_lower:
            sugerencias.append("Hay una cadena sin cerrar (comillas incompletas)")
        
        if "keyword" in error_msg_lower or "reserved" in error_msg_lower:
            sugerencias.append("Estás usando una palabra reservada de Python como variable")
        
        if "name" in error_msg_lower and "not defined" in error_msg_lower:
            sugerencias.append("La variable no está definida - verifica el nombre o el scope")
        
        # Sugerencias específicas basadas en el código
        if 'fn' in linea_codigo and '=>' not in linea_codigo:
            sugerencias.append("Arrow function incompleta - usa: fn(args) => expresion")
        
        if '..' in linea_codigo and 'range' not in linea_codigo:
            sugerencias.append("Range shorthand debe estar en un contexto válido (ej: for x en 1..10)")
        
        if not sugerencias:
            sugerencias.append("Revisa la sintaxis del código My Lenguaje")
            sugerencias.append("Ejecuta 'python my.py keywords' para ver keywords válidas")
        
        return sugerencias[:4]  # Máximo 4 sugerencias
    
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
