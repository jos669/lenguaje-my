"""
My Lenguaje - Editor Inteligente (Fase 6.5)
Editor TUI con syntax highlighting, autocompletado y auto-corrección
"""

import curses
import os
import sys
import re
from pathlib import Path
from typing import List, Dict, Optional, Tuple


class ColoresSintaxis:
    """Define los colores para syntax highlighting"""
    KEYWORD = 1
    STRING = 2
    COMMENT = 3
    NUMBER = 4
    FUNCTION = 5
    CLASS = 6
    OPERATOR = 7
    NORMAL = 0


class AutoCorrector:
    """Corrige automáticamente errores comunes"""
    
    CORRECCIONES = {
        'funtion': 'función', 'fucion': 'función', 'funcio': 'función',
        'imrpimir': 'imprimir', 'imprmir': 'imprimir',
        'retornr': 'retornar', 'retonar': 'retornar',
        '=>': '>=', '=<': '<=', '!!': '!=',
    }
    
    @classmethod
    def corregir_linea(cls, linea: str) -> str:
        resultado = linea
        for error, correccion in cls.CORRECCIONES.items():
            patron = r'\b' + re.escape(error.strip()) + r'\b'
            resultado = re.sub(patron, correccion.strip(), resultado, flags=re.IGNORECASE)
        resultado = cls._cerrar_parentesis(resultado)
        return resultado
    
    @classmethod
    def _cerrar_parentesis(cls, linea: str) -> str:
        cuenta = {
            '(': linea.count('(') - linea.count(')'),
            '[': linea.count('[') - linea.count(']'),
            '{': linea.count('{') - linea.count('}'),
        }
        resultado = linea.rstrip()
        for char, faltante in cuenta.items():
            if faltante > 0:
                cierre = ')' if char == '(' else (']' if char == '[' else '}')
                resultado += cierre * faltante
        return resultado


class Autocompletado:
    """Sistema de autocompletado inteligente"""
    
    KEYWORDS = [
        'definir', 'clase', 'función', 'retornar',
        'si', 'sino si', 'sino', 'para', 'en', 'mientras', 'rango',
        'intentar', 'excepto', 'finalmente', 'importar', 'como',
        'y', 'o', 'no', 'verdadero', 'falso', 'nulo',
        'imprimir', 'entrada', 'entero', 'flotante', 'cadena',
        'lista', 'diccionario', 'longitud', 'con', 'asíncrono', 'esperar',
    ]
    
    SNIPPETS = {
        'for': 'para {var} en rango({max}):\n    {cuerpo}',
        'if': 'si {condicion}:\n    {cuerpo}',
        'ifelse': 'si {condicion}:\n    {cuerpo}\nsino:\n    {otro}',
        'func': 'función {nombre}({params}):\n    {cuerpo}',
        'class': 'clase {nombre}:\n    función __init__(self):\n        {cuerpo}',
        'try': 'intentar:\n    {cuerpo}\nexcepto:\n    {manejo}',
        'while': 'mientras {condicion}:\n    {cuerpo}',
    }
    
    def __init__(self):
        self.variables_locales: List[str] = []
        self.funciones: List[str] = []
        self.clases: List[str] = []
    
    def actualizar_contexto(self, codigo: str):
        self.variables_locales = []
        self.funciones = []
        self.clases = []
        
        for linea in codigo.split('\n'):
            match = re.search(r'definir\s+(\w+)\s*=', linea)
            if match:
                self.variables_locales.append(match.group(1))
            match = re.search(r'función\s+(\w+)\s*\(', linea)
            if match:
                self.funciones.append(match.group(1))
            match = re.search(r'clase\s+(\w+)', linea)
            if match:
                self.clases.append(match.group(1))
    
    def obtener_sugerencias(self, texto_actual: str) -> List[Tuple[str, str, str]]:
        if not texto_actual:
            return []
        
        palabras = texto_actual.split()
        if not palabras:
            return []
        
        ultima = palabras[-1]
        if len(ultima) < 1:
            return []
        
        sugerencias = []
        
        for kw in self.KEYWORDS:
            if kw.startswith(ultima):
                sugerencias.append((kw, 'keyword', 'Palabra clave'))
        
        for var in self.variables_locales:
            if var.startswith(ultima):
                sugerencias.append((var, 'variable', 'Variable'))
        
        for func in self.funciones:
            if func.startswith(ultima):
                sugerencias.append((func, 'function', 'Función'))
        
        for clase in self.clases:
            if clase.startswith(ultima):
                sugerencias.append((clase, 'class', 'Clase'))
        
        for nombre, snippet in self.SNIPPETS.items():
            if nombre.startswith(ultima):
                sugerencias.append((nombre, 'snippet', f'Snippet'))
        
        return sugerencias[:10]
    
    def obtener_snippet(self, nombre: str) -> Optional[str]:
        return self.SNIPPETS.get(nombre)


