#!/bin/bash

echo "🚀 Script para subir proyecto a GitHub"
echo "--------------------------------------"

# Verificar git (método mejorado para Termux)
GIT_PATH=$(which git 2>/dev/null)
if [ -n "$GIT_PATH" ] || [ -x "/data/data/com.termux/files/usr/bin/git" ]; then
    echo "✓ Git encontrado: ${GIT_PATH:-/data/data/com.termux/files/usr/bin/git}"
else
    echo "❌ Git no está instalado."
    echo "   Instala con: pkg install git"
    exit 1
fi

# Verificar si estamos en el directorio correcto
if [ ! -f "my.py" ] && [ ! -f "README.md" ]; then
    echo "⚠️  Advertencia: No parece estar en el directorio del proyecto"
    echo "   Asegúrate de estar en /data/data/com.termux/files/home/lenguaje"
    read -p "¿Continuar de todos modos? (s/n): " CONTINUAR
    if [ "$CONTINUAR" != "s" ] && [ "$CONTINUAR" != "S" ]; then
        exit 1
    fi
fi

# Pedir datos
echo ""
read -p "👤 Usuario de GitHub: " GITHUB_USER
read -p "📦 Nombre del repositorio: " REPO_NAME
read -p "📝 Mensaje del commit: " COMMIT_MSG
read -p "🌍 ¿Repositorio privado? (s/n): " PRIVADO

# Determinar visibilidad
if [ "$PRIVADO" = "s" ] || [ "$PRIVADO" == "S" ]; then
    VISIBILITY="--private"
else
    VISIBILITY="--public"
fi

# Inicializar git si no existe
if [ ! -d ".git" ]; then
    echo ""
    echo "📁 Inicializando repositorio Git..."
    git init
fi

# Configurar usuario de git si no está configurado
if [ -z "$(git config user.name 2>/dev/null)" ]; then
    echo ""
    read -p "✏️  Tu nombre para Git: " GIT_NAME
    read -p "✏️  Tu email para Git: " GIT_EMAIL
    git config user.name "$GIT_NAME"
    git config user.email "$GIT_EMAIL"
fi

# Agregar archivos
echo ""
echo "📌 Agregando archivos..."
git add .

# Verificar si hay cambios
if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  No hay cambios para commitear"
else
    # Commit
    echo "💾 Haciendo commit..."
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="feat: Initial commit - My Lenguaje v0.6.5"
    fi
    git commit -m "$COMMIT_MSG

Co-authored-by: Qwen-Coder <qwen-coder@alibabacloud.com>"
fi

# Cambiar rama a main
git branch -M main 2>/dev/null

# Crear repo en GitHub si gh está disponible
if command -v gh &> /dev/null; then
    echo ""
    echo "🌐 Creando repositorio en GitHub con gh..."
    gh repo create "$GITHUB_USER/$REPO_NAME" $VISIBILITY --source=. --remote=origin --push
else
    echo ""
    echo "⚠️  gh (GitHub CLI) no está instalado."
    echo "🔗 Creando remoto manualmente..."
    echo ""
    echo "Instrucciones:"
    echo "1. Ve a https://github.com/new"
    echo "2. Nombre del repositorio: $REPO_NAME"
    echo "3. Descripción: Un lenguaje de programación en español"
    echo "4. Público (recomendado)"
    echo "5. NO marcar 'Initialize with README'"
    echo "6. Click en 'Create repository'"
    echo ""
    read -p "¿Ya creaste el repositorio? (s/n): " CREADO
    
    if [ "$CREADO" = "s" ] || [ "$CREADO" == "S" ]; then
        git remote remove origin 2>/dev/null
        git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
        
        echo "📤 Subiendo a GitHub..."
        git push -u origin main
        
        echo ""
        echo "✅ ¡Proyecto subido con éxito!"
        echo "🌐 Tu repositorio: https://github.com/$GITHUB_USER/$REPO_NAME"
    else
        echo ""
        echo "⏹️  Operación cancelada."
        echo "   Cuando crees el repositorio, ejecuta:"
        echo "   git remote add origin https://github.com/$GITHUB_USER/$REPO_NAME.git"
        echo "   git push -u origin main"
        exit 1
    fi
fi

echo ""
echo "🎉 ¡Gracias por usar My Lenguaje!"
echo "   No olvides actualizar el README con tu usuario de GitHub"
