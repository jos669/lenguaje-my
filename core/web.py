"""
My Lenguaje - Web Framework Mínimo (Fase 6)
Framework web simple para aplicaciones básicas
"""

import json
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
from typing import Callable, Dict, List, Optional, Any


class Solicitud:
    """Representa una solicitud HTTP"""
    
    def __init__(self, metodo: str, ruta: str, headers: dict, cuerpo: str = ""):
        self.metodo = metodo
        self.ruta = ruta
        self.headers = headers
        self.cuerpo = cuerpo
        self.params = parse_qs(urlparse(ruta).query)
        self.json = None
        
        if cuerpo and 'application/json' in headers.get('Content-Type', ''):
            try:
                self.json = json.loads(cuerpo)
            except:
                pass
    
    def obtener_param(self, nombre: str, default=None):
        """Obtiene un parámetro de la URL"""
        valores = self.params.get(nombre, [default])
        return valores[0] if valores else default


class Respuesta:
    """Representa una respuesta HTTP"""
    
    def __init__(self, cuerpo: str, estado: int = 200, headers: dict = None):
        self.cuerpo = cuerpo
        self.estado = estado
        self.headers = headers or {}
    
    @classmethod
    def json(cls, datos: dict, estado: int = 200):
        """Crea respuesta JSON"""
        return cls(
            cuerpo=json.dumps(datos),
            estado=estado,
            headers={'Content-Type': 'application/json'}
        )
    
    @classmethod
    def html(cls, html: str, estado: int = 200):
        """Crea respuesta HTML"""
        return cls(
            cuerpo=html,
            estado=estado,
            headers={'Content-Type': 'text/html'}
        )
    
    @classmethod
    def texto(cls, texto: str, estado: int = 200):
        """Crea respuesta de texto plano"""
        return cls(cuerpo=texto, estado=estado)
    
    @classmethod
    def no_encontrado(cls):
        """Respuesta 404"""
        return cls(cuerpo="404 - No encontrado", estado=404)
    
    @classmethod
    def error(cls, mensaje: str, estado: int = 500):
        """Respuesta de error"""
        return cls(cuerpo=json.dumps({'error': mensaje}), estado=estado, headers={'Content-Type': 'application/json'})


class AplicacionWeb:
    """
    Framework web mínimo para My Lenguaje
    
    Ejemplo:
        app = AplicacionWeb()
        
        @app.ruta("/")
        función inicio():
            retornar "¡Hola Mundo!"
        
        @app.ruta("/usuario/<id>")
        función perfil(id):
            retornar f"Perfil {id}"
        
        app.ejecutar(puerto=8080)
    """
    
    def __init__(self):
        self.rutas: Dict[str, Dict[str, Callable]] = {}
        self.middlewares: List[Callable] = []
    
    def ruta(self, patron: str, metodos: List[str] = None):
        """
        Decorador para registrar rutas
        
        Args:
            patron: Patrón de ruta (ej: "/usuario/<id>")
            metodos: Lista de métodos HTTP (default: ["GET"])
        """
        metodos = metodos or ["GET"]
        
        def decorador(func: Callable):
            for metodo in metodos:
                if metodo not in self.rutas:
                    self.rutas[metodo] = {}
                self.rutas[metodo][patron] = func
            return func
        
        return decorador
    
    def agregar_middleware(self, func: Callable):
        """Agrega un middleware"""
        self.middlewares.append(func)
    
    def _encontrar_ruta(self, metodo: str, ruta: str) -> tuple:
        """Encuentra la función para una ruta"""
        if metodo not in self.rutas:
            return None, {}

        for patron, func in self.rutas[metodo].items():
            # Convertir patrón a regex CORREGIDO
            import re
            patron_regex = re.sub(r'<(\w+)>', r'(?P<\1>[^/]+)', patron)
            
            match = re.match(f'^{patron_regex}$', ruta)

            if match:
                return func, match.groupdict()

        return None, {}
    
    def manejar_solicitud(self, solicitud: Solicitud) -> Respuesta:
        """Maneja una solicitud HTTP"""
        # Ejecutar middlewares
        for middleware in self.middlewares:
            resultado = middleware(solicitud)
            if resultado:
                return resultado
        
        # Encontrar ruta
        func, params = self._encontrar_ruta(solicitud.metodo, solicitud.ruta)
        
        if not func:
            return Respuesta.no_encontrado()
        
        try:
            # Ejecutar handler
            if params:
                resultado = func(**params)
            else:
                resultado = func()
            
            # Convertir resultado a Respuesta
            if isinstance(resultado, Respuesta):
                return resultado
            elif isinstance(resultado, dict):
                return Respuesta.json(resultado)
            elif isinstance(resultado, str):
                return Respuesta.texto(resultado)
            else:
                return Respuesta.texto(str(resultado))
        
        except Exception as e:
            return Respuesta.error(str(e), 500)
    
    def ejecutar(self, puerto: int = 8000, host: str = "localhost"):
        """Ejecuta el servidor web"""
        
        class Handler(BaseHTTPRequestHandler):
            def __init__(self, app, *args, **kwargs):
                self.app = app
                super().__init__(*args, **kwargs)
            
            def do_GET(self):
                self._manejar("GET")
            
            def do_POST(self):
                self._manejar("POST")
            
            def do_PUT(self):
                self._manejar("PUT")
            
            def do_DELETE(self):
                self._manejar("DELETE")
            
            def _manejar(self, metodo: str):
                # Leer cuerpo
                longitud = int(self.headers.get('Content-Length', 0))
                cuerpo = self.rfile.read(longitud).decode('utf-8') if longitud else ""
                
                # Crear solicitud
                solicitud = Solicitud(
                    metodo=metodo,
                    ruta=self.path,
                    headers=dict(self.headers),
                    cuerpo=cuerpo
                )
                
                # Manejar
                respuesta = self.app.manejar_solicitud(solicitud)
                
                # Enviar respuesta
                self.send_response(respuesta.estado)
                for header, valor in respuesta.headers.items():
                    self.send_header(header, valor)
                self.end_headers()
                self.wfile.write(respuesta.cuerpo.encode('utf-8'))
        
        # Crear handler con la app
        def crear_handler(*args, **kwargs):
            return Handler(self, *args, **kwargs)
        
        servidor = HTTPServer((host, puerto), crear_handler)
        
        print(f"🌐 Servidor web iniciado")
        print(f"   http://{host}:{puerto}")
        print(f"   Presiona Ctrl+C para detener\n")
        
        try:
            servidor.serve_forever()
        except KeyboardInterrupt:
            print("\n⏹️  Servidor detenido")
            servidor.shutdown()


# Funciones de conveniencia
def crear_aplicacion() -> AplicacionWeb:
    """Crea una nueva aplicación web"""
    return AplicacionWeb()
