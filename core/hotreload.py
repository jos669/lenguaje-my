"""
My Lenguaje - Hot Reload (Fase 6)
Recarga automática al cambiar archivos
"""

import os
import sys
import time
import hashlib
import threading
from pathlib import Path
from typing import Callable, Dict, List, Optional, Set


class HotReloader:
    """
    Hot Reload para My Lenguaje
    
    Monitorea cambios en archivos .my y recarga automáticamente
    """
    
    def __init__(self, archivo_principal: str, callback: Callable = None):
        self.archivo_principal = Path(archivo_principal)
        self.callback = callback
        self.hashes: Dict[str, str] = {}
        self.ejecutando = False
        self.hilo: Optional[threading.Thread] = None
    
    def _calcular_hash(self, archivo: Path) -> str:
        """Calcula hash del contenido del archivo"""
        try:
            with open(archivo, 'rb') as f:
                return hashlib.md5(f.read()).hexdigest()
        except:
            return ""
    
    def _escanear_archivos(self) -> Set[Path]:
        """Escanea todos los archivos .my relacionados - CON imports relativos resueltos"""
        archivos = {self.archivo_principal}
        directorio_base = self.archivo_principal.parent

        # Buscar imports
        try:
            with open(self.archivo_principal, 'r', encoding='utf-8') as f:
                for linea in f:
                    linea = linea.strip()
                    if linea.startswith('importar'):
                        partes = linea.split()
                        if len(partes) >= 2:
                            modulo = partes[1]
                            
                            # Resolver imports relativos (con puntos)
                            if modulo.startswith('.'):
                                # Import relativo
                                niveles = modulo.count('.')
                                modulo = modulo.lstrip('.')
                                # Navegar hacia arriba en el árbol de directorios
                                base = directorio_base
                                for _ in range(niveles - 1):
                                    base = base.parent
                                archivo_mod = base / (modulo.replace('.', '/') + '.my')
                            else:
                                # Import absoluto
                                archivo_mod = directorio_base / (modulo.replace('.', '/') + '.my')
                            
                            if archivo_mod.exists():
                                archivos.add(archivo_mod)
                            else:
                                # Intentar en directorio actual
                                archivo_mod = Path(modulo.replace('.', '/') + '.my')
                                if archivo_mod.exists():
                                    archivos.add(archivo_mod)
        except Exception as e:
            import logging
            logging.error(f"Error escaneando archivos: {e}")

        return archivos
    
    def _iniciar_monitoreo(self):
        """Inicia el monitoreo de archivos"""
        print("🔍 Hot Reload activado")
        print(f"  Monitoreando: {self.archivo_principal}")
        print("  Presiona Ctrl+C para detener\n")
        
        # Hash inicial
        archivos = self._escanear_archivos()
        for archivo in archivos:
            self.hashes[str(archivo)] = self._calcular_hash(archivo)
        
        while self.ejecutando:
            time.sleep(1)
            
            # Verificar cambios
            archivos_actuales = self._escanear_archivos()
            
            # Detectar archivos nuevos o eliminados
            if archivos_actuales != set(self.hashes.keys()):
                self._recargar("Cambios detectados")
                continue
            
            # Detectar modificaciones
            for archivo_str, hash_original in self.hashes.items():
                archivo = Path(archivo_str)
                if archivo.exists():
                    hash_actual = self._calcular_hash(archivo)
                    if hash_actual != hash_original:
                        self._recargar(f"Modificado: {archivo}")
                        break
    
    def _recargar(self, razon: str):
        """Recarga el código"""
        print(f"\n🔄 {razón}")
        print("  Recargando...\n")
        
        # Actualizar hashes
        archivos = self._escanear_archivos()
        self.hashes = {}
        for archivo in archivos:
            self.hashes[str(archivo)] = self._calcular_hash(archivo)
        
        # Ejecutar callback
        if self.callback:
            self.callback()
    
    def ejecutar(self):
        """Ejecuta con hot reload"""
        self.ejecutando = True
        
        # Ejecutar inicial
        if self.callback:
            self.callback()
        
        # Iniciar monitoreo en hilo separado
        self.hilo = threading.Thread(target=self._iniciar_monitoreo, daemon=True)
        self.hilo.start()
        
        # Mantener ejecutando
        try:
            while self.ejecutando:
                time.sleep(0.1)
        except KeyboardInterrupt:
            self.detener()
    
    def detener(self):
        """Detiene el hot reload"""
        self.ejecutando = False
        print("\n⏹️  Hot Reload detenido")


def ejecutar_con_hot_reload(archivo: str, contexto: dict = None):
    """Ejecuta un archivo con hot reload"""
    from core import Traductor
    
    traductor = Traductor()
    
    def ejecutar():
        with open(archivo, 'r', encoding='utf-8') as f:
            codigo = f.read()
        traductor.ejecutar(codigo, contexto)
    
    reloader = HotReloader(archivo, callback=ejecutar)
    reloader.ejecutar()
