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
    """Ejecuta un archivo .my con aislamiento de argumentos"""
    input_file = Path(args.file)
    if not input_file.exists():
        print(f"Error: El archivo '{input_file}' no existe", file=sys.stderr)
        sys.exit(1)

    try:
        traductor = Traductor()
        
        # Leer y traducir código
        with open(input_file, 'r', encoding='utf-8') as f:
            codigo_my = f.read()
        
        codigo_python = traductor.traducir(codigo_my)
        
        # Aislar sys.argv para el script del usuario
        argv_original = sys.argv
        sys.argv = [str(input_file)] + (args.user_args if hasattr(args, 'user_args') else [])
        
        # Ejecutar en namespace separado
        namespace = {
            '__name__': '__main__',
            '__file__': str(input_file)
        }
        
        try:
            exec(codigo_python, namespace)
        finally:
            # Restaurar argv original
            sys.argv = argv_original
            
    except TranslatorError as e:
        print(f"❌ Error de traducción: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error en ejecución: {e}", file=sys.stderr)
        sys.exit(1)


def compile_command(args):
    """Compila un archivo .my con validación AST"""
    import ast as py_ast
    
    input_file = Path(args.file)
    if not input_file.exists():
        print(f"Error: El archivo '{input_file}' no existe", file=sys.stderr)
        sys.exit(1)

    output_file = args.output or input_file.with_suffix('.py')
    optimizar = not args.no_optimize

    try:
        traductor = Traductor()
        codigo = traductor.traducir_archivo(str(input_file), str(output_file), optimizar=optimizar)

        # VALIDACIÓN AST: Verificar que el Python generado es válido
        try:
            py_ast.parse(codigo)
        except SyntaxError as e:
            print(f"❌ Error de validación AST:", file=sys.stderr)
            print(f"   El código Python generado tiene errores de sintaxis", file=sys.stderr)
            print(f"   Línea {e.lineno}: {e.text.strip() if e.text else ''}", file=sys.stderr)
            print(f"   {e.msg}", file=sys.stderr)
            sys.exit(1)

        print(f"✓ Archivo compilado:")
        print(f"  Entrada:  {input_file}")
        print(f"  Salida:   {output_file}")
        print(f"  Líneas:   {len(codigo.splitlines())}")
        print(f"  Validación AST: ✓")

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
    print("My Lenguaje v0.8.0 - Fase 8: Ultimate Edition")
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
    print("\n✨ Fase 7 - IA/ML/NLP:")
    print("  ✓ Redes neuronales artificiales")
    print("  ✓ Machine Learning (regresión, clasificación, clustering)")
    print("  ✓ NLP en español (análisis de sentimiento, chatbot)")
    print("  ✓ Agentes de IA con Q-learning")
    print("\n🚀 Fase 8 - Advanced Features:")
    print("  ✓ ORM y Base de Datos (SQLite/MySQL/PostgreSQL)")
    print("  ✓ Sistema de Plugins")
    print("  ✓ Computación Distribuida")
    print("  ✓ Sistema de Caché (LRU/LFU/TTL)")
    print("  ✓ Depuración Avanzada")
    print("  ✓ Análisis de Memoria")


def keywords_command(args):
    """Muestra keywords sincronizadas con el traductor"""
    from core.translator_v2 import TraductorMejorado
    
    print("Palabras clave de My Lenguaje:")
    print("=" * 50)
    print("(Sincronizado con el traductor)")
    print()

    # Obtener keywords directamente del traductor
    traductor = TraductorMejorado()
    keyword_map = traductor.KEYWORD_MAP
    
    categorias = {
        'Declaraciones': ['definir', 'clase', 'función', 'retornar'],
        'Condicionales': ['si', 'sino si', 'sino'],
        'Bucles': ['para', 'en', 'mientras', 'rango'],
        'Excepciones': ['intentar', 'excepto', 'finalmente'],
        'Importaciones': ['importar', 'como'],
        'Lógicos': ['y', 'o', 'no', 'verdadero', 'falso', 'nulo'],
        'Builtins': ['imprimir', 'entrada', 'entero', 'flotante', 'cadena', 'lista', 'diccionario', 'longitud'],
        'Tipos': ['entero', 'flotante', 'cadena', 'booleano', 'lista', 'dict'],
        'Control Flujo': ['parar', 'continuar', 'pasar'],
        'Fase 4-6': ['con', 'asíncrono', 'esperar', '@decorador'],
        'Fase 7-8': ['red_neuronal', 'entrenar', 'cache', 'orm']
    }

    # Construir traducción desde el traductor + hardcoded
    traduccion = dict(keyword_map)
    traduccion.update({
        'definir': '(variable)',
        'y': 'and (contextual)',
        'o': 'or (contextual)',
        'no': 'not (contextual)',
        '@decorador': '@decorator'
    })

    for cat, keywords in categorias.items():
        print(f"\n{cat}:")
        for kw in keywords:
            py = traduccion.get(kw, kw)
            # Marcar keywords nuevas
            marker = " ✨" if kw in ['parar', 'continuar', 'pasar'] else ""
            print(f"  {kw:15} → {py}{marker}")
    
    print("\n" + "=" * 50)
    print("Nota: 'y', 'o', 'no' se traducen contextualmente")
    print("      (solo como operadores, no como variables)")


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
    imprimir("¡Hola desde My Lenguaje v0.7.0!")

    definir nombre: cadena = "Mundo"
    imprimir("Hola, " + nombre)

