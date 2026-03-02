"""
My Lenguaje - Debugger Integrado (Fase 5)
Debugger paso a paso con breakpoints y inspección de variables
"""

import sys
import traceback
from typing import Any, Callable, Dict, List, Optional, Set
from dataclasses import dataclass, field


@dataclass
class Breakpoint:
    """Representa un breakpoint"""
    linea: int
    condicion: Optional[str] = None
    habilitado: bool = True
    hit_count: int = 0


@dataclass
class StackFrame:
    """Representa un frame de la pila de ejecución"""
    nombre_funcion: str
    archivo: str
    linea: int
    variables: Dict[str, Any] = field(default_factory=dict)


class Debugger:
    """
    Debugger integrado para My Lenguaje
    
    Características:
    - Breakpoints con condición
    - Ejecución paso a paso (step, next, continue)
    - Inspección de variables
    - Stack trace
    - Evaluar expresiones en contexto
    """
    
    def __init__(self):
        self.breakpoints: Dict[str, Set[Breakpoint]] = {}  # archivo -> breakpoints
        self.stack: List[StackFrame] = []
        self.contexto: Dict[str, Any] = {}
        self.archivo_actual: Optional[str] = None
        self.linea_actual: int = 0
        self.en_debug: bool = False
        self.paso_a_paso: bool = False
        self.comando: Optional[str] = None
        
        # Comandos disponibles
        self.comandos = {
            'n': self._next,
            'next': self._next,
            's': self._step,
            'step': self._step,
            'c': self._continue,
            'continue': self._continue,
            'q': self._quit,
            'quit': self._quit,
            'p': self._print_var,
            'print': self._print_var,
            'l': self._list_vars,
            'list': self._list_vars,
            'w': self._where,
            'where': self._where,
            'b': self._set_breakpoint,
            'break': self._set_breakpoint,
            'h': self._help,
            'help': self._help,
        }
    
    def ejecutar_con_debug(self, codigo: str, contexto: dict = None) -> dict:
        """
        Ejecuta código con debugging habilitado
        
        Args:
            codigo: Código a ejecutar
            contexto: Contexto de ejecución
            
        Returns:
            Contexto después de la ejecución
        """
        self.en_debug = True
        self.contexto = contexto if contexto else {'__name__': '__main__'}
        
        # Ejecutar línea por línea
        lineas = codigo.split('\n')
        
        try:
            for i, linea in enumerate(lineas, start=1):
                self.linea_actual = i
                self.archivo_actual = '<string>'
                
                # Verificar breakpoints
                if self._debe_parar(i):
                    self._loop_interactivo(linea, i)
                
                # Ejecutar línea
                if linea.strip():
                    try:
                        exec(linea, self.contexto)
                    except Exception as e:
                        print(f"Error en línea {i}: {e}")
                        if self.en_debug:
                            self._mostrar_error(e, i)
                
                # Modo paso a paso
                if self.paso_a_paso and linea.strip():
                    self._loop_interactivo(linea, i)
                    
        except Exception as e:
            print(f"Error: {e}")
            traceback.print_exc()
        
        self.en_debug = False
        return self.contexto
    
    def _debe_parar(self, linea: int) -> bool:
        """Verifica si debe parar en esta línea"""
        if self.archivo_actual not in self.breakpoints:
            return False
        
        for bp in self.breakpoints[self.archivo_actual]:
            if bp.linea == linea and bp.habilitado:
                bp.hit_count += 1
                
                # Verificar condición
                if bp.condicion:
                    try:
                        if not eval(bp.condicion, self.contexto):
                            return False
                    except:
                        pass
                
                return True
        
        return False
    
    def _loop_interactivo(self, linea: str, num_linea: int):
        """Loop interactivo del debugger"""
        print(f"\n📍 Línea {num_linea}: {linea.strip()}")
        
        while self.en_debug:
            try:
                entrada = input("(my-debug) ").strip()
                
                if not entrada:
                    # Enter repite último comando
                    if self.comando:
                        self.comandos.get(self.comando, lambda: None)()
                    continue
                
                partes = entrada.split(maxsplit=1)
                cmd = partes[0].lower()
                args = partes[1] if len(partes) > 1 else None
                
                self.comando = cmd
                
                if cmd in self.comandos:
                    if args:
                        self.comandos[cmd](args)
                    else:
                        self.comandos[cmd]()
                else:
                    # Intentar evaluar como expresión Python
                    try:
                        resultado = eval(entrada, self.contexto)
                        print(f"= {resultado}")
                    except Exception as e:
                        print(f"Comando desconocido: {cmd}")
                
            except KeyboardInterrupt:
                print("\nUse 'q' para salir o 'c' para continuar")
            except EOFError:
                self._quit()
                break
    
    def _next(self, arg=None):
        """Ejecuta siguiente línea (no entra a funciones)"""
        self.paso_a_paso = False
        self.en_debug = False
        print("→ Ejecutando siguiente línea...")
    
    def _step(self, arg=None):
        """Ejecuta siguiente línea (entra a funciones)"""
        self.paso_a_paso = True
        self.en_debug = False
        print("→ Paso a paso activado...")
    
    def _continue(self, arg=None):
        """Continúa hasta el próximo breakpoint"""
        self.paso_a_paso = False
        self.en_debug = False
        print("→ Continuando ejecución...")
    
    def _quit(self, arg=None):
        """Sale del debugger"""
        self.en_debug = False
        self.paso_a_paso = False
        print("Saliendo del debugger")
    
    def _print_var(self, arg=None):
        """Imprime el valor de una variable"""
        if not arg:
            print("Uso: p <variable>")
            return
        
        try:
            valor = eval(arg, self.contexto)
            print(f"{arg} = {valor!r}")
        except Exception as e:
            print(f"Error: {e}")
    
    def _list_vars(self, arg=None):
        """Lista todas las variables en contexto"""
        print("\n📋 Variables:")
        for nombre, valor in self.contexto.items():
            if not nombre.startswith('__'):
                print(f"  {nombre}: {valor!r}")
        print()
    
    def _where(self, arg=None):
        """Muestra el stack trace"""
        print("\n📚 Stack:")
        for i, frame in enumerate(self.stack):
            print(f"  #{i} {frame.nombre_funcion}() en {frame.archivo}:{frame.linea}")
        print()
    
    def _set_breakpoint(self, arg=None):
        """Establece un breakpoint"""
        if not arg:
            print("Uso: b <línea> [condición]")
            return
        
        partes = arg.split(maxsplit=1)
        try:
            linea = int(partes[0])
            condicion = partes[1] if len(partes) > 1 else None
            
            if self.archivo_actual not in self.breakpoints:
                self.breakpoints[self.archivo_actual] = set()
            
            bp = Breakpoint(linea=linea, condicion=condicion)
            self.breakpoints[self.archivo_actual].add(bp)
            print(f"✓ Breakpoint en línea {linea}")
            
            if condicion:
                print(f"  Condición: {condicion}")
                
        except ValueError:
            print("Línea inválida")
    
    def _help(self, arg=None):
        """Muestra ayuda"""
        print("""
📖 Comandos del debugger:
  n, next       - Ejecutar siguiente línea
  s, step       - Paso a paso (entra a funciones)
  c, continue   - Continuar hasta próximo breakpoint
  q, quit       - Salir del debugger
  p, print      - Imprimir variable (p <var>)
  l, list       - Listar variables
  w, where      - Mostrar stack trace
  b, break      - Set breakpoint (b <línea> [cond])
  h, help       - Mostrar esta ayuda
  
Sin comando: Evaluar expresión Python
""")
    
    def _mostrar_error(self, error: Exception, linea: int):
        """Muestra información detallada del error"""
        print(f"\n❌ Error en línea {linea}:")
        print(f"   Tipo: {type(error).__name__}")
        print(f"   Mensaje: {error}")
        print()


def debug(codigo: str, contexto: dict = None) -> dict:
    """Función de conveniencia para ejecutar con debug"""
    debugger = Debugger()
    return debugger.ejecutar_con_debug(codigo, contexto)
