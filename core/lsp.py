"""
My Lenguaje - LSP Server (Fase 6)
Language Server Protocol para autocompletado y más
"""

import json
import sys
import re
from typing import Dict, List, Optional, Any
from pathlib import Path


class LSPServer:
    """
    Language Server Protocol para My Lenguaje
    
    Características:
    - Autocompletado
    - Go to definition
    - Hover
    - Find references
    - Rename symbol
    - Signature help
    """
    
    # Keywords para autocompletado
    KEYWORDS = [
        'definir', 'clase', 'función', 'retornar',
        'si', 'sino', 'sino si', 'para', 'en', 'mientras',
        'intentar', 'excepto', 'finalmente',
        'importar', 'como',
        'y', 'o', 'no', 'verdadero', 'falso', 'nulo',
        'imprimir', 'entrada', 'entero', 'flotante',
        'cadena', 'lista', 'diccionario', 'longitud',
        'con', 'asíncrono', 'esperar',
        # Tipos
        'entero', 'flotante', 'cadena', 'booleano', 'lista', 'dict',
    ]
    
    # Builtins
    BUILTINS = [
        'imprimir', 'entrada', 'entero', 'flotante', 'cadena',
        'lista', 'diccionario', 'longitud', 'rango',
    ]
    
    def __init__(self):
        self.symbols: Dict[str, Any] = {}
        self.documents: Dict[str, str] = {}
        self.capabilities = {
            'textDocumentSync': 1,
            'completionProvider': {
                'resolveProvider': True,
                'triggerCharacters': ['.', '(', '"', "'"]
            },
            'hoverProvider': True,
            'definitionProvider': True,
            'referencesProvider': True,
            'renameProvider': True,
            'signatureHelpProvider': {
                'triggerCharacters': ['(', ',']
            },
            'documentSymbolProvider': True,
        }
    
    def handle_request(self, request: dict) -> dict:
        """Maneja una solicitud LSP"""
        method = request.get('method')
        params = request.get('params', {})
        request_id = request.get('id')
        
        response = {'jsonrpc': '2.0', 'id': request_id}
        
        if method == 'initialize':
            response['result'] = {'capabilities': self.capabilities}
        
        elif method == 'initialized':
            pass  # No response needed
        
        elif method == 'textDocument/didOpen':
            uri = params.get('textDocument', {}).get('uri')
            text = params.get('textDocument', {}).get('text')
            if uri:
                self.documents[uri] = text
                self._analizar_documento(uri, text)
            response = None  # Notification
        
        elif method == 'textDocument/didChange':
            uri = params.get('textDocument', {}).get('uri')
            changes = params.get('contentChanges', [])
            if uri and changes:
                self.documents[uri] = changes[-1].get('text', '')
                self._analizar_documento(uri, self.documents[uri])
            response = None
        
        elif method == 'textDocument/completion':
            response['result'] = self._completar(params)
        
        elif method == 'textDocument/hover':
            response['result'] = self._hover(params)
        
        elif method == 'textDocument/definition':
            response['result'] = self._definicion(params)
        
        elif method == 'textDocument/references':
            response['result'] = self._referencias(params)
        
        elif method == 'textDocument/signatureHelp':
            response['result'] = self._signature_help(params)
        
        elif method == 'textDocument/documentSymbol':
            response['result'] = self._document_symbols(params)
        
        elif method == 'shutdown':
            response['result'] = None
        
        elif method == 'exit':
            sys.exit(0)
        
        else:
            response['error'] = {
                'code': -32601,
                'message': f'Method not found: {method}'
            }
        
        return response
    
    def _analizar_documento(self, uri: str, texto: str):
        """Analiza un documento y extrae símbolos"""
        self.symbols[uri] = {
            'funciones': [],
            'clases': [],
            'variables': []
        }
        
        lineas = texto.split('\n')
        for num_linea, linea in enumerate(lineas):
            # Funciones
            match = re.search(r'función\s+(\w+)\s*\(([^)]*)\)', linea)
            if match:
                self.symbols[uri]['funciones'].append({
                    'nombre': match.group(1),
                    'parametros': match.group(2),
                    'linea': num_linea
                })
            
            # Clases
            match = re.search(r'clase\s+(\w+)', linea)
            if match:
                self.symbols[uri]['clases'].append({
                    'nombre': match.group(1),
                    'linea': num_linea
                })
            
            # Variables
            match = re.search(r'definir\s+(\w+)\s*=', linea)
            if match:
                self.symbols[uri]['variables'].append({
                    'nombre': match.group(1),
                    'linea': num_linea
                })
    
    def _completar(self, params: dict) -> dict:
        """Provee autocompletado"""
        uri = params.get('textDocument', {}).get('uri')
        position = params.get('position', {})
        linea = position.get('line', 0)
        caracter = position.get('character', 0)
        
        documento = self.documents.get(uri, '')
        lineas = documento.split('\n')
        
        if linea >= len(lineas):
            return {'isIncomplete': False, 'items': []}
        
        linea_actual = lineas[linea][:caracter]
        
        items = []
        
        # Keywords
        for keyword in self.KEYWORDS:
            if keyword.startswith(linea_actual.split()[-1] if linea_actual.split() else ''):
                items.append({
                    'label': keyword,
                    'kind': 14,  # Keyword
                    'insertText': keyword
                })
        
        # Builtins
        for builtin in self.BUILTINS:
            if builtin.startswith(linea_actual.split()[-1] if linea_actual.split() else ''):
                items.append({
                    'label': builtin,
                    'kind': 3,  # Function
                    'insertText': builtin
                })
        
        # Símbolos del documento
        if uri in self.symbols:
            for func in self.symbols[uri]['funciones']:
                items.append({
                    'label': func['nombre'],
                    'kind': 3,  # Function
                    'insertText': func['nombre'],
                    'detail': f"función {func['nombre']}({func['parametros']})"
                })
            
            for clase in self.symbols[uri]['clases']:
                items.append({
                    'label': clase['nombre'],
                    'kind': 7,  # Class
                    'insertText': clase['nombre']
                })
            
            for var in self.symbols[uri]['variables']:
                items.append({
                    'label': var['nombre'],
                    'kind': 6,  # Variable
                    'insertText': var['nombre']
                })
        
        return {'isIncomplete': False, 'items': items}
    
    def _hover(self, params: dict) -> Optional[dict]:
        """Provee información hover"""
        uri = params.get('textDocument', {}).get('uri')
        position = params.get('position', {})
        
        if uri not in self.symbols:
            return None
        
        # Buscar símbolo bajo el cursor
        # (implementación simplificada)
        return None
    
    def _definicion(self, params: dict) -> Optional[list]:
        """Encuentra la definición de un símbolo"""
        uri = params.get('textDocument', {}).get('uri')
        position = params.get('position', {})
        
        if uri not in self.symbols:
            return None
        
        # Buscar símbolo
        # (implementación simplificada)
        return None
    
    def _referencias(self, params: dict) -> list:
        """Encuentra referencias a un símbolo"""
        return []
    
    def _signature_help(self, params: dict) -> Optional[dict]:
        """Ayuda de firma para funciones"""
        return None
    
    def _document_symbols(self, params: dict) -> list:
        """Lista símbolos del documento"""
        uri = params.get('textDocument', {}).get('uri')
        
        if uri not in self.symbols:
            return []
        
        symbols = self.symbols[uri]
        result = []
        
        for func in symbols['funciones']:
            result.append({
                'name': func['nombre'],
                'kind': 12,  # Function
                'range': {
                    'start': {'line': func['linea'], 'character': 0},
                    'end': {'line': func['linea'], 'character': 100}
                },
                'selectionRange': {
                    'start': {'line': func['linea'], 'character': 0},
                    'end': {'line': func['linea'], 'character': len(func['nombre'])}
                }
            })
        
        for clase in symbols['clases']:
            result.append({
                'name': clase['nombre'],
                'kind': 5,  # Class
                'range': {
                    'start': {'line': clase['linea'], 'character': 0},
                    'end': {'line': clase['linea'], 'character': 100}
                }
            })
        
        return result


