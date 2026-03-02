#!/usr/bin/env python3
"""
My Lenguaje - CLI Principal (Fase 6)
Interfaz completa con todas las características enterprise
"""

import sys
import os
import argparse
import json
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from core import Traductor, TranslatorError
from core.debugger import Debugger
from core.profiler import Profiler
from core.testing import Tester
from core.lsp import LSPServer, iniciar_lsp
from core.packagemanager import GestorPaquetes
from core.hotreload import ejecutar_con_hot_reload
from core.docs import GeneradorDocumentacion, generar_documentacion
from core.logging import configurar_logging
from core.editor import editar_archivo


def run_command(args):
    """Ejecuta un archivo .my"""
    input_file = Path(args.file)
    if not input_file.exists():
        print(f"Error: El archivo '{input_file}' no existe", file=sys.stderr)
        sys.exit(1)
    
    try:
        traductor = Traductor()
        traductor.ejecutar_archivo(str(input_file))
    except TranslatorError as e:
        print(f"❌ Error de traducción: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error en ejecución: {e}", file=sys.stderr)
        sys.exit(1)


def compile_command(args):
    """Compila un archivo .my"""
    input_file = Path(args.file)
    if not input_file.exists():
        print(f"Error: El archivo '{input_file}' no existe", file=sys.stderr)
        sys.exit(1)
    
    output_file = args.output or input_file.with_suffix('.py')
    optimizar = not args.no_optimize
    
    try:
        traductor = Traductor()
        codigo = traductor.traducir_archivo(str(input_file), str(output_file), optimizar=optimizar)
        
        print(f"✓ Archivo compilado:")
        print(f"  Entrada:  {input_file}")
        print(f"  Salida:   {output_file}")
        print(f"  Líneas:   {len(codigo.splitlines())}")
        
        if optimizar:
            reporte = traductor.optimizador.get_reporte()
            if reporte['cantidad'] > 0:
                print(f"  Optimizaciones: {', '.join(reporte['optimizaciones'])}")
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def debug_command(args):
    """Ejecuta con debugger"""
    input_file = Path(args.file)
    if not input_file.exists():
        print(f"Error: El archivo no existe", file=sys.stderr)
        sys.exit(1)
    
    try:
        traductor = Traductor()
        codigo = input_file.read_text(encoding='utf-8')
        codigo_python = traductor.traducir(codigo, optimizar=False)
        
        print("🔍 Debugger de My Lenguaje")
        print("Comandos: n, s, c, q, p <var>, l, w, b <línea>, h\n")
        
        traductor.debug(codigo_python)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def profile_command(args):
    """Profilea ejecución"""
    input_file = Path(args.file)
    if not input_file.exists():
        print(f"Error: El archivo no existe", file=sys.stderr)
        sys.exit(1)
    
    try:
        traductor = Traductor()
        codigo = input_file.read_text(encoding='utf-8')
        codigo_python = traductor.traducir(codigo, optimizar=False)
        reporte = traductor.profilear(codigo_python)
        print(reporte)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def watch_command(args):
    """Ejecuta con hot reload"""
    input_file = Path(args.file)
    if not input_file.exists():
        print(f"Error: El archivo no existe", file=sys.stderr)
        sys.exit(1)
    
    print("🔥 Hot Reload activado")
    print(f"  Vigilando: {input_file}\n")
    
    try:
        ejecutar_con_hot_reload(str(input_file))
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def docs_command(args):
    """Genera documentación"""
    archivos = args.files if args.files else ['src/**/*.my']
    salida = args.output or 'docs.md'
    
    print(f"📚 Generando documentación...")
    
    try:
        from glob import glob
        archivos_my = []
        for patron in archivos:
            archivos_my.extend(glob(patron, recursive=True))
        
        if not archivos_my:
            print("No se encontraron archivos .my")
            sys.exit(1)
        
        generar_documentacion(archivos_my, salida)
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def package_command(args):
    """Gestiona paquetes"""
    accion = args.accion
    gestor = GestorPaquetes()
    
    if accion == 'new':
        gestor.crear_paquete(args.nombre, args.version, args.autor)
    elif accion == 'install':
        if args.nombre:
            gestor.instalar(args.nombre, args.version)
        else:
            gestor.instalar_dependencias()
    elif accion == 'build':
        gestor.construir()
    elif accion == 'publish':
        gestor.publicar()
    elif accion == 'list':
        gestor.lista()


