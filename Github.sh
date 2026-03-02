#!/bin/bash

# My Lenguaje - Script para subir a GitHub
# Uso: sh Github.sh

echo "🚀 Script para subir proyecto a GitHub"
echo "--------------------------------------"

# Verificar git
if ! command -v git >/dev/null 2>&1; then
    echo "❌ Git no está instalado."
    echo "   Instala con: pkg install git"
    exit 1
fi

echo "✓ Git encontrado: $(which git)"

# Verificar directorio
if [ ! -f "my.py" ]; then
    echo "⚠️  No estás en el directorio del proyecto"
    echo "   Deberías estar en /data/data/com.termux/files/home/lenguaje"
    exit 1
fi

# Configuración de Git
if [ -z "$(git config user.name 2>/dev/null)" ]; then
    echo ""
    read -p "✏️  Tu nombre para Git: " GIT_NAME
    read -p "✏️  Tu email para Git: " GIT_EMAIL
    git config user.name "$GIT_NAME"
    git config user.email "$GIT_EMAIL"
    echo "✓ Configuración de Git guardada"
fi

# Inicializar si es necesario
if [ ! -d ".git" ]; then
    echo ""
    echo "📁 Inicializando repositorio..."
    git init
fi

# Pedir datos del commit
echo ""
read -p "📝 Mensaje del commit (o Enter para default): " COMMIT_MSG
if [ -z "$COMMIT_MSG" ]; then
    COMMIT_MSG="feat: Initial commit - My Lenguaje v0.6.5"
fi

# Agregar y commitear
echo ""
echo "📌 Agregando archivos..."
git add .

if git diff-index --quiet HEAD -- 2>/dev/null; then
    echo "⚠️  No hay cambios nuevos"
else
    echo "💾 Haciendo commit..."
    git commit -m "$COMMIT_MSG"
fi

# Asegurar rama main
git branch -M main 2>/dev/null

# Verificar remote
echo ""
if git remote -v | grep -q origin; then
    echo "✓ Remote 'origin' ya configurado"
    read -p "¿Cambiar remote? (s/n): " CAMBIAR_REMOTE
    if [ "$CAMBIAR_REMOTE" = "s" ] || [ "$CAMBIAR_REMOTE" = "S" ]; then
        read -p "👤 Usuario de GitHub: " GITHUB_USER
        read -p "📦 Nombre del repositorio: " REPO_NAME
        git remote remove origin 2>/dev/null
        git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
    fi
else
    read -p "👤 Usuario de GitHub: " GITHUB_USER
    read -p "📦 Nombre del repositorio: " REPO_NAME
    
    git remote remove origin 2>/dev/null
    git remote add origin "https://github.com/$GITHUB_USER/$REPO_NAME.git"
fi

# Mostrar URL del remote
REMOTE_URL=$(git remote get-url origin 2>/dev/null)
echo ""
echo "🔗 Remote: $REMOTE_URL"

# Intentar push
echo ""
echo "📤 Subiendo a GitHub..."

if git push -u origin main 2>&1; then
    echo ""
    echo "✅ ¡ÉXITO! Proyecto subido a GitHub"
    
    # Extraer URL para mostrar
    REPO_PATH=$(echo $REMOTE_URL | sed 's|.git$||' | sed 's|.*github.com/||')
    echo ""
    echo "🌐 Tu repositorio: https://github.com/$REPO_PATH"
    echo ""
    echo "📋 Próximos pasos:"
    echo "   1. Ve a tu repositorio en GitHub"
    echo "   2. Verifica que todos los archivos estén presentes"
    echo "   3. Actualiza el README con tu información"
    echo "   4. Comparte el enlace!"
else
    echo ""
    echo "❌ Error al subir"
    echo ""
    echo "Posibles soluciones:"
    echo ""
    echo "1. Si el error es de autenticación:"
    echo "   - Usa un Personal Access Token en lugar de password"
    echo "   - Crea uno en: https://github.com/settings/tokens"
    echo "   - Marca los scopes: repo, workflow"
    echo ""
    echo "2. Si el repositorio no existe:"
    echo "   - Créalo manualmente en: https://github.com/new"
    echo "   - Nombre: lenguaje-my (o el que elegiste)"
    echo "   - NO lo inicialices con README"
    echo "   - Luego ejecuta este script nuevamente"
    echo ""
    echo "3. Si el error es de workflow:"
    echo "   - El token necesita permiso 'workflow'"
    echo "   - Actualiza tu token en GitHub Settings"
    echo ""
    echo "Comandos manuales alternativos:"
    echo "   git remote -v                    # Ver remote actual"
    echo "   git remote remove origin         # Eliminar remote"
    echo "   git remote add origin URL        # Agregar nuevo remote"
    echo "   git push -u origin main          # Subir cambios"
fi

echo ""
echo "🎉 ¡Gracias por usar My Lenguaje!"
