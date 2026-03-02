"""
My Lenguaje - Generador de Documentación (Fase 6)
Genera documentación automática desde el código
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field


@dataclass
class DocItem:
    """Elemento documentado"""
    nombre: str
    tipo: str  # funcion, clase, variable, modulo
    descripcion: str = ""
    args: List[str] = field(default_factory=list)
    retorna: str = ""
    excepciones: List[str] = field(default_factory=list)
    ejemplo: str = ""
    linea: int = 0
    archivo: str = ""


class GeneradorDocumentacion:
    """
    Generador de documentación para My Lenguaje
    
    Extrae docstrings y genera documentación en Markdown
    """
    
    def __init__(self):
        self.elementos: List[DocItem] = []
    
    def analizar_archivo(self, archivo: str):
        """Analiza un archivo .my y extrae documentación"""
        path = Path(archivo)
        if not path.exists():
            return
        
        with open(path, 'r', encoding='utf-8') as f:
            contenido = f.read()
        
        self._extraer_funciones(contenido, str(path))
        self._extraer_clases(contenido, str(path))
        self._extraer_modulo(contenido, str(path))
    
    def _extraer_docstring(self, texto: str, posicion: int) -> tuple[str, int]:
        """Extrae docstring de un elemento"""
        # Buscar docstring con """
        match = re.search(r'"""(.*?)"""', texto[posicion:posicion+500], re.DOTALL)
        if match:
            docstring = match.group(1).strip()
            return docstring, posicion + match.end()
        
        # Buscar docstring con '''
        match = re.search(r"'''(.*?)'''", texto[posicion:posicion+500], re.DOTALL)
        if match:
            docstring = match.group(1).strip()
            return docstring, posicion + match.end()
        
        return "", posicion
    
    def _parsear_docstring(self, docstring: str) -> dict:
        """Parsea un docstring estructurado"""
        resultado = {
            'descripcion': '',
            'args': [],
            'retorna': '',
            'excepciones': [],
            'ejemplo': ''
        }
        
        if not docstring:
            return resultado
        
        lineas = docstring.split('\n')
        seccion_actual = 'descripcion'
        
        for linea in lineas:
            linea = linea.strip()
            
            if linea.startswith('Args:'):
                seccion_actual = 'args'
            elif linea.startswith('Returns:'):
                seccion_actual = 'retorna'
            elif linea.startswith('Raises:'):
                seccion_actual = 'excepciones'
            elif linea.startswith('Example:'):
                seccion_actual = 'ejemplo'
            elif linea.startswith('>>>'):
                resultado['ejemplo'] += linea + '\n'
            elif seccion_actual == 'descripcion':
                resultado['descripcion'] += linea + ' '
            elif seccion_actual == 'args' and ':' in linea:
                nombre, desc = linea.split(':', 1)
                resultado['args'].append(f"{nombre.strip()}: {desc.strip()}")
            elif seccion_actual == 'retorna':
                resultado['retorna'] = linea
            elif seccion_actual == 'excepciones':
                resultado['excepciones'].append(linea)
        
        resultado['descripcion'] = resultado['descripcion'].strip()
        return resultado
    
    def _extraer_funciones(self, texto: str, archivo: str):
        """Extrae funciones del código"""
        patron = r'función\s+(\w+)\s*\(([^)]*)\)\s*(?:->\s*(\w+))?:'
        
        for match in re.finditer(patron, texto):
            nombre = match.group(1)
            params = match.group(2)
            tipo_retorno = match.group(3) or ""
            
            # Buscar docstring
            docstring, _ = self._extraer_docstring(texto, match.end())
            info = self._parsear_docstring(docstring)
            
            item = DocItem(
                nombre=nombre,
                tipo='funcion',
                descripcion=info['descripcion'],
                args=info['args'],
                retorna=info['retorna'] or tipo_retorno,
                excepciones=info['excepciones'],
                ejemplo=info['ejemplo'],
                linea=texto[:match.start()].count('\n') + 1,
                archivo=archivo
            )
            
            self.elementos.append(item)
    
    def _extraer_clases(self, texto: str, archivo: str):
        """Extrae clases del código"""
        patron = r'clase\s+(\w+)(?:\s*\(\s*(\w+)\s*\))?:'
        
        for match in re.finditer(patron, texto):
            nombre = match.group(1)
            padre = match.group(2) or ""
            
            # Buscar docstring
            docstring, _ = self._extraer_docstring(texto, match.end())
            info = self._parsear_docstring(docstring)
            
            item = DocItem(
                nombre=nombre,
                tipo='clase',
                descripcion=info['descripcion'],
                ejemplo=info['ejemplo'],
                linea=texto[:match.start()].count('\n') + 1,
                archivo=archivo
            )
            
            if padre:
                item.descripcion += f"\n\nHereda de: {padre}"
            
            self.elementos.append(item)
    
    def _extraer_modulo(self, texto: str, archivo: str):
        """Extrae documentación del módulo"""
        # Buscar docstring al inicio del archivo
        match = re.match(r'\s*"""(.*?)"""', texto, re.DOTALL)
        if match:
            docstring = match.group(1).strip()
            
            item = DocItem(
                nombre=Path(archivo).stem,
                tipo='modulo',
                descripcion=docstring,
                archivo=archivo,
                linea=1
            )
            
            self.elementos.insert(0, item)
    
    def generar_markdown(self, salida: str = "docs.md"):
        """Genera documentación en Markdown"""
        lineas = []
        lineas.append("# Documentación de My Lenguaje\n")
        lineas.append("Generada automáticamente\n")
        lineas.append("=" * 50)
        
        # Agrupar por tipo
        modulos = [e for e in self.elementos if e.tipo == 'modulo']
        clases = [e for e in self.elementos if e.tipo == 'clase']
        funciones = [e for e in self.elementos if e.tipo == 'funcion']
        
        # Módulo
        if modulos:
            lineas.append("\n## Módulo\n")
            for mod in modulos:
                lineas.append(f"\n### {mod.nombre}\n")
                lineas.append(f"{mod.descripcion}\n")
        
        # Clases
        if clases:
            lineas.append("\n## Clases\n")
            for clase in clases:
                lineas.append(f"\n### Clase `{clase.nombre}`\n")
                if clase.descripcion:
                    lineas.append(f"{clase.descripcion}\n")
        
        # Funciones
        if funciones:
            lineas.append("\n## Funciones\n")
            for func in funciones:
                lineas.append(f"\n### `{func.nombre}()`\n")
                if func.descripcion:
                    lineas.append(f"{func.descripcion}\n")
                
                if func.args:
                    lineas.append("\n**Parámetros:**")
                    for arg in func.args:
                        lineas.append(f"- {arg}")
                
                if func.retorna:
                    lineas.append(f"\n**Retorna:** {func.retorna}")
                
                if func.excepciones:
                    lineas.append("\n**Excepciones:**")
                    for exc in func.excepciones:
                        lineas.append(f"- {exc}")
                
                if func.ejemplo:
                    lineas.append("\n**Ejemplo:**\n```python")
                    lineas.append(func.ejemplo)
                    lineas.append("```\n")
        
        contenido = "\n".join(lineas)
        
        with open(salida, 'w', encoding='utf-8') as f:
            f.write(contenido)
        
        print(f"✓ Documentación generada: {salida}")
        return contenido


def generar_documentacion(archivos: List[str], salida: str = "docs.md"):
    """Genera documentación para múltiples archivos"""
    generador = GeneradorDocumentacion()
    
    for archivo in archivos:
        generador.analizar_archivo(archivo)
    
    return generador.generar_markdown(salida)