class EditorMy:
    """Editor de texto inteligente para My Lenguaje"""
    
    def __init__(self, archivo: str = None):
        self.archivo = Path(archivo) if archivo else None
        self.lineas: List[str] = []
        self.cursor_x = 0
        self.cursor_y = 0
        self.scroll_y = 0
        self.scroll_x = 0
        self.modificado = False
        self.mensaje = ""
        self.mensaje_tiempo = 0
        self.mostrar_autocompletado = False
        self.sugerencias: List[Tuple[str, str, str]] = []
        self.sugerencia_seleccionada = 0
        
        self.autocompletado = Autocompletado()
        self.auto_corrector = AutoCorrector()
        
        if self.archivo and self.archivo.exists():
            self.cargar_archivo()
        else:
            self.lineas = [""]
    
    def cargar_archivo(self):
        try:
            with open(self.archivo, 'r', encoding='utf-8') as f:
                self.lineas = f.read().split('\n')
                if not self.lineas:
                    self.lineas = [""]
            self.modificado = False
            self.mensaje = f"Archivo cargado: {self.archivo.name}"
        except Exception as e:
            self.mensaje = f"Error al cargar: {e}"
    
    def guardar_archivo(self):
        if not self.archivo:
            self.archivo = Path("sin_nombre.my")
        try:
            with open(self.archivo, 'w', encoding='utf-8') as f:
                f.write('\n'.join(self.lineas))
            self.modificado = False
            self.mensaje = f"Guardado: {self.archivo.name}"
            self.mensaje_tiempo = 30
        except Exception as e:
            self.mensaje = f"Error al guardar: {e}"
    
    def ejecutar_codigo(self, stdscr):
        if not self.archivo:
            self.guardar_archivo()
        
        stdscr.clear()
        stdscr.addstr(0, 0, "Ejecutando código...", curses.color_pair(ColoresSintaxis.KEYWORD))
        stdscr.refresh()
        
        import subprocess
        try:
            result = subprocess.run(
                ['python', 'my.py', 'run', str(self.archivo)],
                capture_output=True, text=True, timeout=30
            )
            
            stdscr.clear()
            stdscr.addstr(0, 0, "=== RESULTADO ===", curses.color_pair(ColoresSintaxis.CLASS) | curses.A_BOLD)
            
            lineas_output = result.stdout.split('\n') + result.stderr.split('\n')
            for i, linea in enumerate(lineas_output[:30], start=2):
                if i < stdscr.getmaxyx()[0] - 2:
                    color = ColoresSintaxis.STRING if result.stderr else ColoresSintaxis.NORMAL
                    stdscr.addstr(i, 0, linea[:stdscr.getmaxyx()[1]-1], curses.color_pair(color))
            
            stdscr.addstr(stdscr.getmaxyx()[0]-2, 0, "Presiona cualquier tecla para continuar...", 
                         curses.color_pair(ColoresSintaxis.COMMENT))
            stdscr.refresh()
            stdscr.getch()
            
        except subprocess.TimeoutExpired:
            self.mensaje = "Timeout: el código tardó demasiado"
        except Exception as e:
            self.mensaje = f"Error al ejecutar: {e}"
    
    def aplicar_auto_correccion(self):
        if 0 <= self.cursor_y < len(self.lineas):
            linea_original = self.lineas[self.cursor_y]
            linea_corregida = self.auto_corrector.corregir_linea(linea_original)
            if linea_corregida != linea_original:
                self.lineas[self.cursor_y] = linea_corregida
                self.modificado = True
                self.mensaje = "Auto-corrección aplicada"
    
    def insertar_caracter(self, char: int):
        if self.cursor_y >= len(self.lineas):
            self.lineas.append("")
        
        linea = self.lineas[self.cursor_y]
        self.lineas[self.cursor_y] = linea[:self.cursor_x] + chr(char) + linea[self.cursor_x:]
        self.cursor_x += 1
        self.modificado = True
        
        # Auto-cerrar paréntesis
        if chr(char) in '([{':
            cierre = ')' if chr(char) == '(' else (']' if chr(char) == '[' else '}')
            linea = self.lineas[self.cursor_y]
            self.lineas[self.cursor_y] = linea[:self.cursor_x] + cierre + linea[self.cursor_x:]
    
    def manejar_tecla(self, tecla: int, stdscr) -> bool:
        self.autocompletado.actualizar_contexto('\n'.join(self.lineas))
        
        # Ctrl+S - Guardar
        if tecla == 19:
            self.guardar_archivo()
            return True
        
        # Ctrl+Q - Salir
        if tecla == 17:
            if self.modificado:
                self.mensaje = "¿Guardar antes de salir? (y/n)"
                stdscr.refresh()
                resp = stdscr.getch()
                if resp == ord('y'):
                    self.guardar_archivo()
            return False
        
        # Ctrl+E - Ejecutar
        if tecla == 5:
            self.ejecutar_codigo(stdscr)
            return True
        
        # Ctrl+R - Auto-corregir línea
        if tecla == 18:
            self.aplicar_auto_correccion()
            return True
        
        # Tab - Autocompletar
        if tecla == 9:
            if self.sugerencias:
                sugerencia = self.sugerencias[self.sugerencia_seleccionada]
                self._insertar_sugerencia(sugerencia[0])
            return True
        
        # Navegación autocompletado
        if self.mostrar_autocompletado and self.sugerencias:
            if tecla == curses.KEY_UP:
                self.sugerencia_seleccionada = max(0, self.sugerencia_seleccionada - 1)
                return True
            if tecla == curses.KEY_DOWN:
                self.sugerencia_seleccionada = min(len(self.sugerencias)-1, self.sugerencia_seleccionada + 1)
                return True
            if tecla == 27:
                self.mostrar_autocompletado = False
                return True
        
        # Flechas
        if tecla == curses.KEY_UP and self.cursor_y > 0:
            self.cursor_y -= 1
            self.cursor_x = min(self.cursor_x, len(self.lineas[self.cursor_y]))
        elif tecla == curses.KEY_DOWN and self.cursor_y < len(self.lineas) - 1:
            self.cursor_y += 1
            self.cursor_x = min(self.cursor_x, len(self.lineas[self.cursor_y]))
        elif tecla == curses.KEY_LEFT and self.cursor_x > 0:
            self.cursor_x -= 1
        elif tecla == curses.KEY_RIGHT and self.cursor_x < len(self.lineas[self.cursor_y]):
            self.cursor_x += 1
        elif tecla == curses.KEY_HOME:
            self.cursor_x = 0
        elif tecla == curses.KEY_END:
            self.cursor_x = len(self.lineas[self.cursor_y])
        
        # Backspace
        elif tecla in (127, curses.KEY_BACKSPACE, 8):
            if self.cursor_x > 0:
                linea = self.lineas[self.cursor_y]
                self.lineas[self.cursor_y] = linea[:self.cursor_x-1] + linea[self.cursor_x:]
                self.cursor_x -= 1
                self.modificado = True
            elif self.cursor_y > 0:
                self.cursor_x = len(self.lineas[self.cursor_y - 1])
                self.lineas[self.cursor_y - 1] += self.lineas[self.cursor_y]
                del self.lineas[self.cursor_y]
                self.cursor_y -= 1
                self.modificado = True
        
        # Delete
        elif tecla == curses.KEY_DC:
            if self.cursor_x < len(self.lineas[self.cursor_y]):
                linea = self.lineas[self.cursor_y]
                self.lineas[self.cursor_y] = linea[:self.cursor_x] + linea[self.cursor_x+1:]
                self.modificado = True
        
        # Enter
        elif tecla in (10, 13):
            linea = self.lineas[self.cursor_y]
            self.lineas[self.cursor_y] = linea[:self.cursor_x]
            self.lineas.insert(self.cursor_y + 1, linea[self.cursor_x:])
            self.cursor_y += 1
            self.cursor_x = 0
            self.modificado = True
            
            # Auto-indentación
            linea_anterior = self.lineas[self.cursor_y - 1]
            if linea_anterior.rstrip().endswith(':'):
                self.lineas[self.cursor_y] = '    ' + self.lineas[self.cursor_y]
                self.cursor_x = 4
        
        # Caracteres normales
        elif 32 <= tecla <= 126:
            self.insertar_caracter(tecla)
            texto_actual = self.lineas[self.cursor_y][:self.cursor_x]
            self.sugerencias = self.autocompletado.obtener_sugerencias(texto_actual)
            self.mostrar_autocompletado = len(self.sugerencias) > 0
            self.sugerencia_seleccionada = 0
        
        # Scroll
        alto, _ = stdscr.getmaxyx()
        if self.cursor_y >= self.scroll_y + alto - 3:
            self.scroll_y = self.cursor_y - alto + 3
        elif self.cursor_y < self.scroll_y:
            self.scroll_y = self.cursor_y
        
        return True
    
    def _insertar_sugerencia(self, sugerencia: str):
        linea = self.lineas[self.cursor_y]
        palabras = linea[:self.cursor_x].split()
        if palabras:
            palabra_actual = palabras[-1]
            inicio = self.cursor_x - len(palabra_actual)
            self.lineas[self.cursor_y] = linea[:inicio] + sugerencia + linea[self.cursor_x:]
            self.cursor_x = inicio + len(sugerencia)
            self.modificado = True
        self.mostrar_autocompletado = False
        self.sugerencias = []
    
    def _resaltar_sintaxis(self, linea: str) -> List[Tuple[str, int]]:
        resultado = []
        
        if '#' in linea:
            idx = linea.index('#')
            resultado.append((linea[idx:], ColoresSintaxis.COMMENT))
            linea = linea[:idx]
        
        patron_string = r'(".*?"|\'.*?\')'
        partes = re.split(f'({patron_string})', linea)
        
        for parte in partes:
            if not parte:
                continue
            
            if (parte.startswith('"') and parte.endswith('"')) or \
               (parte.startswith("'") and parte.endswith("'")):
                resultado.append((parte, ColoresSintaxis.STRING))
                continue
            
            keywords = ['definir', 'clase', 'función', 'retornar', 'si', 'sino', 
                       'para', 'en', 'mientras', 'rango', 'importar', 'como',
                       'intentar', 'excepto', 'finalmente', 'verdadero', 'falso',
                       'nulo', 'imprimir', 'y', 'o', 'no']
            
            palabras = re.split(r'(\W+)', parte)
            for palabra in palabras:
                if not palabra:
                    continue
                
                color = ColoresSintaxis.NORMAL
                if palabra in keywords:
                    color = ColoresSintaxis.KEYWORD
                elif palabra.isdigit() or re.match(r'\d+\.?\d*', palabra):
                    color = ColoresSintaxis.NUMBER
                elif palabra in ['+', '-', '*', '/', '%', '**', '==', '!=', '<', '>']:
                    color = ColoresSintaxis.OPERATOR
                
                resultado.append((palabra, color))
        
        return resultado
    
    def dibujar(self, stdscr):
        stdscr.clear()
        alto, ancho = stdscr.getmaxyx()
        
        # Título
        titulo = f" My Editor - {self.archivo.name if self.archivo else 'Sin nombre'} "
        if self.modificado:
            titulo += "(*) "
        stdscr.attron(curses.color_pair(ColoresSintaxis.CLASS) | curses.A_BOLD)
        stdscr.addstr(0, 0, titulo.ljust(ancho)[:ancho-1])
        stdscr.attroff(curses.color_pair(ColoresSintaxis.CLASS) | curses.A_BOLD)
        
        # Código
        for i in range(alto - 4):
            num_linea = i + self.scroll_y
            if num_linea >= len(self.lineas):
                break
            
            linea = self.lineas[num_linea]
            
            stdscr.attron(curses.color_pair(ColoresSintaxis.COMMENT))
            stdscr.addstr(i + 1, 0, f"{num_linea + 1:4} │ ")
            stdscr.attroff(curses.color_pair(ColoresSintaxis.COMMENT))
            
            partes = self._resaltar_sintaxis(linea[self.scroll_x:ancho-7])
            x = 7
            for texto, color in partes:
                if x + len(texto) > ancho - 1:
                    texto = texto[:ancho - x - 1]
                try:
                    stdscr.attron(curses.color_pair(color))
                    stdscr.addstr(i + 1, x, texto)
                    stdscr.attroff(curses.color_pair(color))
                except:
                    pass
                x += len(texto)
            
            if num_linea == self.cursor_y:
                try:
                    stdscr.move(i + 1, 7 + self.cursor_x - self.scroll_x)
                except:
                    pass
        
        # Barra de estado
        barra = f" Línea: {self.cursor_y + 1} | Col: {self.cursor_x + 1} | "
        barra += "Modificado" if self.modificado else "Guardado"
        barra += " | ^S:Guardar ^E:Ejecutar ^Q:Salir ^R:Auto-corregir ^Tab:Autocompletar "
        
        stdscr.attron(curses.color_pair(ColoresSintaxis.KEYWORD) | curses.A_REVERSE)
        stdscr.addstr(alto - 2, 0, barra.ljust(ancho)[:ancho-1])
        stdscr.attroff(curses.color_pair(ColoresSintaxis.KEYWORD) | curses.A_REVERSE)
        
        # Mensaje
        if self.mensaje:
            stdscr.attron(curses.color_pair(ColoresSintaxis.STRING) | curses.A_BOLD)
            stdscr.addstr(alto - 1, 0, f" {self.mensaje} ".ljust(ancho)[:ancho-1])
            stdscr.attroff(curses.color_pair(ColoresSintaxis.STRING) | curses.A_BOLD)
            self.mensaje_tiempo -= 1
            if self.mensaje_tiempo <= 0:
                self.mensaje = ""
        
        # Autocompletado panel
        if self.mostrar_autocompletado and self.sugerencias:
            panel_y = self.cursor_y - self.scroll_y + 1
            panel_x = 7 + self.cursor_x - self.scroll_x
            
            if panel_y + len(self.sugerencias) + 2 < alto - 2:
                stdscr.attron(curses.color_pair(ColoresSintaxis.NORMAL) | curses.A_REVERSE)
                for i, (sug, tipo, desc) in enumerate(self.sugerencias[:5]):
                    if i == self.sugerencia_seleccionada:
                        stdscr.attron(curses.A_BOLD)
                    try:
                        stdscr.addstr(panel_y + i, panel_x, f" {sug} ({tipo}) ")
                    except:
                        pass
                    if i == self.sugerencia_seleccionada:
                        stdscr.attroff(curses.A_BOLD)
                stdscr.attroff(curses.color_pair(ColoresSintaxis.NORMAL) | curses.A_REVERSE)
        
        stdscr.refresh()
    
    def ejecutar(self, stdscr):
        curses.start_color()
        curses.use_default_colors()
        curses.init_pair(ColoresSintaxis.KEYWORD, curses.COLOR_CYAN, -1)
        curses.init_pair(ColoresSintaxis.STRING, curses.COLOR_GREEN, -1)
        curses.init_pair(ColoresSintaxis.COMMENT, curses.COLOR_YELLOW, -1)
        curses.init_pair(ColoresSintaxis.NUMBER, curses.COLOR_MAGENTA, -1)
        curses.init_pair(ColoresSintaxis.FUNCTION, curses.COLOR_BLUE, -1)
        curses.init_pair(ColoresSintaxis.CLASS, curses.COLOR_WHITE, -1)
        curses.init_pair(ColoresSintaxis.OPERATOR, curses.COLOR_RED, -1)
        curses.init_pair(ColoresSintaxis.NORMAL, -1, -1)
        
        curses.curs_set(1)
        stdscr.nodelay(False)
        stdscr.keypad(True)
        
        corriendo = True
        while corriendo:
            self.dibujar(stdscr)
            tecla = stdscr.getch()
            corriendo = self.manejar_tecla(tecla, stdscr)


def editar_archivo(archivo: str = None):
    """Función principal para abrir el editor"""
    editor = EditorMy(archivo)
    
    def main(stdscr):
        editor.ejecutar(stdscr)
    
    curses.wrapper(main)


if __name__ == '__main__':
    archivo = sys.argv[1] if len(sys.argv) > 1 else None
    editar_archivo(archivo)
