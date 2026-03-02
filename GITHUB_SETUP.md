# 📤 Guía para Subir a GitHub

## Archivos Creados para GitHub

El proyecto ya tiene todos los archivos necesarios:

```
my-lenguaje/
├── .github/
│   ├── ISSUE_TEMPLATE/
│   │   ├── bug_report.md       # Plantilla para reportar bugs
│   │   └── feature_request.md  # Plantilla para features
│   └── workflows/
│       └── tests.yml           # CI/CD con GitHub Actions
├── .gitignore                  # Archivos a ignorar
├── README.md                   # Documentación principal
├── CONTRIBUTING.md             # Guía de contribución
├── LICENSE                     # Licencia MIT
├── requirements.txt            # Dependencias
├── setup.py                    # Instalación como paquete
└── ... (resto del código)
```

## 📋 Pasos para Subir a GitHub

### 1. Inicializar Repositorio Git

```bash
cd /data/data/com.termux/files/home/lenguaje

# Inicializar repositorio
git init

# Añadir todos los archivos
git add .

# Primer commit
git commit -m "feat: Initial commit - My Lenguaje v0.6.5"
```

### 2. Crear Repositorio en GitHub

1. Ve a https://github.com/new
2. Nombre del repositorio: `my-lenguaje`
3. Descripción: "Un lenguaje de programación en español con características enterprise"
4. Público (recomendado para open source)
5. **NO** marques "Initialize this repository with a README"
6. Click en "Create repository"

### 3. Conectar con GitHub

```bash
# Añadir remote (reemplaza TU-USUARIO con tu usuario de GitHub)
git remote add origin https://github.com/TU-USUARIO/my-lenguaje.git

# Verificar remote
git remote -v

# Hacer push
git branch -M main
git push -u origin main
```

### 4. Verificar en GitHub

1. Ve a tu repositorio en GitHub
2. Verifica que todos los archivos estén presentes
3. El README debería mostrarse automáticamente

## 🔄 Comandos Útiles de Git

### Trabajo Diario

```bash
# Ver estado
git status

# Añadir cambios
git add .

# Hacer commit
git commit -m "feat: descripción del cambio"

# Hacer push
git push origin main
```

### Actualizar desde GitHub

```bash
# Pull de cambios
git pull origin main
```

### Crear Nueva Rama

```bash
# Crear y cambiar a nueva rama
git checkout -b feature/nueva-caracteristica

# Hacer cambios y commit
git add .
git commit -m "feat: nueva característica"

# Push de la rama
git push -u origin feature/nueva-caracteristica
```

## 🏷️ Tags y Releases

### Crear Tag

```bash
# Crear tag
git tag -a v0.6.5 -m "Versión 0.6.5 - Fase 6 Completa"

# Push del tag
git push origin --tags
```

### Crear Release en GitHub

1. Ve a https://github.com/TU-USUARIO/my-lenguaje/releases
2. Click en "Draft a new release"
3. Selecciona el tag (v0.6.5)
4. Escribe descripción del release
5. Click en "Publish release"

## 📊 Configurar CI/CD

El archivo `.github/workflows/tests.yml` ya está configurado para:

- Ejecutar tests automáticamente en cada push
- Probar en múltiples versiones de Python
- Ejecutar tests en pull requests

## 📝 Buenas Prácticas

### Commits

Usa [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: nueva característica
fix: corrección de bug
docs: cambios en documentación
test: añadir tests
refactor: refactorización
chore: tareas de mantenimiento
```

## 🚀 Después de Subir

### 1. Compartir en Redes

```
🎉 ¡Acabo de lanzar My Lenguaje v0.6.5!

Un lenguaje de programación en español con:
✨ Syntax en español
🔧 Debugger integrado
⚡ Hot Reload
📝 Editor inteligente
🧪 Testing framework

¡Pruébalo! 👇
https://github.com/TU-USUARIO/my-lenguaje

#opensource #programming #python #spanish
```

### 2. Publicar en Foros

- Reddit: r/programming, r/learnprogramming
- Hacker News
- LinkedIn
- Twitter

---

**¡Listo para compartir tu proyecto con el mundo! 🌍**
