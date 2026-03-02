"""
My Lenguaje - Parser con Lark (Fase 3)
Parser completo con manejo de errores en español
"""

from lark import Lark, Transformer, v_args, Tree, Token
from lark.exceptions import LarkError, UnexpectedToken, UnexpectedInput
from typing import List, Optional, Any, Tuple

from .ast_nodes import (
    Programa, DefinicionVar, DefinicionFuncion, DefinicionClase,
    Condicional, BuclePara, BucleMientras, Retorno, Importacion,
    TryExcept, Asignacion, ExpresionStmt,
    BinOp, UnaryOp, Comparacion, LlamadaFuncion, Identificador,
    AccesoAtributo, AccesoIndice,
    Literal, ListaLiteral, DiccionarioLiteral
)

from .grammar import GRAMATICA_MY


class ErrorSintaxis(Exception):
    """Excepción para errores de sintaxis con mensajes en español"""
    
    def __init__(self, mensaje: str, linea: int = None, columna: int = None, contexto: str = None):
        self.mensaje = mensaje
        self.linea = linea
        self.columna = columna
        self.contexto = contexto
        
        mensaje_completo = f"Error de sintaxis"
        if linea:
            mensaje_completo += f" en línea {linea}"
        if columna:
            mensaje_completo += f", columna {columna}"
        mensaje_completo += f": {mensaje}"
        if contexto:
            mensaje_completo += f"\n  → {contexto}"
        
        super().__init__(mensaje_completo)