principal()
''')

    # README
    (project_dir / 'README.md').write_text(f'''# {args.name}

Proyecto creado con My Lenguaje v0.7.0

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


def ai_chat_command(args):
    """Inicia chatbot interactivo"""
    from core.nlp import ChatbotBasico
    
    print("🤖 My Chatbot - Fase 7 AI/ML")
    print("=" * 50)
    print("Escribe 'salir' para terminar\n")
    
    chatbot = ChatbotBasico()
    chatbot.conversar()


def ai_sentimiento_command(args):
    """Analiza sentimiento de un texto"""
    from core.nlp import AnalizadorSentimiento
    
    texto = args.texto if hasattr(args, 'texto') and args.texto else None
    
    if not texto:
        print("Ingresa el texto a analizar:")
        texto = input("> ")
    
    analizador = AnalizadorSentimiento()
    resultado = analizador.analizar(texto)
    
    print("\n📊 Análisis de Sentimiento")
    print("=" * 50)
    print(f"Texto: \"{texto[:50]}...\"")
    print(f"Sentimiento: {resultado['sentimiento'].upper()}")
    print(f"Puntuación: {resultado['puntuacion']:.4f}")
    print(f"Palabras positivas: {resultado['positivas']}")
    print(f"Palabras negativas: {resultado['negativas']}")
    print(f"Palabras neutrales: {resultado['neutrales']}")
    
    if resultado['palabras_clave']['positivas']:
        print(f"Positivas clave: {', '.join(resultado['palabras_clave']['positivas'][:5])}")
    if resultado['palabras_clave']['negativas']:
        print(f"Negativas clave: {', '.join(resultado['palabras_clave']['negativas'][:5])}")


def ai_demo_command(args):
    """Ejecuta demo de IA/ML"""
    from core.ai import RedNeuronal, ClasificadorIA
    from core.ml import (
        RegresionLineal, KMeans, KNN, ArbolDecision,
        evaluar_precision, dividir_datos
    )
    from core.nlp import AnalizadorSentimiento, tokenizar
    import random
    
    print("🧪 Demo de IA/ML - Fase 7")
    print("=" * 50)
    
    # Demo 1: Red Neuronal (XOR)
    print("\n1️⃣ Red Neuronal - Problema XOR")
    print("-" * 50)
    
    red = RedNeuronal([2, 4, 1], tasa_aprendizaje=0.1)
    
    datos_xor = [[0, 0], [0, 1], [1, 0], [1, 1]]
    salidas_xor = [[0], [1], [1], [0]]
    
    print("Entrenando red neuronal...")
    red.entrenar(datos_xor, salidas_xor, epocas=1000, verbose=False)
    
    print("\nResultados:")
    for entrada, salida_esperada in zip(datos_xor, salidas_xor):
        prediccion = red.predecir(entrada)
        print(f"  {entrada[0]} XOR {entrada[1]} = {prediccion[0]:.4f} (esperado: {salida_esperada[0]})")
    
    # Demo 2: Clasificador
    print("\n2️⃣ Clasificador IA")
    print("-" * 50)
    
    clf = ClasificadorIA()
    
    # Datos de ejemplo: [altura, peso] -> categoria (0: pequeño, 1: mediano, 2: grande)
    datos = [
        [150, 50], [155, 52], [160, 55], [165, 60],
        [170, 65], [175, 70], [180, 75], [185, 80]
    ]
    etiquetas = [
        "pequeño", "pequeño", "pequeño", "mediano",
        "mediano", "grande", "grande", "grande"
    ]
    
    print("Entrenando clasificador...")
    clf.entrenar(datos, etiquetas, epocas=200)
    
    # Probar
    prueba = [[162, 54], [172, 67], [182, 78]]
    print("\nClasificaciones:")
    for p in prueba:
        categoria, confianza = clf.clasificar(p)
        print(f"  {p} -> {categoria} ({confianza:.2%} confianza)")
    
    # Demo 3: K-Means
    print("\n3️⃣ K-Means Clustering")
    print("-" * 50)
    
    kmeans = KMeans(k=3, iteraciones=50)
    datos_cluster = [[random.random() * 10, random.random() * 10] for _ in range(30)]
    
    etiquetas = kmeans.ajustar_predecir(datos_cluster)
    
    print(f"Centroides encontrados: {len(kmeans.centroides)}")
    for i, centroide in enumerate(kmeans.centroides):
        print(f"  Centroide {i}: [{centroide[0]:.2f}, {centroide[1]:.2f}]")
    
    # Demo 4: NLP
    print("\n4️⃣ NLP - Análisis de Sentimiento")
    print("-" * 50)
    
    analizador = AnalizadorSentimiento()
    
    textos_prueba = [
        "Me encanta este producto, es excelente",
        "Esto es terrible, muy malo",
        "Es regular, ni bueno ni malo"
    ]
    
    for texto in textos_prueba:
        resultado = analizador.analizar(texto)
        print(f"  \"{texto[:30]}...\" -> {resultado['sentimiento']}")
    
    # Demo 5: Tokenización
    print("\n5️⃣ NLP - Tokenización")
    print("-" * 50)
    
    texto = "El rápido zorro marrón salta sobre el perro perezoso."
    tokens = tokenizar(texto)
    print(f"  Texto: {texto}")
    print(f"  Tokens: {tokens}")
    
    print("\n" + "=" * 50)
    print("✅ Demo completada exitosamente")


