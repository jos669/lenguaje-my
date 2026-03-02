# Contribuir a My Lenguaje 🤝

¡Gracias por tu interés en contribuir a My Lenguaje! Este documento te guiará en cómo contribuir al proyecto.

## 📋 Tabla de Contenidos

- [Código de Conducta](#código-de-conducta)
- [Cómo Contribuir](#cómo-contribuir)
- [Configuración del Entorno](#configuración-del-entorno)
- [Estándares de Código](#estándares-de-código)
- [Proceso de Pull Request](#proceso-de-pull-request)
- [Reportar Bugs](#reportar-bugs)
- [Solicitar Características](#solicitar-características)

## Código de Conducta

- Sé respetuoso con todos los contribuidores
- Acepta críticas constructivas
- Enfócate en lo que es mejor para la comunidad
- Muestra empatía hacia otros miembros

## Cómo Contribuir

### Formas de Contribuir

1. **Reportar bugs** - Abre un issue describiendo el problema
2. **Solicitar características** - Sugiere nuevas ideas
3. **Corregir bugs** - Envía un PR con la corrección
4. **Añadir características** - Implementa nuevas features
5. **Mejorar documentación** - Corrige o amplía la docs
6. **Traducciones** - Traduce la documentación
7. **Tests** - Añade tests para cubrir más casos

### Primeras Contribuciones

Si es tu primera vez contribuyendo:

1. Busca issues etiquetados como `good first issue` o `principiantes`
2. Lee este documento completamente
3. No tengas miedo de hacer preguntas

## Configuración del Entorno

### 1. Fork del Repositorio

```bash
# Haz click en "Fork" en GitHub
# Luego clona tu fork
git clone https://github.com/TU-USUARIO/my-lenguaje.git
cd my-lenguaje
```

### 2. Configurar Repositorio Remoto

```bash
# Añadir el repositorio original como upstream
git remote add upstream https://github.com/ORIGINAL-USUARIO/my-lenguaje.git

# Verificar remotos
git remote -v
```

### 3. Crear Rama de Trabajo

```bash
# Actualizar desde upstream
git checkout main
git pull upstream main

# Crear rama para tu feature
git checkout -b feature/mi-nueva-caracteristica
```

### 4. Instalar Dependencias de Desarrollo

```bash
# Instalar dependencias base
pip install -r requirements.txt

# Instalar dependencias de desarrollo (si existen)
pip install -r requirements-dev.txt
```

## Estándares de Código

### Estilo de Código

- Sigue PEP 8 para código Python
- Usa 4 espacios para indentación
- Líneas de máximo 100 caracteres
- Usa type hints cuando sea posible

```python
# ✅ Bien
def saludar(nombre: str, edad: int = 0) -> str:
    """Saluda a una persona."""
    if edad >= 18:
        return f"Hola, {nombre}. Eres mayor de edad."
    return f"Hola, {nombre}."

# ❌ Mal
def saludar(n,e=0):
    if e>=18:
        return f"Hola, {n}. Mayor"
    return f"Hola, {n}"
```

### Commits

Usa [Conventional Commits](https://www.conventionalcommits.org/):

```
feat: añadir nueva característica
fix: corregir bug en el parser
docs: actualizar README
test: añadir tests para translator
refactor: refactorizar módulo core
chore: actualizar dependencias
```

Ejemplos:

```bash
git commit -m "feat: añadir autocompletado al editor"
git commit -m "fix: corregir error en optimizador"
git commit -m "docs: añadir ejemplos al README"
```

### Tests

- Escribe tests para nuevas características
- Asegúrate que todos los tests pasen
- Mantén la cobertura de código

```bash
# Ejecutar tests
python -m unittest discover tests -v

# Ejecutar test específico
python -m unittest tests.test_translator.TestTraductorMejorado -v
```

## Proceso de Pull Request

### 1. Antes de Enviar

- [ ] El código sigue los estándares
- [ ] Los tests pasan
- [ ] La documentación está actualizada
- [ ] El commit message es claro

### 2. Enviar PR

```bash
# Hacer commit de tus cambios
git add .
git commit -m "feat: descripción clara del cambio"

# Push a tu fork
git push origin feature/mi-nueva-caracteristica
```

### 3. Crear Pull Request en GitHub

1. Ve a tu fork en GitHub
2. Click en "Pull Request"
3. Selecciona la rama
4. Describe tus cambios
5. Espera la revisión

### 4. Después del PR

- Responde a los comentarios
- Haz los cambios solicitados
- Mantén el PR actualizado

## Reportar Bugs

### Plantilla de Bug Report

```markdown
**Descripción:**
Descripción clara del bug

**Para Reproducir:**
1. Crear archivo 'archivo.my'
2. Ejecutar 'python my.py run archivo.my'
3. Ver error

**Comportamiento Esperado:**
Lo que debería pasar

**Capturas:**
Si aplica

**Entorno:**
- OS: [Windows, Linux, Mac]
- Python: [3.8, 3.9, etc.]
- Versión My Lenguaje: [0.6.5]
```

### Dónde Reportar

- GitHub Issues: https://github.com/tu-usuario/my-lenguaje/issues
- Email: tu-email@ejemplo.com

## Solicitar Características

### Plantilla de Feature Request

```markdown
**Descripción:**
Qué característica te gustaría

**Motivación:**
Por qué es útil

**Ejemplo de Uso:**
```my
# Cómo se vería el código
función nueva_feature():
    imprimir("Nueva feature")
```

**Alternativas Consideradas:**
Otras soluciones que pensaste
```

## Áreas que Necesitan Ayuda

### Prioridad Alta 🔴

- [ ] Tests adicionales
- [ ] Documentación de API
- [ ] Ejemplos de uso
- [ ] Traducciones

### Prioridad Media 🟡

- [ ] Optimizaciones de rendimiento
- [ ] Mejoras al editor
- [ ] Nuevos snippets

### Prioridad Baja 🟢

- [ ] Temas para el editor
- [ ] Más ejemplos
- [ ] Tutoriales

## Recursos Útiles

- [Documentación Oficial](README.md)
- [Ejemplos](ejemplos/)
- [Tests](tests/)
- [Roadmap del Proyecto](README.md#roadmap)

## Reconocimiento

Los contribuidores serán listados en el archivo CONTRIBUTORS.md y mencionados en los release notes.

---

**¡Gracias por contribuir a My Lenguaje! 🎉**

Cualquier duda, no dudes en preguntar en los issues o Discord.
