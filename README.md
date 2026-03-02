# My Lenguaje 🇪🇸

[![Versión](https://img.shields.io/badge/versión-0.6.5-blue.svg)](https://github.com/tu-usuario/my-lenguaje)
[![Python](https://img.shields.io/badge/python-3.8+-green.svg)](https://python.org)
[![Licencia](https://img.shields.io/badge/licencia-MIT-yellow.svg)](LICENSE)
[![Estado](https://img.shields.io/badge/estado-estable-brightgreen.svg)]()

**Un lenguaje de programación en español con características enterprise**

My Lenguaje es un lenguaje de programación que te permite escribir código en español. Se transpila a Python, por lo que tienes acceso a todo el ecosistema de Python mientras escribes en tu idioma nativo.

```my
# ¡Hola Mundo!
imprimir("¡Hola Mundo!")

# Variables con tipos opcionales
definir nombre: cadena = "Mundo"
definir edad: entero = 25

# Funciones
función saludar(nombre: cadena) -> cadena:
    retornar "Hola, " + nombre

imprimir(saludar(nombre))

# Condicionales en español
si edad >= 18:
    imprimir("Eres mayor de edad")
sino:
    imprimir("Eres menor de edad")

# Bucles
para i en rango(5):
    imprimir(f"Iteración: {i}")

# List comprehensions
cuadrados = [n * n para n en rango(10)]
imprimir(f"Cuadrados: {cuadrados}")
```

## ✨ Características

### 🎯 Core del Lenguaje

- ✅ **Sintaxis en español** - Todas las keywords en español
- ✅ **Tipos opcionales** - Sistema de tipos flexible
- ✅ **Programación orientada a objetos** - Clases, herencia
- ✅ **Funciones de primer nivel** - Lambdas, closures
- ✅ **Manejo de excepciones** - try/except/finally
- ✅ **Context managers** - `con ... como ...`
- ✅ **Async/await** - Programación asíncrona

### 🚀 Características Enterprise (Fase 6)

- ✅ **Optimizaciones automáticas** - Constant folding, dead code elimination
- ✅ **Debugger integrado** - Breakpoints, step-through
- ✅ **Profiler de rendimiento** - Análisis de tiempo de ejecución
- ✅ **Hot Reload** - Recarga automática al cambiar código
- ✅ **Sistema de testing** - Assertions en español
- ✅ **Generador de documentación** - Docs automáticas en Markdown
- ✅ **Logging integrado** - Sistema de logs profesional
- ✅ **Web framework** - Creación de APIs web
- ✅ **LSP Server** - Autocompletado en IDEs
- ✅ **Editor inteligente** - TUI con syntax highlighting y autocompletado
- ✅ **Sistema de paquetes** - Gestión de dependencias

## 📦 Instalación

### Requisitos

- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/tu-usuario/my-lenguaje.git
cd my-lenguaje

# Instalar dependencias
pip install -r requirements.txt

# Verificar instalación
python my.py version
```

### Instalación en Termux (Android)

```bash
# Instalar Python
pkg install python

# Clonar repositorio
git clone https://github.com/tu-usuario/my-lenguaje.git
cd my-lenguaje

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar
python my.py run ejemplos/hola.my
```

## 🚀 Uso Rápido

### 1. Crear tu primer programa

Crea un archivo `hola.my`:

```my
# Mi primer programa en My Lenguaje

función principal():
    imprimir("¡Hola desde My Lenguaje!")
    
    definir nombre: cadena = "Mundo"
    imprimir(f"Hola, {nombre}!")
    
    # Ejemplo con bucle
    para i en rango(5):
        imprimir(f"Contando: {i}")

principal()
```

### 2. Ejecutar el programa

```bash
python my.py run hola.my
```

**Salida:**
```
¡Hola desde My Lenguaje!
Hola, Mundo!
Contando: 0
Contando: 1
Contando: 2
Contando: 3
Contando: 4
```

### 3. Compilar a Python

```bash
python my.py compile hola.my -o hola.py
python hola.py  # Ejecutar Python generado
```

## 📖 Comandos Disponibles

| Comando | Descripción | Ejemplo |
|---------|-------------|---------|
| `run` | Ejecutar archivo .my | `python my.py run programa.my` |
| `compile` | Compilar a Python | `python my.py compile programa.my` |
| `debug` | Debugger interactivo | `python my.py debug programa.my` |
| `profile` | Analizar rendimiento | `python my.py profile programa.my` |
| `watch` | Hot reload | `python my.py watch programa.my` |
| `docs` | Generar documentación | `python my.py docs src/` |
| `test` | Ejecutar tests | `python my.py test tests/` |
| `edit` | Editor inteligente | `python my.py edit programa.my` |
| `init` | Crear proyecto | `python my.py init mi_proyecto` |
| `package` | Gestionar paquetes | `python my.py package new mi_lib` |
| `version` | Ver versión | `python my.py version` |
| `keywords` | Ver keywords | `python my.py keywords` |

## 📚 Documentación

### Sintaxis Básica

#### Variables
```my
# Sin tipo explícito
definir x = 5
definir nombre = "Juan"

# Con tipo explícito
definir edad: entero = 25
definir altura: flotante = 1.75
definir activo: booleano = verdadero
```

#### Funciones
```my
función suma(a: entero, b: entero) -> entero:
    retornar a + b

función saludar(nombre: cadena = "Mundo") -> cadena:
    retornar "Hola, " + nombre
```

#### Clases
```my
clase Persona:
    función __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad
    
    función presentarse(self):
        retornar f"Soy {self.nombre} y tengo {self.edad} años"
    
    función es_adulto(self):
        si self.edad >= 18:
            retornar verdadero
        sino:
            retornar falso
```

#### Manejo de Errores
```my
intentar:
    resultado = 10 / 0
excepto ErrorDivision:
    imprimir("No se puede dividir por cero")
finalmente:
    imprimir("Operación completada")
```

#### Context Managers
```my
con abrir("archivo.txt") como f:
    contenido = f.leer()
    imprimir(contenido)
```

#### Async/Await
```my
asíncrono función obtener_datos():
    datos = esperar conexion.leer()
    retornar datos

asíncrono función principal():
    resultados = esperar obtener_datos()
```

### Ejemplos Completos

Ver la carpeta [`ejemplos/`](ejemplos/) para más ejemplos:

- `hola.my` - Hola Mundo básico
- `mega_test.my` - Test completo de todas las características
- `fase4.my` - Ejemplo de características avanzadas

## 🛠️ Desarrollo

### Estructura del Proyecto

```
my-lenguaje/
├── my.py                      # CLI principal
├── core/                      # Núcleo del lenguaje
│   ├── __init__.py           # Módulo principal
│   ├── translator_v2.py      # Traductor base
│   ├── translator_fase4.py   # Características Fase 4
│   ├── optimizer.py          # Optimizador de código
│   ├── debugger.py           # Debugger
│   ├── profiler.py           # Profiler
│   ├── testing.py            # Framework de testing
│   ├── lsp.py                # Language Server
│   ├── editor.py             # Editor inteligente
│   ├── packagemanager.py     # Gestor de paquetes
│   ├── hotreload.py          # Hot Reload
│   ├── docs.py               # Generador de docs
│   ├── logging.py            # Logging
│   └── web.py                # Web framework
├── ejemplos/                  # Ejemplos de código
├── tests/                     # Tests del proyecto
├── requirements.txt           # Dependencias
├── README.md                  # Este archivo
├── CONTRIBUTING.md            # Guía de contribución
└── LICENSE                    # Licencia MIT
```

### Ejecutar Tests

```bash
# Ejecutar todos los tests
python -m unittest discover tests -v

# Ejecutar test específico
python -m unittest tests.test_translator -v
```

### Contribuir

¡Las contribuciones son bienvenidas! Lee [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

1. Fork el repositorio
2. Crea una rama (`git checkout -b feature/nueva-caracteristica`)
3. Commit tus cambios (`git commit -m 'Añadir nueva característica'`)
4. Push (`git push origin feature/nueva-caracteristica`)
5. Abre un Pull Request

## 📋 Roadmap

### ✅ Completado (Fase 6)

- [x] Traductor español → Python
- [x] Optimizaciones de código
- [x] Debugger integrado
- [x] Profiler de rendimiento
- [x] Sistema de testing
- [x] Hot Reload
- [x] Generador de documentación
- [x] Logging integrado
- [x] Web framework
- [x] LSP Server
- [x] Editor inteligente

### 🔄 En Progreso

- [ ] Soporte para bases de datos
- [ ] Sistema de plugins
- [ ] Compilación a WebAssembly
- [ ] IDE gráfico (My Studio)

### 📅 Futuro

- [ ] Machine Learning en español
- [ ] Framework GUI
- [ ] Package registry oficial

## 🤝 Comunidad

- 📧 Email: tu-email@ejemplo.com
- 💬 Discord: [Enlace al Discord]
- 🐦 Twitter: [@tu-usuario]
- 📝 Blog: [Enlace al blog]

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 🙏 Agradecimientos

- A la comunidad de Python por inspirar este proyecto
- A todos los contribuidores que hacen posible My Lenguaje

## 📊 Estadísticas

![Estrellas](https://img.shields.io/github/stars/tu-usuario/my-lenguaje?style=social)
![Forks](https://img.shields.io/github/forks/tu-usuario/my-lenguaje?style=social)
![Issues](https://img.shields.io/github/issues/tu-usuario/my-lenguaje)
![Pull Requests](https://img.shields.io/github/issues-pr/tu-usuario/my-lenguaje)

---

**¡Hecho con ❤️ en español!**
