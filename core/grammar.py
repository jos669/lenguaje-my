"""
My Lenguaje - Gramática Formal (Fase 3)
Gramática EBNF completa para Lark con todas las características
"""

GRAMATICA_MY = r"""
// Comentarios
COMMENT: "#" /[^\n]*/
%ignore COMMENT

// Whitespace
WS: /[ \t]+/
%ignore WS

NEWLINE: /\r?\n/

// Strings
STRING: "\"" /[^\n"]*/ "\"" | "'" /[^\n']*/ "'"

// Números
INT: "-"? /[0-9]+/
FLOAT: "-"? /[0-9]+\.[0-9]+/

// Keywords principales
DEFINIR: "definir"
CLASE: "clase"
FUNCION: "función"
RETORNAR: "retornar"

// Condicionales
SI: "si"
SINO_SI: "sino" WS "si"
SINO: "sino"

// Bucles
PARA: "para"
EN: "en"
MIENTRAS: "mientras"
RANGO: "rango"

// Excepciones
INTENTAR: "intentar"
EXCEPTO: "excepto"
FINALMENTE: "finalmente"

// Importaciones
IMPORTAR: "importar"
COMO: "como"

// Operadores lógicos
Y: "y"
O: "o"
NO: "no"
VERDADERO: "verdadero"
FALSO: "falso"
NULO: "nulo"

// Builtins
IMPRIMIR: "imprimir"
ENTRADA: "entrada"
ENTERO: "entero"
FLOTANTE: "flotante"
CADENA: "cadena"
LISTA: "lista"
DICCIONARIO: "diccionario"
LONGITUD: "longitud"

// Tipos opcionales (Fase 3)
TIPO_ENTERO: "entero"
TIPO_FLOTANTE: "flotante"  
TIPO_CADENA: "cadena"
TIPO_BOOLEANO: "booleano"
TIPO_LISTA: "lista"
TIPO_DICT: "dict"

// Identificadores
IDENTIFIER: /[a-zA-Z_][a-zA-Z0-9_]*/

// Operadores
OP_SUMA: "+"
OP_RESTA: "-"
OP_MULT: "*"
OP_DIV: "/"
OP_MOD: "%"
OP_POTENCIA: "**"
OP_IGUAL: "=="
OP_DIFERENTE: "!="
OP_MAYOR: ">"
OP_MENOR: "<"
OP_MAYOR_IGUAL: ">="
OP_MENOR_IGUAL: "<="
OP_ASIGNAR: "="

// Delimitadores
LPAREN: "("
RPAREN: ")"
LBRACKET: "["
RBRACKET: "]"
LBRACE: "{"
RBRACE: "}"
COMMA: ","
COLON: ":"
DOT: "."
ARROW: "->"

// === Reglas de Gramática ===

start: statement*

statement: definicion_var NEWLINE
         | definicion_funcion
         | definicion_clase  
         | condicional
         | bucle_para
         | bucle_mientras
         | try_except
         | importacion NEWLINE
         | retorno NEWLINE
         | asignacion NEWLINE
         | expresion_stmt NEWLINE

// Definición de variable con tipo opcional (Fase 3)
definicion_var: DEFINIR IDENTIFIER (COLON tipo)? OP_ASIGNAR expresion

// Tipo opcional (Fase 3)
tipo: TIPO_ENTERO | TIPO_FLOTANTE | TIPO_CADENA | TIPO_BOOLEANO | TIPO_LISTA | TIPO_DICT | IDENTIFIER

// Definición de función con tipos opcionales (Fase 3)
definicion_funcion: FUNCION IDENTIFIER parametros (ARROW tipo)? COLON NEWLINE INDENT statement+ DEDENT

// Parámetros con tipos opcionales (Fase 3)
parametros: LPAREN (parametro (COMMA parametro)*)? RPAREN
parametro: IDENTIFIER (COLON tipo)?

// Definición de clase
definicion_clase: CLASE IDENTIFIER (LPAREN IDENTIFIER RPAREN)? COLON NEWLINE INDENT statement+ DEDENT

// Condicionales
condicional: SI expresion COLON NEWLINE INDENT statement+ DEDENT (sino_si)* (sino)?
sino_si: SINO_SI expresion COLON NEWLINE INDENT statement+ DEDENT
sino: SINO COLON NEWLINE INDENT statement+ DEDENT

// Bucles
bucle_para: PARA IDENTIFIER EN expresion COLON NEWLINE INDENT statement+ DEDENT
bucle_mientras: MIENTRAS expresion COLON NEWLINE INDENT statement+ DEDENT

// Try-except-finally
try_except: INTENTAR COLON NEWLINE INDENT statement+ DEDENT except_block+ (finally_block)?
except_block: EXCEPTO IDENTIFIER? COLON NEWLINE INDENT statement+ DEDENT
finally_block: FINALMENTE COLON NEWLINE INDENT statement+ DEDENT

// Importación (Fase 3)
// NEWLINE ya está incluido en la regla statement
importacion: IMPORTAR modulo (COMO IDENTIFIER)?
modulo: IDENTIFIER (DOT IDENTIFIER)*

// Retorno
retorno: RETORNAR expresion?

// Asignación
asignacion: target OP_ASIGNAR expresion
target: IDENTIFIER | IDENTIFIER DOT IDENTIFIER | IDENTIFIER LBRACKET expresion RBRACKET

// Expresión como statement
expresion_stmt: expresion

// === Expresiones ===

expresion: or_expr

or_expr: and_expr (O and_expr)*
and_expr: not_expr (Y not_expr)*
not_expr: NO not_expr | comparison
comparison: sum_expr (comp_op sum_expr)*
comp_op: OP_IGUAL | OP_DIFERENTE | OP_MAYOR | OP_MENOR | OP_MAYOR_IGUAL | OP_MENOR_IGUAL
sum_expr: term ((OP_SUMA | OP_RESTA) term)*
term: factor ((OP_MULT | OP_DIV | OP_MOD) factor)*
factor: potencia | (OP_SUMA | OP_RESTA) factor
potencia: atom (OP_POTENCIA atom)*

atom: LPAREN expresion RPAREN
    | literal
    | llamada_funcion
    | lista_literal
    | diccionario_literal
    | list_comprehension
    | acceso_atributo
    | IDENTIFIER

literal: INT | FLOAT | STRING | VERDADERO | FALSO | NULO

llamada_funcion: builtin LPAREN (expresion (COMMA expresion)*)? RPAREN
builtin: RANGO | IMPRIMIR | ENTRADA | ENTERO | FLOTANTE | CADENA | LISTA | DICCIONARIO | LONGITUD | IDENTIFIER

acceso_atributo: IDENTIFIER DOT IDENTIFIER

// Lista literal
lista_literal: LBRACKET (expresion (COMMA expresion)*)? RBRACKET

// Diccionario literal
diccionario_literal: LBRACE (expresion COLON expresion (COMMA expresion COLON expresion)*)? RBRACE

// List comprehension (Fase 3)
list_comprehension: LBRACKET expresion PARA IDENTIFIER EN expresion RBRACKET

// Indentación
INDENT: /    /
DEDENT: /\n(?!\n)/
"""