def ai_keywords_command(args):
    """Muestra keywords de IA/ML en español"""
    print("🧠 Keywords de IA/ML - My Lenguaje Fase 7")
    print("=" * 50)
    
    categorias = {
        'Redes Neuronales': [
            ('red_neuronal()', 'Crea una red neuronal'),
            ('entrenar()', 'Entrena la red'),
            ('predecir()', 'Haz una predicción'),
            ('guardar_modelo()', 'Guarda el modelo'),
            ('cargar_modelo()', 'Carga un modelo'),
        ],
        'Machine Learning': [
            ('crear_regresion_lineal()', 'Regresión lineal'),
            ('crear_regresion_logistica()', 'Regresión logística'),
            ('crear_kmeans()', 'K-Means clustering'),
            ('crear_knn()', 'K-Nearest Neighbors'),
            ('crear_arbol()', 'Árbol de decisión'),
            ('crear_random_forest()', 'Random Forest'),
            ('evaluar_precision()', 'Evalúa precisión'),
            ('dividir_datos()', 'Divide train/test'),
        ],
        'NLP': [
            ('tokenizar()', 'Tokeniza texto'),
            ('stemmear()', 'Stemming de palabras'),
            ('analizar_sentimiento()', 'Analiza sentimiento'),
            ('extraer_palabras_clave()', 'Extrae keywords'),
            ('crear_chatbot()', 'Crea chatbot'),
            ('conversar()', 'Inicia chat'),
        ],
        'IA Agentes': [
            ('AgenteIA()', 'Crea agente'),
            ('elegir_accion()', 'Elige acción'),
            ('actualizar()', 'Actualiza Q-table'),
            ('aprender()', 'Aprende de episodios'),
        ]
    }
    
    for categoria, items in categorias.items():
        print(f"\n{categoria}:")
        for keyword, descripcion in items:
            print(f"  {keyword:<30} - {descripcion}")