class ConstruirAST(Transformer):
    """Transforma el parse tree de Lark a nuestro AST"""
    
    def __init__(self):
        super().__init__()
    
    def start(self, children):
        statements = [c for c in children if c is not None]
        return Programa(statements=statements)
    
    # === Statements ===
    
    def definicion_var(self, children):
        # DEFINIR IDENTIFIER (COLON tipo)? OP_ASIGNAR expresion NEWLINE
        idx = 1  # Saltar DEFINIR
        nombre = children[idx].value
        idx += 1
        
        tipo = None
        if len(children) > 4 and children[idx] == ':':
            tipo = children[idx + 1]
            idx += 2
        
        # Encontrar la expresión (después de '=')
        for i, child in enumerate(children):
            if isinstance(child, str) and child == '=':
                valor = children[i + 1]
                break
        else:
            valor = None
        
        return DefinicionVar(nombre=nombre, valor=valor)
    
    def definicion_funcion(self, children):
        # FUNCION IDENTIFIER parametros (ARROW tipo)? COLON NEWLINE INDENT statement+ DEDENT
        nombre = children[0].value
        
        # Encontrar parámetros y cuerpo
        params = []
        cuerpo = []
        tipo_retorno = None
        
        for child in children:
            if isinstance(child, list):
                params = child if not cuerpo else child
            elif isinstance(child, Tree):
                if child.data == 'parametros':
                    params = self._extraer_parametros(child)
        
        # El cuerpo está después de los dos puntos
        for i, child in enumerate(children):
            if isinstance(child, str) and child == ':':
                # El cuerpo sigue después
                for j in range(i + 1, len(children)):
                    if isinstance(children[j], list):
                        cuerpo = children[j]
                        break
                break
        
        return DefinicionFuncion(nombre=nombre, parametros=params, cuerpo=cuerpo)
    
    def _extraer_parametros(self, tree):
        params = []
        for child in tree.children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                params.append(child.value)
        return params
    
    def definicion_clase(self, children):
        nombre = children[0].value
        cuerpo = []
        
        for child in children:
            if isinstance(child, list):
                cuerpo = child
        
        return DefinicionClase(nombre=nombre, cuerpo=cuerpo)
    
    def parametros(self, children):
        params = []
        for child in children:
            if isinstance(child, Token) and child.type == 'IDENTIFIER':
                params.append(child.value)
        return params
    
    def condicional(self, children):
        condicion = children[1]
        cuerpo = []
        sino_si = []
        sino = None
        
        # Extraer cuerpo después de ':'
        for i, child in enumerate(children):
            if isinstance(child, str) and child == ':':
                for j in range(i + 1, len(children)):
                    if isinstance(children[j], list):
                        cuerpo = children[j]
                        break
                break
        
        # Extraer sino_si y sino
        for child in children:
            if isinstance(child, tuple):
                sino_si.append(child)
            elif isinstance(child, list) and child and hasattr(child[0], 'type') and child[0].type == 'SINO':
                sino = child
        
        return Condicional(condicion=condicion, cuerpo=cuerpo, sino_si=sino_si, sino=sino)
    
    def bucle_para(self, children):
        variable = children[1].value
        iterable = children[3]
        cuerpo = []
        
        for child in children:
            if isinstance(child, list):
                cuerpo = child
        
        return BuclePara(variable=variable, iterable=iterable, cuerpo=cuerpo)
    
    def bucle_mientras(self, children):
        condicion = children[1]
        cuerpo = []
        
        for child in children:
            if isinstance(child, list):
                cuerpo = child
        
        return BucleMientras(condicion=condicion, cuerpo=cuerpo)
    
    def try_except(self, children):
        cuerpo = []
        exceptos = []
        finalmente = None
        
        for child in children:
            if isinstance(child, list):
                if not cuerpo:
                    cuerpo = child
                else:
                    exceptos.append((None, child))
            elif isinstance(child, tuple):
                if child[0] == 'finally':
                    finalmente = child[1]
        
        return TryExcept(cuerpo=cuerpo, exceptos=exceptos, finalmente=finalmente)
    
    def importacion(self, children):
        modulo = children[1]
        alias = None
        
        for i, child in enumerate(children):
            if isinstance(child, Token) and child.type == 'COMO':
                if i + 1 < len(children):
                    alias = children[i + 1].value
        
        return Importacion(modulo=modulo, alias=alias)
    
    def modulo(self, children):
        parts = [children[0].value]
        for i in range(1, len(children), 2):
            if i + 1 < len(children):
                parts.append(children[i + 1].value)
        return '.'.join(parts)
    
    def retorno(self, children):
        if len(children) > 1:
            return Retorno(valor=children[1])
        return Retorno(valor=None)
    
    def asignacion(self, children):
        target = children[0]
        valor = children[2]
        
        if isinstance(target, Identificador):
            return Asignacion(objetivo=target.nombre, valor=valor)
        return Asignacion(objetivo=str(target), valor=valor)
    
    def target(self, children):
        if len(children) == 1:
            return Identificador(nombre=children[0].value)
        return children[0]
    
    def expresion_stmt(self, children):
        return ExpresionStmt(expresion=children[0])
    
    # === Expresiones ===
    
    def expresion(self, children):
        return children[0]
    
    def or_expr(self, children):
        if len(children) == 1:
            return children[0]
        result = children[0]
        for i in range(1, len(children), 2):
            result = BinOp(izquierda=result, operador='or', derecha=children[i + 1])
        return result
    
    def and_expr(self, children):
        if len(children) == 1:
            return children[0]
        result = children[0]
        for i in range(1, len(children), 2):
            result = BinOp(izquierda=result, operador='and', derecha=children[i + 1])
        return result
    
    def not_expr(self, children):
        if len(children) == 1:
            return children[0]
        return UnaryOp(operador='not', operando=children[1])
    
    def comparison(self, children):
        if len(children) == 1:
            return children[0]
        return Comparacion(izquierda=children[0], operador=children[1], derecha=children[2])
    
    def sum_expr(self, children):
        if len(children) == 1:
            return children[0]
        result = children[0]
        for i in range(1, len(children), 2):
            result = BinOp(izquierda=result, operador=children[i], derecha=children[i + 1])
        return result
    
    def term(self, children):
        if len(children) == 1:
            return children[0]
        result = children[0]
        for i in range(1, len(children), 2):
            result = BinOp(izquierda=result, operador=children[i], derecha=children[i + 1])
        return result
    
    def factor(self, children):
        if len(children) == 1:
            return children[0]
        op = children[0]
        if isinstance(op, str) and op in ('+', '-'):
            return UnaryOp(operador=op, operando=children[1])
        return children[0]
    
    def potencia(self, children):
        if len(children) == 1:
            return children[0]
        result = children[0]
        for i in range(1, len(children), 2):
            result = BinOp(izquierda=result, operador='**', derecha=children[i + 1])
        return result
    
    def atom(self, children):
        return children[0]
    
    def literal(self, children):
        token = children[0]
        if hasattr(token, 'type'):
            if token.type == 'INT':
                return Literal(valor=int(token.value), tipo='int')
            elif token.type == 'FLOAT':
                return Literal(valor=float(token.value), tipo='float')
            elif token.type == 'STRING':
                valor = token.value[1:-1]
                return Literal(valor=valor, tipo='str')
            elif token.type == 'VERDADERO':
                return Literal(valor=True, tipo='bool')
            elif token.type == 'FALSO':
                return Literal(valor=False, tipo='bool')
            elif token.type == 'NULO':
                return Literal(valor=None, tipo='None')
        return Literal(valor=token.value if hasattr(token, 'value') else token, tipo='unknown')
    
    def llamada_funcion(self, children):
        nombre = children[0].value if hasattr(children[0], 'value') else str(children[0])
        argumentos = []
        
        for child in children:
            if isinstance(child, list):
                argumentos = child
            elif not isinstance(child, (Token, str)) and child:
                argumentos.append(child)
        
        return LlamadaFuncion(nombre=nombre, argumentos=argumentos)
    
    def acceso_atributo(self, children):
        return AccesoAtributo(objeto=children[0].value, atributo=children[1].value)
    
    def lista_literal(self, children):
        elementos = []
        for child in children:
            if not isinstance(child, str) or child not in ('[', ']', ','):
                if child:
                    elementos.append(child)
        return ListaLiteral(elementos=elementos)
    
    def diccionario_literal(self, children):
        pares = []
        return DiccionarioLiteral(pares=pares)