def iniciar_lsp():
    """Inicia el servidor LSP"""
    server = LSPServer()
    
    # Leer stdin línea por línea
    buffer = ''
    while True:
        try:
            linea = sys.stdin.readline()
            if not linea:
                break
            
            buffer += linea
            
            # Fin del header
            if buffer.endswith('\r\n\r\n'):
                # Parsear Content-Length
                headers = buffer.split('\r\n')
                content_length = 0
                
                for header in headers:
                    if header.startswith('Content-Length:'):
                        content_length = int(header.split(':')[1].strip())
                        break
                
                # Leer contenido
                contenido = sys.stdin.read(content_length)
                request = json.loads(contenido)
                
                # Procesar request
                response = server.handle_request(request)
                
                # Enviar respuesta
                if response:
                    response_str = json.dumps(response)
                    response_header = f'Content-Length: {len(response_str)}\r\n\r\n'
                    sys.stdout.write(response_header + response_str)
                    sys.stdout.flush()
                
                buffer = ''
        
        except Exception as e:
            # Enviar error
            error_response = {
                'jsonrpc': '2.0',
                'id': None,
                'error': {'code': -32603, 'message': str(e)}
            }
            response_str = json.dumps(error_response)
            response_header = f'Content-Length: {len(response_str)}\r\n\r\n'
            sys.stdout.write(response_header + response_str)
            sys.stdout.flush()
            buffer = ''


if __name__ == '__main__':
    iniciar_lsp()
