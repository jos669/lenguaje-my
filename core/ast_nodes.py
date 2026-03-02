"""
My Lenguaje - Nodos AST (Fase 2)
Definición de nodos para el Abstract Syntax Tree
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Optional, Any


class ASTNode(ABC):
    """Clase base para todos los nodos del AST"""
    
    @abstractmethod
    def to_dict(self) -> dict:
        """Convierte el nodo a un diccionario"""
        pass


@dataclass
class Programa(ASTNode):
    """Nodo raíz del programa"""
    statements: List[ASTNode] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "tipo": "Programa",
            "statements": [s.to_dict() for s in self.statements]
        }


# === Statements ===

@dataclass
class DefinicionVar(ASTNode):
    """definir nombre = valor"""
    nombre: str
    valor: ASTNode
    
    def to_dict(self) -> dict:
        return {
            "tipo": "DefinicionVar",
            "nombre": self.nombre,
            "valor": self.valor.to_dict() if self.valor else None
        }


@dataclass
class DefinicionFuncion(ASTNode):
    """función nombre(params): cuerpo"""
    nombre: str
    parametros: List[str]
    cuerpo: List[ASTNode]
    
    def to_dict(self) -> dict:
        return {
            "tipo": "DefinicionFuncion",
            "nombre": self.nombre,
            "parametros": self.parametros,
            "cuerpo": [s.to_dict() for s in self.cuerpo]
        }


@dataclass
class DefinicionClase(ASTNode):
    """clase Nombre: cuerpo"""
    nombre: str
    cuerpo: List[ASTNode]
    
    def to_dict(self) -> dict:
        return {
            "tipo": "DefinicionClase",
            "nombre": self.nombre,
            "cuerpo": [s.to_dict() for s in self.cuerpo]
        }


@dataclass
class Condicional(ASTNode):
    """si condicion: cuerpo sino: alternativo"""
    condicion: ASTNode
    cuerpo: List[ASTNode]
    sino_si: List[tuple[ASTNode, List[ASTNode]]] = field(default_factory=list)
    sino: Optional[List[ASTNode]] = None
    
    def to_dict(self) -> dict:
        return {
            "tipo": "Condicional",
            "condicion": self.condicion.to_dict(),
            "cuerpo": [s.to_dict() for s in self.cuerpo],
            "sino_si": [(c.to_dict(), [s.to_dict() for s in cuerpo]) for c, cuerpo in self.sino_si],
            "sino": [s.to_dict() for s in self.sino] if self.sino else None
        }


@dataclass
class BuclePara(ASTNode):
    """para i en iterable: cuerpo"""
    variable: str
    iterable: ASTNode
    cuerpo: List[ASTNode]
    
    def to_dict(self) -> dict:
        return {
            "tipo": "BuclePara",
            "variable": self.variable,
            "iterable": self.iterable.to_dict(),
            "cuerpo": [s.to_dict() for s in self.cuerpo]
        }


@dataclass
class BucleMientras(ASTNode):
    """mientras condicion: cuerpo"""
    condicion: ASTNode
    cuerpo: List[ASTNode]
    
    def to_dict(self) -> dict:
        return {
            "tipo": "BucleMientras",
            "condicion": self.condicion.to_dict(),
            "cuerpo": [s.to_dict() for s in self.cuerpo]
        }


@dataclass
class Retorno(ASTNode):
    """retornar valor"""
    valor: Optional[ASTNode] = None
    
    def to_dict(self) -> dict:
        return {
            "tipo": "Retorno",
            "valor": self.valor.to_dict() if self.valor else None
        }


@dataclass
class Importacion(ASTNode):
    """importar modulo [como alias]"""
    modulo: str
    alias: Optional[str] = None
    
    def to_dict(self) -> dict:
        return {
            "tipo": "Importacion",
            "modulo": self.modulo,
            "alias": self.alias
        }


@dataclass
class TryExcept(ASTNode):
    """intentar: cuerpo excepto: manejo finalmente: cleanup"""
    cuerpo: List[ASTNode]
    exceptos: List[tuple[Optional[str], List[ASTNode]]]
    finalmente: Optional[List[ASTNode]] = None
    
    def to_dict(self) -> dict:
        return {
            "tipo": "TryExcept",
            "cuerpo": [s.to_dict() for s in self.cuerpo],
            "exceptos": [(nombre, [s.to_dict() for s in cuerpo]) for nombre, cuerpo in self.exceptos],
            "finalmente": [s.to_dict() for s in self.finalmente] if self.finalmente else None
        }


@dataclass
class Asignacion(ASTNode):
    """nombre = valor"""
    objetivo: str
    valor: ASTNode
    es_asignacion_multiple: bool = False
    objetivos: List[str] = field(default_factory=list)
    
    def to_dict(self) -> dict:
        return {
            "tipo": "Asignacion",
            "objetivo": self.objetivo,
            "valor": self.valor.to_dict(),
            "es_asignacion_multiple": self.es_asignacion_multiple,
            "objetivos": self.objetivos
        }


@dataclass
class ExpresionStmt(ASTNode):
    """Expresión como statement"""
    expresion: ASTNode
    
    def to_dict(self) -> dict:
        return {
            "tipo": "ExpresionStmt",
            "expresion": self.expresion.to_dict()
        }


# === Expresiones ===

@dataclass
class BinOp(ASTNode):
    """Operación binaria: a + b"""
    izquierda: ASTNode
    operador: str
    derecha: ASTNode
    
    def to_dict(self) -> dict:
        return {
            "tipo": "BinOp",
            "izquierda": self.izquierda.to_dict(),
            "operador": self.operador,
            "derecha": self.derecha.to_dict()
        }


@dataclass
class UnaryOp(ASTNode):
    """Operación unaria: -x, no x"""
    operador: str
    operando: ASTNode
    
    def to_dict(self) -> dict:
        return {
            "tipo": "UnaryOp",
            "operador": self.operador,
            "operando": self.operando.to_dict()
        }


@dataclass
class Comparacion(ASTNode):
    """Comparación: a > b"""
    izquierda: ASTNode
    operador: str
    derecha: ASTNode
    
    def to_dict(self) -> dict:
        return {
            "tipo": "Comparacion",
            "izquierda": self.izquierda.to_dict(),
            "operador": self.operador,
            "derecha": self.derecha.to_dict()
        }


@dataclass
class LlamadaFuncion(ASTNode):
    """funcion(arg1, arg2)"""
    nombre: str
    argumentos: List[ASTNode]
    
    def to_dict(self) -> dict:
        return {
            "tipo": "LlamadaFuncion",
            "nombre": self.nombre,
            "argumentos": [a.to_dict() for a in self.argumentos]
        }


@dataclass
class Identificador(ASTNode):
    """Variable o nombre"""
    nombre: str
    
    def to_dict(self) -> dict:
        return {
            "tipo": "Identificador",
            "nombre": self.nombre
        }


@dataclass
class AccesoAtributo(ASTNode):
    """objeto.atributo"""
    objeto: str
    atributo: str
    
    def to_dict(self) -> dict:
        return {
            "tipo": "AccesoAtributo",
            "objeto": self.objeto,
            "atributo": self.atributo
        }


@dataclass
class AccesoIndice(ASTNode):
    """objeto[indice]"""
    objeto: str
    indice: ASTNode
    
    def to_dict(self) -> dict:
        return {
            "tipo": "AccesoIndice",
            "objeto": self.objeto,
            "indice": self.indice.to_dict()
        }


# === Literales ===

@dataclass
class Literal(ASTNode):
    """Valor literal: números, strings, booleanos"""
    valor: Any
    tipo: str  # "int", "float", "str", "bool", "None"
    
    def to_dict(self) -> dict:
        return {
            "tipo": "Literal",
            "valor": self.valor,
            "tipo_literal": self.tipo
        }


@dataclass
class ListaLiteral(ASTNode):
    """[1, 2, 3]"""
    elementos: List[ASTNode]
    
    def to_dict(self) -> dict:
        return {
            "tipo": "ListaLiteral",
            "elementos": [e.to_dict() for e in self.elementos]
        }


@dataclass
class DiccionarioLiteral(ASTNode):
    """{"clave": valor}"""
    pares: List[tuple[ASTNode, ASTNode]]
    
    def to_dict(self) -> dict:
        return {
            "tipo": "DiccionarioLiteral",
            "pares": [(k.to_dict(), v.to_dict()) for k, v in self.pares]
        }
