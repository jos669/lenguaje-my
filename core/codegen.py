"""
My Lenguaje - Generador de Código Python (Fase 2)
Convierte el AST a código Python válido
"""

import ast as py_ast
from typing import List, Optional, Any

from .ast_nodes import (
    Programa, DefinicionVar, DefinicionFuncion, DefinicionClase,
    Condicional, BuclePara, BucleMientras, Retorno, Importacion,
    TryExcept, Asignacion, ExpresionStmt,
    BinOp, UnaryOp, Comparacion, LlamadaFuncion, Identificador,
    AccesoAtributo, AccesoIndice,
    Literal, ListaLiteral, DiccionarioLiteral
)


class GeneradorPython:
    """
    Genera código Python válido desde el AST de My Lenguaje
    """
    
    # Mapeo de builtins en español a Python
    BUILTINS_MAP = {
        'rango': 'range',
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
        self.indent_level = 0
        self.indent_str = "    "  # 4 espacios
    
    def generar(self, arbol: Programa) -> str:
        """
        Genera código Python desde el AST
        
        Args:
            arbol: AST del programa
            
        Returns:
            Código Python como string
        """
        lineas = []
        for stmt in arbol.statements:
            codigo = self._generar_statement(stmt)
            if codigo:
                lineas.append(codigo)
        
        return '\n'.join(lineas)
    
    def _indent(self, codigo: str) -> str:
        """Añade indentación al código"""
        indent = self.indent_str * self.indent_level
        lineas = codigo.split('\n')
        return '\n'.join(indent + linea if linea.strip() else linea for linea in lineas)
    
    def _generar_statement(self, nodo) -> str:
        """Genera un statement"""
        if isinstance(nodo, DefinicionVar):
            return self._generar_definicion_var(nodo)
        elif isinstance(nodo, DefinicionFuncion):
            return self._generar_definicion_funcion(nodo)
        elif isinstance(nodo, DefinicionClase):
            return self._generar_definicion_clase(nodo)
        elif isinstance(nodo, Condicional):
            return self._generar_condicional(nodo)
        elif isinstance(nodo, BuclePara):
            return self._generar_bucle_para(nodo)
        elif isinstance(nodo, BucleMientras):
            return self._generar_bucle_mientras(nodo)
        elif isinstance(nodo, Retorno):
            return self._generar_retorno(nodo)
        elif isinstance(nodo, Importacion):
            return self._generar_importacion(nodo)
        elif isinstance(nodo, TryExcept):
            return self._generar_try_except(nodo)
        elif isinstance(nodo, Asignacion):
            return self._generar_asignacion(nodo)
        elif isinstance(nodo, ExpresionStmt):
            return self._generar_expresion_stmt(nodo)
        else:
            raise ValueError(f"Statement desconocido: {type(nodo)}")
    
    def _generar_definicion_var(self, nodo: DefinicionVar) -> str:
        """definir x = valor → x = valor"""
        valor = self._generar_expresion(nodo.valor)
        return f"{nodo.nombre} = {valor}"
    
    def _generar_definicion_funcion(self, nodo: DefinicionFuncion) -> str:
        """función nombre(params): cuerpo"""
        params = ', '.join(nodo.parametros)
        lineas = [f"def {nodo.nombre}({params}):"]
        
        self.indent_level += 1
        for stmt in nodo.cuerpo:
            codigo = self._generar_statement(stmt)
            lineas.append(self._indent(codigo))
        self.indent_level -= 1
        
        return '\n'.join(lineas)
    
    def _generar_definicion_clase(self, nodo: DefinicionClase) -> str:
        """clase Nombre: cuerpo"""
        lineas = [f"class {nodo.nombre}:"]
        
        self.indent_level += 1
        for stmt in nodo.cuerpo:
            codigo = self._generar_statement(stmt)
            lineas.append(self._indent(codigo))
        self.indent_level -= 1
        
        return '\n'.join(lineas)
    
    def _generar_condicional(self, nodo: Condicional) -> str:
        """si condicion: cuerpo sino: alternativo"""
        condicion = self._generar_expresion(nodo.condicion)
        lineas = [f"if {condicion}:"]
        
        self.indent_level += 1
        for stmt in nodo.cuerpo:
            codigo = self._generar_statement(stmt)
            lineas.append(self._indent(codigo))
        self.indent_level -= 1
        
        # sino_si (elif)
        for condicion_si, cuerpo_si in nodo.sino_si:
            cond_str = self._generar_expresion(condicion_si)
            lineas.append(f"elif {cond_str}:")
            
            self.indent_level += 1
            for stmt in cuerpo_si:
                codigo = self._generar_statement(stmt)
                lineas.append(self._indent(codigo))
            self.indent_level -= 1
        
        # sino (else)
        if nodo.sino:
            lineas.append("else:")
            self.indent_level += 1
            for stmt in nodo.sino:
                codigo = self._generar_statement(stmt)
                lineas.append(self._indent(codigo))
            self.indent_level -= 1
        
        return '\n'.join(lineas)
    
    def _generar_bucle_para(self, nodo: BuclePara) -> str:
        """para i en iterable: cuerpo"""
        iterable = self._generar_expresion(nodo.iterable)
        lineas = [f"for {nodo.variable} in {iterable}:"]
        
        self.indent_level += 1
        for stmt in nodo.cuerpo:
            codigo = self._generar_statement(stmt)
            lineas.append(self._indent(codigo))
        self.indent_level -= 1
        
        return '\n'.join(lineas)
    
    def _generar_bucle_mientras(self, nodo: BucleMientras) -> str:
        """mientras condicion: cuerpo"""
        condicion = self._generar_expresion(nodo.condicion)
        lineas = [f"while {condicion}:"]
        
        self.indent_level += 1
        for stmt in nodo.cuerpo:
            codigo = self._generar_statement(stmt)
            lineas.append(self._indent(codigo))
        self.indent_level -= 1
        
        return '\n'.join(lineas)
    
    def _generar_retorno(self, nodo: Retorno) -> str:
        """retornar [valor]"""
        if nodo.valor:
            valor = self._generar_expresion(nodo.valor)
            return f"return {valor}"
        return "return"
    
    def _generar_importacion(self, nodo: Importacion) -> str:
        """importar modulo [como alias]"""
        if nodo.alias:
            return f"import {nodo.modulo} as {nodo.alias}"
        return f"import {nodo.modulo}"
    
    def _generar_try_except(self, nodo: TryExcept) -> str:
        """intentar: cuerpo excepto: manejo finalmente: cleanup"""
        lineas = ["try:"]
        
        self.indent_level += 1
        for stmt in nodo.cuerpo:
            codigo = self._generar_statement(stmt)
            lineas.append(self._indent(codigo))
        self.indent_level -= 1
        
        # exceptos
        for nombre_excepcion, cuerpo in nodo.exceptos:
            if nombre_excepcion:
                lineas.append(f"except {nombre_excepcion}:")
            else:
                lineas.append("except:")
            
            self.indent_level += 1
            for stmt in cuerpo:
                codigo = self._generar_statement(stmt)
                lineas.append(self._indent(codigo))
            self.indent_level -= 1
        
        # finalmente
        if nodo.finalmente:
            lineas.append("finally:")
            self.indent_level += 1
            for stmt in nodo.finalmente:
                codigo = self._generar_statement(stmt)
                lineas.append(self._indent(codigo))
            self.indent_level -= 1
        
        return '\n'.join(lineas)
    
    def _generar_asignacion(self, nodo: Asignacion) -> str:
        """nombre = valor"""
        valor = self._generar_expresion(nodo.valor)
        
        if nodo.es_asignacion_multiple:
            targets = ' = '.join(nodo.objetivos)
            return f"{targets} = {valor}"
        
        return f"{nodo.objetivo} = {valor}"
    
    def _generar_expresion_stmt(self, nodo: ExpresionStmt) -> str:
        """Expresión como statement"""
        return self._generar_expresion(nodo.expresion)
    
    def _generar_expresion(self, nodo) -> str:
        """Genera una expresión"""
        if isinstance(nodo, Literal):
            return self._generar_literal(nodo)
        elif isinstance(nodo, Identificador):
            return nodo.nombre
        elif isinstance(nodo, BinOp):
            return self._generar_binop(nodo)
        elif isinstance(nodo, UnaryOp):
            return self._generar_unaryop(nodo)
        elif isinstance(nodo, Comparacion):
            return self._generar_comparacion(nodo)
        elif isinstance(nodo, LlamadaFuncion):
            return self._generar_llamada_funcion(nodo)
        elif isinstance(nodo, AccesoAtributo):
            return f"{nodo.objeto}.{nodo.atributo}"
        elif isinstance(nodo, AccesoIndice):
            indice = self._generar_expresion(nodo.indice)
            return f"{nodo.objeto}[{indice}]"
        elif isinstance(nodo, ListaLiteral):
            return self._generar_lista_literal(nodo)
        elif isinstance(nodo, DiccionarioLiteral):
            return self._generar_diccionario_literal(nodo)
        else:
            raise ValueError(f"Expresión desconocida: {type(nodo)}")
    
    def _generar_literal(self, nodo: Literal) -> str:
        """Genera un literal"""
        if nodo.tipo == 'str':
            # Escapar comillas dobles en el string
            valor = nodo.valor.replace('"', '\\"')
            return f'"{valor}"'
        elif nodo.tipo == 'bool':
            return 'True' if nodo.valor else 'False'
        elif nodo.tipo == 'None':
            return 'None'
        else:
            return str(nodo.valor)
    
    def _generar_binop(self, nodo: BinOp) -> str:
        """Genera operación binaria"""
        izquierda = self._generar_expresion(nodo.izquierda)
        derecha = self._generar_expresion(nodo.derecha)
        return f"({izquierda} {nodo.operador} {derecha})"
    
    def _generar_unaryop(self, nodo: UnaryOp) -> str:
        """Genera operación unaria"""
        operando = self._generar_expresion(nodo.operando)
        return f"({nodo.operador} {operando})"
    
    def _generar_comparacion(self, nodo: Comparacion) -> str:
        """Genera comparación"""
        izquierda = self._generar_expresion(nodo.izquierda)
        derecha = self._generar_expresion(nodo.derecha)
        return f"({izquierda} {nodo.operador} {derecha})"
    
    def _generar_llamada_funcion(self, nodo: LlamadaFuncion) -> str:
        """Genera llamada a función"""
        # Traducir builtins
        nombre = self.BUILTINS_MAP.get(nodo.nombre, nodo.nombre)
        
        args = ', '.join(self._generar_expresion(arg) for arg in nodo.argumentos)
        return f"{nombre}({args})"
    
    def _generar_lista_literal(self, nodo: ListaLiteral) -> str:
        """Genera lista literal"""
        elementos = ', '.join(self._generar_expresion(e) for e in nodo.elementos)
        return f"[{elementos}]"
    
    def _generar_diccionario_literal(self, nodo: DiccionarioLiteral) -> str:
        """Genera diccionario literal"""
        pares = []
        for clave, valor in nodo.pares:
            k = self._generar_expresion(clave)
            v = self._generar_expresion(valor)
            pares.append(f"{k}: {v}")
        return "{" + ", ".join(pares) + "}"


def validar_python(codigo: str) -> tuple[bool, Optional[str]]:
    """
    Valida que el código Python generado sea sintácticamente correcto
    
    Returns:
        Tuple (es_valido, mensaje_error)
    """
    try:
        py_ast.parse(codigo)
        return True, None
    except SyntaxError as e:
        return False, f"Error de sintaxis Python: {e}"


def generar_python(arbol: Programa) -> str:
    """Función de conveniencia para generar Python"""
    generador = GeneradorPython()
    codigo = generador.generar(arbol)
    
    # Validar el código generado
    es_valido, error = validar_python(codigo)
    if not es_valido:
        raise GeneracionError(f"El código generado no es Python válido: {error}")
    
    return codigo


class GeneracionError(Exception):
    """Excepción para errores de generación de código"""
    pass