def fase8_demo_command(args):
    """Demo de Fase 8 - Advanced Features"""
    print("🚀 Demo de Fase 8 - Advanced Features")
    print("=" * 60)
    
    # Demo 1: Caché
    print("\n1️⃣ Sistema de Caché")
    print("-" * 60)
    from core.cache import Caché, en_caché
    
    cache = Caché(capacidad=100, ttl=60)
    cache.establecer("usuario:1", {"nombre": "Juan", "edad": 30})
    usuario = cache.obtener("usuario:1")
    print(f"  Caché: {usuario}")
    print(f"  Estadísticas: {cache.obtener_estadisticas()}")
    
    # Demo 2: Base de Datos
    print("\n2️⃣ Base de Datos ORM")
    print("-" * 60)
    from core.database import ORM, Modelo, Campo
    import tempfile
    import os
    
    db_file = tempfile.mktemp(suffix=".db")
    orm = ORM(db_file)
    orm.conectar()
    
    # Crear tabla simple
    orm.db.ejecutar("""
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            email TEXT UNIQUE,
            edad INTEGER
        )
    """)
    
    # Insertar
    orm.db.ejecutar("INSERT INTO usuarios (nombre, email, edad) VALUES (?, ?, ?)",
                   ("Ana", "ana@test.com", 25))
    orm.db.ejecutar("INSERT INTO usuarios (nombre, email, edad) VALUES (?, ?, ?)",
                   ("Carlos", "carlos@test.com", 30))
    
    # Consultar
    resultados = orm.db.ejecutar("SELECT * FROM usuarios")
    print(f"  Usuarios en BD: {len(resultados)}")
    for r in resultados:
        print(f"    - {r['nombre']} ({r['email']})")
    
    orm.cerrar()
    os.unlink(db_file)
    
    # Demo 3: Distribuido
    print("\n3️⃣ Computación Distribuida")
    print("-" * 60)
    from core.distributed import Distribuidor
    
    def cuadrado(x):
        return x * x
    
    dist = Distribuidor(workers=2, tipo="thread")
    dist.iniciar()
    
    ids = dist.ejecutar_multiple(cuadrado, [(i,) for i in range(5)])
    
    resultados = []
    for id_tarea in ids:
        resultado = dist.obtener_resultado(id_tarea, timeout=5)
        resultados.append(resultado)
    
    print(f"  Cuadrados: {resultados}")
    print(f"  Estadísticas: {dist.obtener_estadisticas()}")
    
    dist.detener()
    
    # Demo 4: Plugins
    print("\n4️⃣ Sistema de Plugins")
    print("-" * 60)
    from core.plugins import GestorPlugins
    
    gestor = GestorPlugins()
    stats = gestor.obtener_estadisticas()
    print(f"  Plugins cargados: {stats['total_plugins']}")
    print(f"  Hooks registrados: {stats['hooks_registrados']}")
    
    # Demo 5: Debug Avanzado
    print("\n5️⃣ Depuración Avanzada")
    print("-" * 60)
    from core.advanced_debug import DepuradorAvanzado, perfilar
    
    dep = DepuradorAvanzado()
    dep.agregar_breakpoint("test.py", 10)
    print(f"  Breakpoints: {dep.listar_breakpoints()}")
    print(f"  Estadísticas: {dep.obtener_estadisticas()}")
    
    print("\n" + "=" * 60)
    print("✅ Demo de Fase 8 completada exitosamente")


def fase8_cache_command(args):
    """Comandos de caché"""
    from core.cache import Caché
    
    cache = Caché(capacidad=1000, ttl=3600)
    
    if hasattr(args, 'accion') and args.accion == "stats":
        print("📊 Estadísticas de Caché")
        print("=" * 50)
        print(f"  Entradas: {cache.tamanio()}")
        print(f"  Capacidad: {cache.capacidad}")
        stats = cache.obtener_estadisticas()
        for k, v in stats.items():
            print(f"  {k}: {v}")
    else:
        print("💾 Sistema de Caché")
        print("=" * 50)
        print("Comandos:")
        print("  python my.py cache stats - Ver estadísticas")
        print("  python my.py cache test - Ejecutar test")


def main():
    parser = argparse.ArgumentParser(
        prog='my',
        description='My Lenguaje v0.8.0 - Ultimate Edition',
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

    # AI/ML commands (Fase 7)
    p = subparsers.add_parser('ai', help='Comandos de IA/ML')
    p.set_defaults(func=ai_demo_command)

    p = subparsers.add_parser('chat', help='Chatbot interactivo')
    p.set_defaults(func=ai_chat_command)

    p = subparsers.add_parser('sentimiento', help='Análisis de sentimiento')
    p.add_argument('texto', nargs='?', default=None)
    p.set_defaults(func=ai_sentimiento_command)

    p = subparsers.add_parser('ai-demo', help='Demo de IA/ML')
    p.set_defaults(func=ai_demo_command)

    p = subparsers.add_parser('ai-keywords', help='Keywords de IA/ML')
    p.set_defaults(func=ai_keywords_command)

    # Fase 8 commands
    p = subparsers.add_parser('fase8', help='Demo de Fase 8')
    p.set_defaults(func=fase8_demo_command)

    p = subparsers.add_parser('fase8-demo', help='Demo completa de Fase 8')
    p.set_defaults(func=fase8_demo_command)

    p = subparsers.add_parser('cache', help='Sistema de Caché')
    p.add_argument('accion', nargs='?', default='info')
    p.set_defaults(func=fase8_cache_command)

    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        sys.exit(0)
    
    args.func(args)


if __name__ == '__main__':
    main()
