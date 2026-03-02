"""
My Lenguaje - Sistema de Paquetes (Fase 6)
Gestor de paquetes y dependencias
"""

import os
import sys
import json
import subprocess
from pathlib import Path
from typing import Dict, List, Optional

# Intentar usar tomllib (Python 3.11+) o toml library
try:
    import tomllib
except ImportError:
    try:
        import toml as tomllib
    except ImportError:
        tomllib = None


class GestorPaquetes:
    """
    Sistema de paquetes para My Lenguaje
    
    Características:
    - Crear paquetes
    - Instalar dependencias
    - Publicar en PyPI
    - Gestión de versiones
    """
    
    def __init__(self, directorio: str = "."):
        self.directorio = Path(directorio)
        self.archivo_config = self.directorio / "my.toml"
    
    def crear_paquete(self, nombre: str, version: str = "0.1.0", autor: str = ""):
        """Crea un nuevo paquete"""
        estructura = {
            'proyecto': {
                'nombre': nombre,
                'version': version,
                'autor': autor,
                'descripcion': '',
                'licencia': 'MIT'
            },
            'dependencias': {},
            'dependencias_desarrollo': {}
        }
        
        # Crear my.toml
        with open(self.archivo_config, 'w') as f:
            self._escribir_toml(f, estructura)
        
        # Crear estructura de directorios
        src_dir = self.directorio / "src" / nombre.replace("-", "_")
        src_dir.mkdir(parents=True, exist_ok=True)
        
        # Crear __init__.my
        init_file = src_dir / "__init__.my"
        init_file.write_text(f'# {nombre} v{version}\n')
        
        # Crear tests
        tests_dir = self.directorio / "tests"
        tests_dir.mkdir(exist_ok=True)
        
        # Crear README
        readme = self.directorio / "README.md"
        readme.write_text(f"# {nombre}\n\nDescripción del paquete.\n")
        
        print(f"✓ Paquete '{nombre}' creado exitosamente")
        print(f"  Directorio: {self.directorio.absolute()}")
        print(f"  Versión: {version}")
    
    def instalar_dependencias(self):
        """Instala todas las dependencias del my.toml"""
        if not self.archivo_config.exists():
            print("Error: No se encontró my.toml")
            return
        
        config = self._leer_toml()
        dependencias = config.get('dependencias', {})
        
        if not dependencias:
            print("No hay dependencias para instalar")
            return
        
        print("Instalando dependencias...")
        
        for paquete, version in dependencias.items():
            print(f"  📦 {paquete} {version}")
            self._instalar_paquete_pypi(paquete, version)
        
        print("✓ Dependencias instaladas")
    
    def instalar(self, nombre_paquete: str, version: str = None):
        """Instala un paquete específico"""
        print(f"Instalando {nombre_paquete}...")
        self._instalar_paquete_pypi(nombre_paquete, version or "latest")
        
        # Agregar a my.toml
        config = self._leer_toml()
        if 'dependencias' not in config:
            config['dependencias'] = {}
        
        config['dependencias'][nombre_paquete] = version or ">=0.0.0"
        
        with open(self.archivo_config, 'w') as f:
            self._escribir_toml(f, config)
        
        print(f"✓ {nombre_paquete} instalado")
    
    def _instalar_paquete_pypi(self, nombre: str, version: str):
        """Instala un paquete desde PyPI"""
        try:
            spec = f"{nombre}=={version}" if version != "latest" else nombre
            subprocess.check_call([sys.executable, "-m", "pip", "install", spec, "-q"])
        except subprocess.CalledProcessError:
            print(f"  ⚠️  No se pudo instalar {nombre}")
    
    def construir(self):
        """Construye el paquete para distribución"""
        config = self._leer_toml()
        nombre = config.get('proyecto', {}).get('nombre', 'mi_paquete')
        
        print(f"Construyendo {nombre}...")
        setup_py = self._generar_setup_py(config)
        
        try:
            subprocess.check_call([sys.executable, "setup.py", "sdist", "bdist_wheel"])
            print(f"✓ Paquete construido en dist/")
        except subprocess.CalledProcessError:
            print("❌ Error al construir el paquete")
        finally:
            if Path("setup.py").exists():
                Path("setup.py").unlink()
    
    def publicar(self):
        """Publica el paquete en PyPI"""
        print("Publicando paquete en PyPI...")
        
        try:
            subprocess.check_call([sys.executable, "-m", "twine", "upload", "dist/*"])
            print("✓ Paquete publicado exitosamente")
        except subprocess.CalledProcessError:
            print("❌ Error al publicar")
    
    def lista(self):
        """Lista paquetes instalados"""
        print("Paquetes instalados:")
        print("=" * 50)
        
        try:
            result = subprocess.check_output([sys.executable, "-m", "pip", "list", "--format=json"])
            paquetes = json.loads(result)
            
            for pkg in paquetes:
                print(f"  {pkg['name']:<25} {pkg['version']}")
        except:
            print("No se pudo obtener la lista de paquetes")
    
    def _leer_toml(self) -> dict:
        """Lee el archivo my.toml usando biblioteca TOML real"""
        if not self.archivo_config.exists():
            return {'proyecto': {}, 'dependencias': {}}
        
        # Usar biblioteca TOML si está disponible
        if tomllib:
            try:
                with open(self.archivo_config, 'rb' if hasattr(tomllib, 'load') else 'r') as f:
                    if hasattr(tomllib, 'load'):
                        # tomllib (Python 3.11+) usa modo binario
                        return tomllib.load(f)
                    else:
                        # toml library usa modo texto
                        return tomllib.load(f)
            except Exception as e:
                import logging
                logging.error(f"Error leyendo TOML: {e}")
                # Fallback al parser manual
                return self._leer_toml_manual()
        else:
            # Fallback al parser manual si no hay biblioteca
            return self._leer_toml_manual()
    
    def _leer_toml_manual(self) -> dict:
        """Parser TOML manual (fallback)"""
        config = {'proyecto': {}, 'dependencias': {}, 'dependencias_desarrollo': {}}
        seccion_actual = None
        
        with open(self.archivo_config, 'r') as f:
            for linea in f:
                linea = linea.strip()
                if not linea or linea.startswith('#'):
                    continue
                
                if linea.startswith('[') and linea.endswith(']'):
                    seccion_actual = linea[1:-1]
                    if seccion_actual not in config:
                        config[seccion_actual] = {}
                    continue
                
                if '=' in linea and seccion_actual:
                    clave, valor = linea.split('=', 1)
                    valor = valor.strip().strip('"\'')
                    config[seccion_actual][clave.strip()] = valor
        
        return config
    
    def _escribir_toml(self, f, config: dict):
        """Escribe el archivo my.toml"""
        for seccion, valores in config.items():
            f.write(f"[{seccion}]\n")
            for clave, valor in valores.items():
                if isinstance(valor, dict):
                    for k, v in valor.items():
                        f.write(f'{k} = "{v}"\n')
                else:
                    f.write(f'{clave} = "{valor}"\n')
            f.write("\n")
    
    def _generar_setup_py(self, config: dict) -> str:
        """Genera setup.py para el paquete"""
        proyecto = config.get('proyecto', {})
        dependencias = config.get('dependencias', {})
        
        setup_code = f'''from setuptools import setup, find_packages

setup(
    name="{proyecto.get('nombre', 'mi_paquete')}",
    version="{proyecto.get('version', '0.1.0')}",
    author="{proyecto.get('autor', '')}",
    description="{proyecto.get('descripcion', '')}",
    license="{proyecto.get('licencia', 'MIT')}",
    packages=find_packages(where="src"),
    package_dir={{"": "src"}},
    install_requires={[f'"{k}{v}"' for k, v in dependencias.items()]},
    python_requires=">=3.8",
)
'''
        
        with open("setup.py", 'w') as f:
            f.write(setup_code)
        
        return setup_code


def crear_paquete(nombre: str, version: str = "0.1.0", autor: str = ""):
    """Crea un nuevo paquete"""
    gestor = GestorPaquetes()
    gestor.crear_paquete(nombre, version, autor)


def instalar(paquete: str, version: str = None):
    """Instala un paquete"""
    gestor = GestorPaquetes()
    gestor.instalar(paquete, version)


def instalar_dependencias():
    """Instala todas las dependencias"""
    gestor = GestorPaquetes()
    gestor.instalar_dependencias()
