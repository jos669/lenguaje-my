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
        """Escanea todos los archivos .my relacionados"""
        archivos = {self.archivo_principal}
        
        # Buscar imports
        try:
            with open(self.archivo_principal, 'r', encoding='utf-8') as f:
                for linea in f:
                    if linea.strip().startswith('importar'):
                        partes = linea.strip().split()
                        if len(partes) >= 2:
                            modulo = partes[1].replace('.', '/')
                            archivo_mod = Path(modulo + '.my')
                            if archivo_mod.exists():
                                archivos.add(archivo_mod)
        except:
            pass
        
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