def lsp_command(args):
    """Inicia servidor LSP"""
    print("🖥️  Iniciando LSP Server...")
    print("   Para VS Code, agrega al settings.json:")
    print('   "my-lenguaje.lsp.port": 8765\n')
    
    try:
        iniciar_lsp()
    except Exception as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        sys.exit(1)


def test_command(args):
    """Ejecuta tests"""
    test_dir = Path(args.directory or 'tests')
    
    if not test_dir.exists():
        print(f"Error: El directorio '{test_dir}' no existe", file=sys.stderr)
        sys.exit(1)
    
    print("🧪 Sistema de Testing")
    print("=" * 50)
    
    from glob import glob
    test_files = glob(str(test_dir / "*.my"), recursive=True)
    
    if not test_files:
        print("No se encontraron tests .my")
        return
    
    tester = Tester()
    tester.crear_suite("Tests")
    
    for test_file in test_files:
        try:
            traductor = Traductor()
            codigo = Path(test_file).read_text(encoding='utf-8')
            codigo_python = traductor.traducir(codigo, optimizar=False)
            contexto = {'__name__': '__test__'}
            exec(codigo_python, contexto)
            print(f"  ✓ {Path(test_file).name}")
        except Exception as e:
            print(f"  ✗ {Path(test_file).name}: {e}")
    
    print("\n" + tester.get_reporte())


def version_command(args):
    """Muestra versión"""
    print("My Lenguaje v0.6.0 - Fase 6: Enterprise Edition")
    print("\nCaracterísticas:")
    print("  ✓ Traductor mejorado sin bugs")
    print("  ✓ Optimizaciones de código")
    print("  ✓ Debugger integrado")
    print("  ✓ Profiler de rendimiento")
    print("  ✓ Sistema de testing")
    print("  ✓ LSP Server (autocompletado)")
    print("  ✓ Hot Reload")
    print("  ✓ Sistema de paquetes")
    print("  ✓ Generador de documentación")
    print("  ✓ Logging integrado")
    print("  ✓ Web framework")
    print("  ✓ REPL interactivo")


def keywords_command(args):
    """Muestra keywords"""
    print("Palabras clave de My Lenguaje:")
    print("=" * 50)
    
    categorias = {
        'Declaraciones': ['definir', 'clase', 'función', 'retornar'],
        'Condicionales': ['si', 'sino si', 'sino'],
        'Bucles': ['para', 'en', 'mientras', 'rango'],
        'Excepciones': ['intentar', 'excepto', 'finalmente'],
        'Importaciones': ['importar', 'como'],
        'Lógicos': ['y', 'o', 'no', 'verdadero', 'falso', 'nulo'],
        'Builtins': ['imprimir', 'entrada', 'entero', 'flotante', 'cadena', 'lista', 'diccionario', 'longitud'],
        'Tipos': ['entero', 'flotante', 'cadena', 'booleano', 'lista', 'dict'],
        'Fase 4-6': ['con', 'asíncrono', 'esperar', '@decorador']
    }
    
    traduccion = {
        'definir': '(variable)', 'clase': 'class', 'función': 'def', 'retornar': 'return',
        'si': 'if', 'sino si': 'elif', 'sino': 'else',
        'para': 'for', 'en': 'in', 'mientras': 'while', 'rango': 'range',
        'intentar': 'try', 'excepto': 'except', 'finalmente': 'finally',
        'importar': 'import', 'como': 'as',
        'y': 'and', 'o': 'or', 'no': 'not',
        'verdadero': 'True', 'falso': 'False', 'nulo': 'None',
        'imprimir': 'print', 'entrada': 'input', 'entero': 'int',
        'flotante': 'float', 'cadena': 'str', 'lista': 'list',
        'diccionario': 'dict', 'longitud': 'len',
        'con': 'with', 'asíncrono': 'async', 'esperar': 'await'
    }
    
    for cat, keywords in categorias.items():
        print(f"\n{cat}:")
        for kw in keywords:
            py = traduccion.get(kw, kw)
            print(f"  {kw:15} → {py}")