class Parser:
    """
    Parser principal para My Lenguaje (Fase 3)
    
    Características:
    - Parser Lark con gramática EBNF
    - Errores de sintaxis en español
    - Construcción de AST
    """
    
    def __init__(self):
        self.parser = Lark(
            GRAMATICA_MY,
            parser='lalr',
            propagate_positions=True,
            debug=False
        )
    
    def parse(self, codigo: str):
        """
        Parsea código fuente y retorna un AST
        
        Args:
            codigo: Código fuente en español
            
        Returns:
            Nodo raíz del AST (Programa)
            
        Raises:
            ErrorSintaxis: Si hay errores de sintaxis
        """
        try:
            arbol = self.parser.parse(codigo)
            transformer = ConstruirAST()
            return transformer.transform(arbol)
        except UnexpectedToken as e:
            raise ErrorSintaxis(
                mensaje=f"Token inesperado '{e.token}'. Se esperaba uno de: {e.accepts or 'expresión'}",
                linea=e.line,
                columna=e.column,
                contexto=e.context
            )
        except UnexpectedInput as e:
            raise ErrorSintaxis(
                mensaje=f"Entrada inesperada en la posición {e.pos}",
                linea=e.line,
                columna=e.column,
                contexto=e.context
            )
        except LarkError as e:
            raise ErrorSintaxis(mensaje=str(e))
        except Exception as e:
            raise ErrorSintaxis(mensaje=f"Error interno del parser: {e}")
    
    def parse_file(self, ruta: str):
        """Parsea un archivo .my"""
        with open(ruta, 'r', encoding='utf-8') as f:
            codigo = f.read()
        return self.parse(codigo)


class ParseError(Exception):
    """Excepción para errores de parsing (compatibilidad)"""
    pass