def init_command(args):
    """Inicializa proyecto"""
    from shutil import copytree
    
    project_dir = Path(args.name)
    if project_dir.exists():
        print(f"Error: El directorio ya existe", file=sys.stderr)
        sys.exit(1)
    
    project_dir.mkdir()
    (project_dir / 'src').mkdir()
    (project_dir / 'tests').mkdir()
    
    # my.toml
    (project_dir / 'my.toml').write_text(f'''[proyecto]
nombre = "{args.name}"
version = "0.1.0"
autor = ""
descripcion = ""
licencia = "MIT"

[dependencias]

[dependencias_desarrollo]
''')
    
    # principal.my
    (project_dir / 'src' / 'principal.my').write_text('''# My Lenguaje - Proyecto Nuevo

función principal():
    imprimir("¡Hola desde My Lenguaje v0.6.0!")
    
    definir nombre: cadena = "Mundo"
    imprimir("Hola, " + nombre)

principal()
''')
    
    # README
    (project_dir / 'README.md').write_text(f'''# {args.name}

Proyecto creado con My Lenguaje v0.6.0

## Comandos

```bash
# Ejecutar
python ../my.py run src/principal.my

# Compilar
python ../my.py compile src/principal.my

# Hot reload
python ../my.py watch src/principal.my

# Tests
python ../my.py test tests/

# Documentación
python ../my.py docs src/principal.my
```
''')
    
    print(f"✓ Proyecto '{args.name}' creado")
    print(f"  cd {args.name}")
    print(f"  python ../my.py run src/principal.my")




def edit_command(args):
    from core.editor import editar_archivo
    archivo = args.file if hasattr(args, 'file') else None
    print("🎨 My Editor - Editor Inteligente")
    print("=" * 50)
    print("Atajos: Ctrl+S:Guardar  Ctrl+E:Ejecutar  Ctrl+Q:Salir  Tab:Autocompletar")
    print("=" * 50)
    try:
        editar_archivo(archivo)
    except KeyboardInterrupt:
        print("\nEditor cerrado")

def main():
    parser = argparse.ArgumentParser(
        prog='my',
        description='My Lenguaje v0.6.0 - Enterprise Edition',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Comandos')
    
    # run
    p = subparsers.add_parser('run', help='Ejecutar .my')
    p.add_argument('file')
    p.set_defaults(func=run_command)
    
    # compile
    p = subparsers.add_parser('compile', help='Compilar .my')
    p.add_argument('file')
    p.add_argument('-o', '--output')
    p.add_argument('--no-optimize', action='store_true')
    p.set_defaults(func=compile_command)
    
    # debug
    p = subparsers.add_parser('debug', help='Debugger')
    p.add_argument('file')
    p.set_defaults(func=debug_command)
    
    # profile
    p = subparsers.add_parser('profile', help='Profiler')
    p.add_argument('file')
    p.set_defaults(func=profile_command)
    
    # watch (hot reload)
    p = subparsers.add_parser('watch', help='Hot Reload')
    p.add_argument('file')
    p.set_defaults(func=watch_command)
    
    # docs
    p = subparsers.add_parser('docs', help='Documentación')
    p.add_argument('files', nargs='*')
    p.add_argument('-o', '--output', default='docs.md')
    p.set_defaults(func=docs_command)
    
    # package
    p = subparsers.add_parser('package', help='Paquetes')
    p.add_argument('accion', choices=['new', 'install', 'build', 'publish', 'list'])
    p.add_argument('nombre', nargs='?')
    p.add_argument('-v', '--version')
    p.add_argument('-a', '--autor')
    p.set_defaults(func=package_command)
    
    # lsp
    p = subparsers.add_parser('lsp', help='LSP Server')
    p.set_defaults(func=lsp_command)
    
    # test
    p = subparsers.add_parser('test', help='Tests')
    p.add_argument('directory', nargs='?', default='tests')
    p.set_defaults(func=test_command)
    
    # init
    p = subparsers.add_parser('init', help='Nuevo proyecto')
    p.add_argument('name')
    p.set_defaults(func=init_command)
    
    # version
    p = subparsers.add_parser('version', help='Versión')
    p.set_defaults(func=version_command)
    
    # keywords
    p = subparsers.add_parser('keywords', help='Keywords')
    p.set_defaults(func=keywords_command)

    # edit
    p = subparsers.add_parser('edit', help='Editor Inteligente')
    p.add_argument('file', nargs='?')
    p.set_defaults(func=edit_command)

    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == '__main__':
    main()
