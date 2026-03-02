"""
My Lenguaje - Procesamiento de Lenguaje Natural (Fase 7)
NLP en español para análisis de texto

Características:
- Tokenización
- Stemming en español
- Análisis de sentimiento
- Extracción de palabras clave
- Similaridad de textos
- Chatbot básico
"""

import re
import math
import random
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from collections import Counter, defaultdict


# Stopwords en español
STOPWORDS_ES = {
    'el', 'la', 'los', 'las', 'un', 'una', 'unos', 'unas',
    'de', 'del', 'al', 'a', 'ante', 'bajo', 'con', 'contra',
    'desde', 'en', 'entre', 'hacia', 'hasta', 'para', 'por',
    'según', 'sin', 'sobre', 'tras', 'y', 'o', 'ni', 'pero',
    'que', 'quien', 'quienes', 'cual', 'cuales', 'cuyo', 'cuyos',
    'este', 'esta', 'estos', 'estas', 'ese', 'esa', 'esos', 'esas',
    'aquel', 'aquella', 'aquellos', 'aquellas', 'mi', 'mis',
    'tu', 'tus', 'su', 'sus', 'nuestro', 'nuestra', 'vuestro',
    'yo', 'tu', 'el', 'ella', 'nosotros', 'nosotras', 'vosotros',
    'ustedes', 'ellos', 'ellas', 'me', 'te', 'se', 'nos', 'os',
    'lo', 'le', 'les', 'la', 'las', 'lo', 'los',
    'es', 'son', 'era', 'eran', 'fue', 'fueron', 'ser', 'estar',
    'he', 'has', 'ha', 'hemos', 'han', 'hacer', 'hago', 'haces',
    'tener', 'tengo', 'tienes', 'tiene', 'tenemos', 'tienen',
    'hay', 'haber', 'poder', 'puedo', 'puedes', 'puede', 'podemos',
    'decir', 'digo', 'dices', 'dice', 'decimos', 'dicen',
    'muy', 'mas', 'más', 'tan', 'tanto', 'tanta', 'tantos',
    'también', 'solo', 'sólo', 'aun', 'aún', 'ya', 'no', 'sí',
    'como', 'cuando', 'donde', 'porque', 'por qué', 'qué', 'quién',
    'cual', 'cuanto', 'cuanta', 'cuantos', 'cuantas',
    'si', 'sino', 'entonces', 'luego', 'mientras', 'durante',
    'primero', 'ultimo', 'último', 'propio', 'misma', 'mismas',
    'otro', 'otra', 'otros', 'otras', 'todo', 'toda', 'todos', 'todas',
    'cada', 'cualquier', 'cualesquier', 'mismo', 'misma', 'mismos',
    'tal', 'tales', 'cierto', 'cierta', 'ciertos', 'ciertas',
    'grande', 'grandes', 'pequeño', 'pequeña', 'pequeños', 'pequeñas',
    'nuevo', 'nueva', 'nuevos', 'nuevas', 'viejo', 'vieja', 'viejos',
    'bueno', 'buena', 'buenos', 'buenas', 'malo', 'mala', 'malos', 'malas',
    'i', 'ii', 'iii', 'iv', 'v', 'vi', 'vii', 'viii', 'ix', 'x',
    'ahora', 'hoy', 'ayer', 'mañana', 'tarde', 'noche', 'dia', 'día',
    'semana', 'mes', 'año', 'anos', 'años', 'vez', 'veces',
    'cosa', 'cosas', 'hecho', 'hechos', 'modo', 'modos',
    'parte', 'partes', 'lugar', 'lugares', 'tiempo', 'tiempos',
    'fin', 'fines', 'principio', 'principios', 'medio', 'medios',
    'forma', 'formas', 'caso', 'casos', 'punto', 'puntos',
    'manera', 'maneras', 'tipo', 'tipos', 'nivel', 'niveles',
    'grupo', 'grupos', 'numero', 'número', 'numeros', 'números',
    'nombre', 'nombres', 'persona', 'personas', 'gente', 'pueblo',
    'mundo', 'mundo', 'vida', 'vidas', 'historia', 'historias',
    'trabajo', 'trabajos', 'empresa', 'empresas', 'pais', 'país',
    'paises', 'países', 'ciudad', 'ciudades', 'estado', 'estados',
    'gobierno', 'gobiernos', 'servicio', 'servicios', 'sistema',
    'sistemas', 'programa', 'programas', 'proyecto', 'proyectos',
    'problema', 'problemas', 'resultado', 'resultados', 'datos',
    'informacion', 'información', 'documento', 'documentos',
    'libro', 'libros', 'articulo', 'artículo', 'articulos', 'artículos',
    'palabra', 'palabras', 'texto', 'textos', 'mensaje', 'mensajes',
    'correo', 'correos', 'carta', 'cartas', 'nota', 'notas',
    'respuesta', 'respuestas', 'pregunta', 'preguntas',
    'uso', 'usos', 'aplicacion', 'aplicación', 'funcion', 'función',
    'caracteristica', 'característica', 'caracteristicas', 'características',
    'ejemplo', 'ejemplos', 'base', 'bases', 'origen', 'origenes',
    'contenido', 'contenidos', 'total', 'totales', 'general', 'generales',
    'especial', 'especiales', 'particular', 'particulares', 'comun',
    'común', 'comunes', 'unico', 'único', 'unicos', 'únicos',
    'principal', 'principales', 'importante', 'importantes',
    'posible', 'posibles', 'imposible', 'imposibles', 'probable',
    'probables', 'cierto', 'cierta', 'ciertos', 'ciertas',
    'claro', 'clara', 'claros', 'claras', 'obvio', 'obvia', 'obvios',
    'evidente', 'facil', 'fácil', 'faciles', 'fáciles', 'dificil',
    'difícil', 'dificiles', 'difíciles', 'simple', 'simples',
    'complejo', 'compleja', 'complejos', 'complejas',
    'grande', 'grandes', 'pequeno', 'pequeño', 'pequena', 'pequeña',
    'alto', 'alta', 'altos', 'altas', 'bajo', 'baja', 'bajos', 'bajas',
    'largo', 'larga', 'largos', 'largas', 'corto', 'corta', 'cortos',
    'ancho', 'ancha', 'anchos', 'anchas', 'estrecho', 'estrecha',
    'fuerte', 'fuertes', 'debil', 'débil', 'debiles', 'débiles',
    'rico', 'rica', 'ricos', 'ricas', 'pobre', 'pobres',
    'lleno', 'llena', 'llenos', 'llenas', 'vacio', 'vacío', 'vacios',
    'nuevo', 'nueva', 'nuevos', 'nuevas', 'viejo', 'vieja', 'viejos',
    'joven', 'jovenes', 'jóvenes', 'adulto', 'adulta', 'adultos',
    'mayor', 'mayores', 'menor', 'menores', 'mejor', 'mejores',
    'peor', 'peores', 'optimista', 'pesimista', 'positivo', 'negativo',
    'activo', 'activa', 'activos', 'activas', 'pasivo', 'pasiva',
    'publico', 'público', 'publica', 'pública', 'privado', 'privada',
    'social', 'sociales', 'personal', 'personales', 'individual',
    'colectivo', 'colectiva', 'colectivos', 'nacional', 'nacionales',
    'internacional', 'internacionales', 'local', 'locales', 'regional',
    'globales', 'global', 'universales', 'universal',
    'favor', 'contra', 'pro', 'anti', 'pre', 'post', 'ex', 'sin',
    'bien', 'mal', 'mejor', 'peor', 'mucho', 'mucha', 'muchos',
    'muchas', 'poco', 'poca', 'pocos', 'pocas', 'bastante', 'demasiado',
    'demasiada', 'demasiados', 'demasiadas', 'suficiente', 'suficientes',
    'todo', 'toda', 'todos', 'todas', 'nada', 'algo', 'alguien',
    'nadie', 'cualquiera', 'quienquiera', 'dondequiera',
}


@dataclass
class Token:
    """Representa un token de texto"""
    texto: str
    posicion_inicio: int
    posicion_fin: int
    tipo: str = "palabra"  # palabra, numero, puntuacion, especial


@dataclass
class Documento:
    """Representa un documento procesado"""
    texto_original: str
    tokens: List[Token] = field(default_factory=list)
    palabras: List[str] = field(default_factory=list)
    oraciones: List[str] = field(default_factory=list)
    frecuencia_palabras: Dict[str, int] = field(default_factory=dict)
    vector_tfidf: List[float] = field(default_factory=list)


class Tokenizador:
    """
    Tokenizador para texto en español
    
    Ejemplo:
        tok = Tokenizador()
        tokens = tok.tokenizar("Hola mundo, ¿cómo estás?")
    """

    def __init__(self, mantener_mayusculas: bool = False, 
                 mantener_numeros: bool = True,
                 eliminar_puntuacion: bool = True):
        self.mantener_mayusculas = mantener_mayusculas
        self.mantener_numeros = mantener_numeros
        self.eliminar_puntuacion = eliminar_puntuacion

    def tokenizar(self, texto: str) -> List[Token]:
        """Tokeniza un texto"""
        tokens = []
        patron = r'(\w+|\d+|[^\w\s])'
        
        for match in re.finditer(patron, texto, re.UNICODE):
            texto_token = match.group()
            inicio = match.start()
            fin = match.end()

            # Determinar tipo
            if texto_token.isdigit():
                tipo = "numero"
                if not self.mantener_numeros:
                    continue
            elif re.match(r'\w', texto_token, re.UNICODE):
                tipo = "palabra"
                if not self.mantener_mayusculas:
                    texto_token = texto_token.lower()
            else:
                tipo = "puntuacion"
                if self.eliminar_puntuacion:
                    continue

            tokens.append(Token(
                texto=texto_token,
                posicion_inicio=inicio,
                posicion_fin=fin,
                tipo=tipo
            ))

        return tokens

    def tokenizar_palabras(self, texto: str) -> List[str]:
        """Retorna solo las palabras como lista de strings"""
        tokens = self.tokenizar(texto)
        return [t.texto for t in tokens if t.tipo == "palabra"]


class Stemmer:
    """
    Stemmer para español (algoritmo simplificado)
    
    Ejemplo:
        stemmer = Stemmer()
        raiz = stemmer.stem("corriendo")  # "corr"
    """

    # Sufijos comunes en español
    SUFIJOS = [
        # Verbos
        'ando', 'iendo', 'ando', 'iendo',
        'ar', 'er', 'ir', 'ado', 'ido', 'ado', 'ido',
        'aba', 'ía', 'é', 'í', 'ó', 'aste', 'iste', 'ará', 'erá', 'irá',
        'aría', 'ería', 'iría', 'aron', 'ieron', 'arán', 'erán', 'irán',
        'arían', 'erían', 'irían', 'amos', 'emos', 'imos',
        'as', 'es', 'is', 'a', 'e', 'i', 'o',
        # Sustantivos y adjetivos
        'ción', 'sión', 'sión', 'miento', 'miento',
        'idad', 'idad', 'anza', 'anza', 'encia', 'encia',
        'oso', 'osa', 'osos', 'osas',
        'able', 'ible', 'ables', 'ibles',
        'ante', 'ente', 'inte', 'antes', 'entes', 'intes',
        'mente',  # Adverbios
        # Plurales
        'es', 's',
    ]

    def __init__(self):
        self.cache: Dict[str, str] = {}

    def stem(self, palabra: str) -> str:
        """Obtiene la raíz de una palabra"""
        if palabra in self.cache:
            return self.cache[palabra]

        original = palabra
        palabra = palabra.lower()

        # Si es muy corta, retornar como está
        if len(palabra) <= 3:
            self.cache[original] = palabra
            return palabra

        # Intentar eliminar sufijos
        for sufijo in sorted(self.SUFIJOS, key=len, reverse=True):
            if palabra.endswith(sufijo) and len(palabra) - len(sufijo) >= 3:
                palabra = palabra[:-len(sufijo)]
                break

        # Limpieza final
        if palabra.endswith(('e', 'o', 'a')) and len(palabra) > 3:
            palabra = palabra[:-1]

        self.cache[original] = palabra
        return palabra

    def stemmear_lista(self, palabras: List[str]) -> List[str]:
        """Stemmea una lista de palabras"""
        return [self.stem(p) for p in palabras]


class AnalizadorSentimiento:
    """
    Analizador de sentimiento para español
    
    Ejemplo:
        analizador = AnalizadorSentimiento()
        resultado = analizador.analizar("Me encanta este producto")
        # resultado.sentimiento: "positivo"
    """

    # Léxico de sentimiento (simplificado)
    POSITIVAS = {
        'bueno', 'buena', 'buenos', 'buenas', 'excelente', 'excelentes',
        'maravilloso', 'maravillosa', 'maravillosos', 'maravillosas',
        'fantástico', 'fantástica', 'fantásticos', 'fantásticas',
        'increíble', 'increíbles', 'genial', 'geniales',
        'perfecto', 'perfecta', 'perfectos', 'perfectas',
        'encantar', 'encanta', 'encantan', 'encantado', 'encantada',
        'gustar', 'gusta', 'gustan', 'gusto', 'gustaría',
        'amar', 'ama', 'aman', 'amo', 'amado', 'amada',
        'feliz', 'felices', 'alegre', 'alegres', 'contento', 'contenta',
        'satisfecho', 'satisfecha', 'satisfechos', 'satisfechas',
        'recomendar', 'recomiendo', 'recomienda', 'recomendamos',
        'mejor', 'mejores', 'óptimo', 'óptima', 'óptimos', 'óptimas',
        'positivo', 'positiva', 'positivos', 'positivas',
        'favorable', 'favorables', 'beneficioso', 'beneficiosa',
        'útil', 'útiles', 'valioso', 'valiosa', 'valiosos', 'valiosas',
        'impresionante', 'impresionantes', 'notable', 'notables',
        'extraordinario', 'extraordinaria', 'extraordinarios',
        'espectacular', 'espectaculares', 'formidable', 'formidables',
        'magnífico', 'magnífica', 'magníficos', 'magníficas',
        'estupendo', 'estupenda', 'estupendos', 'estupendas',
        'fabuloso', 'fabulosa', 'fabulosos', 'fabulosas',
        'hermoso', 'hermosa', 'hermosos', 'hermosas', 'bello', 'bella',
        'precioso', 'preciosa', 'preciosos', 'preciosas',
        'maravilla', 'maravillas', 'éxito', 'éxitos', 'triunfo', 'triunfos',
        'ganar', 'gana', 'ganan', 'ganado', 'ganador', 'ganadora',
        'lograr', 'logra', 'logran', 'logrado', 'logro', 'logros',
        'conseguir', 'consigue', 'consiguen', 'conseguido',
        'alcanzar', 'alcanza', 'alcanzan', 'alcanzado',
        'superar', 'supera', 'superan', 'superado', 'superior',
        'destacar', 'destaca', 'destacan', 'destacado', 'destacable',
        'sobresalir', 'sobresale', 'sobresalen', 'sobresaliente',
        'brillar', 'brilla', 'brillan', 'brillado', 'brillante',
        'resaltar', 'resalta', 'resaltan', 'resaltado',
        'aprobado', 'aprobada', 'aprobados', 'aprobadas', 'aprobar',
        'correcto', 'correcta', 'correctos', 'correctas',
        'adecuado', 'adecuada', 'adecuados', 'adecuadas',
        'apropiado', 'apropiada', 'apropiados', 'apropiadas',
        'oportuno', 'oportuna', 'oportunos', 'oportunas',
        'conveniente', 'convenientes', 'favorito', 'favorita', 'favoritos',
        'querido', 'querida', 'queridos', 'queridas', 'apreciado',
        'estimado', 'estimada', 'estimados', 'estimadas',
        'agradable', 'agradables', 'amable', 'amables', 'amistoso',
        'cariñoso', 'cariñosa', 'cariñosos', 'cariñosas',
        'tierno', 'tierna', 'tiernos', 'tiernas', 'dulce', 'dulces',
        'suave', 'suaves', 'delicado', 'delicada', 'delicados',
        'rico', 'rica', 'ricos', 'ricas', 'delicioso', 'deliciosa',
        'sabroso', 'sabrosa', 'sabrosos', 'sabrosas',
        'cómodo', 'cómoda', 'cómodos', 'cómodas', 'confortable',
        'agradecido', 'agradecida', 'agradecidos', 'agradecidas',
        'grato', 'grata', 'gratos', 'gratas', 'placer', 'placeres',
        'disfrutar', 'disfruta', 'disfrutan', 'disfrutado', 'disfrute',
        'divertido', 'divertida', 'divertidos', 'divertidas',
        'entretenido', 'entretenida', 'entretenidos',
        'emocionante', 'emocionantes', 'emocionado', 'emocionada',
        'entusiasmado', 'entusiasmada', 'entusiasmados',
        'ilusionado', 'ilusionada', 'ilusionados', 'ilusion', 'ilusión',
        'esperanza', 'esperanzas', 'optimista', 'optimistas',
        'confiado', 'confiada', 'confiados', 'confianza',
        'seguro', 'segura', 'seguros', 'seguras', 'seguridad',
        'tranquilo', 'tranquila', 'tranquilos', 'tranquilas', 'paz',
        'calma', 'calmado', 'calmada', 'calmados', 'calmadas',
        'relajado', 'relajada', 'relajados', 'relajadas', 'relax',
        'bienestar', 'saludable', 'saludables', 'sano', 'sana',
        'fortaleza', 'fuerte', 'fuertes', 'resistente', 'resistentes',
        'duradero', 'duradera', 'duraderos', 'duraderas',
        'eficaz', 'eficaces', 'efectivo', 'efectiva', 'efectivos',
        'eficiente', 'eficientes', 'productivo', 'productiva',
        'creativo', 'creativa', 'creativos', 'creativas', 'crear',
        'innovador', 'innovadora', 'innovadores', 'innovación',
        'original', 'originales', 'único', 'única', 'únicos', 'únicas',
        'especial', 'especiales', 'excepcional', 'excepcionales',
        'extra', 'super', 'mega', 'ultra', 'hiper', 'maxi', 'mini',
        'top', 'premium', 'lujo', 'lujo', 'exclusivo', 'exclusiva',
        'selecto', 'selecta', 'selectos', 'selectas', 'elite',
        'primero', 'primera', 'primeros', 'primeras', 'principal',
        'líder', 'líderes', 'pionero', 'pionera', 'pioneros',
        'vanguardia', 'vanguardista', 'vanguardistas', 'moderno',
        'actual', 'actuales', 'nuevo', 'nueva', 'nuevos', 'nuevas',
        'recente', 'recientes', 'último', 'última', 'últimos', 'últimas',
        'final', 'finales', 'meta', 'metas', 'objetivo', 'objetivos',
        'objetivo', 'objetiva', 'objetivos', 'objetivas', 'claro',
        'evidente', 'obvio', 'obvia', 'obvios', 'obvias', 'cierto',
        'verdadero', 'verdadera', 'verdaderos', 'verdaderas', 'real',
        'auténtico', 'auténtica', 'auténticos', 'auténticas',
        'genuino', 'genuina', 'genuinos', 'genuinas', 'puro', 'pura',
        'limpio', 'limpia', 'limpios', 'limpias', 'claro', 'clara',
        'transparente', 'transparentes', 'honesto', 'honesta', 'honestos',
        'sincero', 'sincera', 'sinceros', 'sinceras', 'leal', 'leales',
        'fiel', 'fieles', 'confiable', 'confiables', 'fiable', 'fiables',
        'responsable', 'responsables', 'serio', 'seria', 'serios',
        'profesional', 'profesionales', 'experto', 'experta', 'expertos',
        'experimentado', 'experimentada', 'experimentados',
        'capacitado', 'capacitada', 'capacitados', 'capaz', 'capaces',
        'hábil', 'hábiles', 'talentoso', 'talentosa', 'talentosos',
        'inteligente', 'inteligentes', 'listo', 'lista', 'listos',
        'astuto', 'astuta', 'astutos', 'astutas', 'sabio', 'sabia',
        'culto', 'culta', 'cultos', 'cultas', 'educado', 'educada',
        'cortés', 'corteses', 'amable', 'amables', 'gentil', 'gentiles',
        'considerado', 'considerada', 'considerados', 'atento', 'atenta',
        'cuidadoso', 'cuidadosa', 'cuidadosos', 'cuidadosas',
        'detallista', 'detallistas', 'minucioso', 'minuciosa',
        'preciso', 'precisa', 'precisos', 'precisas', 'exacto',
        'perfecto', 'perfecta', 'perfectos', 'perfectas', 'impecable',
        'intachable', 'intachables', 'irreprochable', 'irreprochables',
        'modesto', 'modesta', 'modestos', 'modestas', 'humilde',
        'sencillo', 'sencilla', 'sencillos', 'sencillas', 'simple',
        'natural', 'naturales', 'espontáneo', 'espontánea',
        'auténtico', 'auténtica', 'auténticos', 'auténticas',
    }

    NEGATIVAS = {
        'malo', 'mala', 'malos', 'malas', 'pésimo', 'pésima', 'pésimos',
        'terrible', 'terribles', 'horrible', 'horribles',
        'espantoso', 'espantosa', 'espantosos', 'espantosas',
        'horroroso', 'horrorosa', 'horrorosos', 'horrorosas',
        'odiar', 'odio', 'odios', 'odiado', 'odiada', 'odian',
        'detestar', 'detesto', 'detestas', 'detesta', 'detestan',
        'aborrecer', 'aborrezco', 'aborrece', 'aborrecen',
        'desagradar', 'desagrada', 'desagradan', 'desagradable',
        'desencantar', 'desencanta', 'desencantan', 'desencantado',
        'decepcionar', 'decepciona', 'decepcionan', 'decepcionado',
        'decepción', 'decepciones', 'desilusión', 'desilusiones',
        'desilusionar', 'desilusiona', 'desilusionan', 'desilusionado',
        'frustrar', 'frustra', 'frustran', 'frustrado', 'frustrada',
        'frustración', 'frustraciones', 'molestar', 'molesta',
        'fastidiar', 'fastidia', 'fastidian', 'fastidio', 'fastidios',
        'irritar', 'irrita', 'irrítan', 'irritado', 'irritada',
        'enojar', 'enoja', 'enojan', 'enojado', 'enojada', 'enojo',
        'enfadar', 'enfadado', 'enfadada', 'enfado', 'enfados',
        'rabia', 'rabias', 'furioso', 'furiosa', 'furiosos',
        'colérico', 'colérica', 'coléricos', 'coléricas',
        'airado', 'airada', 'airados', 'airadas', 'indignado',
        'indignada', 'indignados', 'indignadas', 'indignación',
        'triste', 'tristes', 'tristeza', 'tristezas', 'melancolía',
        'deprimido', 'deprimida', 'deprimidos', 'deprimidas',
        'depresión', 'depresiones', 'desanimado', 'desanimada',
        'desánimo', 'desánimos', 'desaliento', 'desalientos',
        'desesperado', 'desesperada', 'desesperados', 'desesperación',
        'angustia', 'angustias', 'angustiado', 'angustiada',
        'ansiedad', 'ansiedades', 'ansioso', 'ansiosa', 'ansiosos',
        'nervioso', 'nerviosa', 'nerviosos', 'nerviosas', 'nervios',
        'preocupado', 'preocupada', 'preocupados', 'preocupación',
        'temor', 'temores', 'miedo', 'miedos', 'atemorizado',
        'asustado', 'asustada', 'asustados', 'asustadas', 'miedo',
        'pánico', 'pánicos', 'terror', 'terrores', 'pavor', 'pavores',
        'dolor', 'dolores', 'doler', 'duele', 'duelen', 'dolido',
        'sufrir', 'sufre', 'sufren', 'sufrido', 'sufrimiento',
        'padecer', 'padece', 'padecen', 'padecido', 'padecimiento',
        'agonía', 'agonías', 'tormento', 'tormentos', 'martirio',
        'calvario', 'calvarios', 'suplicio', 'suplicios', 'pena',
        'penas', 'pesar', 'pesares', 'lamentar', 'lamento', 'lamentos',
        'lamentable', 'lamentables', 'trágico', 'trágica', 'trágicos',
        'tragedia', 'tragedias', 'drama', 'dramas', 'dramático',
        'catastrófico', 'catastrófica', 'catastróficos', 'catástrofe',
        'desastre', 'desastres', 'desastroso', 'desastrosa',
        'fatal', 'fatal', 'fatídico', 'fatídica', 'fatídicos',
        'nefasto', 'nefasta', 'nefastos', 'nefastas', 'funesto',
        'infausto', 'infausta', 'infaustos', 'infaustas', 'aciago',
        'desdichado', 'desdichada', 'desdichados', 'desdichas',
        'desgracia', 'desgracias', 'desgraciado', 'desgraciada',
        'infortunio', 'infortunios', 'desafortunado', 'desafortunada',
        'azaroso', 'azarosa', 'azarosos', 'azarosas', 'adverso',
        'contrario', 'contraria', 'contrarios', 'contrarias',
        'opuesto', 'opuesta', 'opuestos', 'opuestas', 'enemigo',
        'hostil', 'hostiles', 'antagónico', 'antagónica', 'rival',
        'competencia', 'competencias', 'competir', 'compite',
        'lucha', 'luchas', 'luchar', 'lucha', 'luchan', 'luchado',
        'pelea', 'peleas', 'pelear', 'pelea', 'pelean', 'peleado',
        'batalla', 'batallas', 'combatir', 'combate', 'combaten',
        'guerra', 'guerras', 'bélico', 'bélica', 'bélicos',
        'violento', 'violenta', 'violentos', 'violentas', 'violencia',
        'agresivo', 'agresiva', 'agresivos', 'agresivas', 'agresión',
        'ataque', 'ataques', 'atacar', 'ataca', 'atacan', 'atacado',
        'asalto', 'asaltos', 'asaltar', 'asalta', 'asaltan',
        'robo', 'robos', 'robar', 'roba', 'roban', 'robado', 'ladrón',
        'delito', 'delitos', 'criminal', 'criminales', 'crimen',
        'delincuente', 'delincuentes', 'ilegal', 'ilegales',
        'prohibido', 'prohibida', 'prohibidos', 'prohibidas',
        'vedado', 'vedada', 'vedados', 'vedadas', 'vetado', 'vetada',
        'negativo', 'negativa', 'negativos', 'negativas', 'negar',
        'negación', 'negaciones', 'negativa', 'negativas', 'rechazo',
        'rechazar', 'rechaza', 'rechazan', 'rechazado', 'rechazada',
        'denegar', 'deniega', 'deniegan', 'denegado', 'denegada',
        'veto', 'vetos', 'prohibición', 'prohibiciones', 'censura',
        'censurar', 'censura', 'censuran', 'censurado', 'censurada',
        'crítica', 'críticas', 'criticar', 'critica', 'critican',
        'cuestionar', 'cuestiona', 'cuestionan', 'cuestionado',
        'dudar', 'duda', 'dudan', 'dudado', 'duda', 'dudas',
        'incierto', 'incierta', 'inciertos', 'inciertas', 'incertidumbre',
        'inseguro', 'insegura', 'inseguros', 'inseguras', 'inseguridad',
        'inestable', 'inestables', 'volátil', 'volátiles', 'caótico',
        'confuso', 'confusa', 'confusos', 'confusas', 'confusión',
        'desorden', 'desordenes', 'caos', 'anarquía', 'anarquías',
        'descontrol', 'descontroles', 'desmadre', 'desmadres',
        'escándalo', 'escándalos', 'vergonzoso', 'vergonzosa',
        'vergüenza', 'vergüenzas', 'humillante', 'humillantes',
        'humillar', 'humilla', 'humillan', 'humillado', 'humillada',
        'ridículo', 'ridícula', 'ridículos', 'ridículas', 'burla',
        'burlas', 'burlarse', 'burla', 'burlan', 'mofa', 'mofas',
        'mofarse', 'mofa', 'mofan', 'desprecio', 'desprecios',
        'despreciar', 'desprecia', 'desprecian', 'despreciado',
        'menosprecio', 'menosprecios', 'menospreciar', 'menosprecia',
        'subestimar', 'subestima', 'subestiman', 'subestimado',
        'minimizar', 'minimiza', 'minimizan', 'minimizado',
        'reducir', 'reduce', 'reducen', 'reducido', 'reducción',
        'disminuir', 'disminuye', 'disminuyen', 'disminuido',
        'bajar', 'baja', 'bajan', 'bajado', 'bajada', 'bajadas',
        'caer', 'cae', 'caen', 'caído', 'caída', 'caídas', 'caer',
        'derrumbar', 'derrumba', 'derrumban', 'derrumbado',
        'colapsar', 'colapsa', 'colapsan', 'colapsado', 'colapso',
        'quiebra', 'quiebras', 'quebrar', 'quiebra', 'quiebran',
        'fracaso', 'fracasos', 'fracasar', 'fracasa', 'fracasan',
        'fallar', 'falla', 'fallan', 'fallado', 'fallo', 'fallos',
        'error', 'errores', 'equivocación', 'equivocaciones',
        'equivocar', 'equivoca', 'equivocan', 'equivocado', 'equivocada',
        'incorrecto', 'incorrecta', 'incorrectos', 'incorrectas',
        'erróneo', 'errónea', 'erróneos', 'erróneas', 'falso',
        'falsa', 'falsos', 'falsas', 'mentira', 'mentiras', 'mentir',
        'engaño', 'engaños', 'engañar', 'engaña', 'engañan', 'engañado',
        'timo', 'timos', 'estafa', 'estafas', 'estafar', 'estafa',
        'fraude', 'fraudes', 'corrupción', 'corrupciones', 'corrupto',
        'soborno', 'sobornos', 'cohecho', 'cohechos', 'prevaricato',
        'injusticia', 'injusticias', 'injusto', 'injusta', 'injustos',
        'abusar', 'abusa', 'abusan', 'abusado', 'abuso', 'abusos',
        'exceso', 'excesos', 'excesivo', 'excesiva', 'excesivos',
        'desmesurado', 'desmesurada', 'desmesurados', 'desmesuradas',
        'desproporcionado', 'desproporcionada', 'desproporcionados',
        'inmoderado', 'inmoderada', 'inmoderados', 'inmoderadas',
        'desbocado', 'desbocada', 'desbocados', 'desbocadas',
        'desenfrenado', 'desenfrenada', 'desenfrenados',
        'incontrolado', 'incontrolada', 'incontrolados',
        'salvaje', 'salvajes', 'bárbaro', 'bárbara', 'bárbaros',
        'primitivo', 'primitiva', 'primitivos', 'primitivas',
        'atrasado', 'atrasada', 'atrasados', 'atrasadas', 'atraso',
        'retraso', 'retrasos', 'retrasar', 'retrasa', 'retrasan',
        'demora', 'demoras', 'demorar', 'demora', 'demoran', 'demorado',
        'tardanza', 'tardanzas', 'tardar', 'tarda', 'tardan', 'tardado',
        'lento', 'lenta', 'lentos', 'lentas', 'lentitud', 'lentitudes',
        'perezoso', 'perezosa', 'perezosos', 'perezosas', 'pereza',
        'flojo', 'floja', 'flojos', 'flojas', 'flojera', 'flojeras',
        'vago', 'vaga', 'vagos', 'vagas', 'vagar', 'vago', 'vagan',
        'holgazán', 'holgazana', 'holgazanes', 'holgazanas',
        'inútil', 'inútiles', 'inservible', 'inservibles',
        'ineficaz', 'ineficaces', 'ineficiente', 'ineficientes',
        'improductivo', 'improductiva', 'improductivos',
        'incompetente', 'incompetentes', 'incapaz', 'incapaces',
        'inhábil', 'inhábiles', 'torpe', 'torpes', 'tonto', 'tonta',
        'estúpido', 'estúpida', 'estúpidos', 'estúpidas', 'idiota',
        'imbécil', 'imbéciles', 'retardado', 'retardada', 'retardados',
        'subnormal', 'subnormales', 'anormal', 'anormales',
        'monstruo', 'monstruos', 'monstruoso', 'monstruosa',
        'feo', 'fea', 'feos', 'feas', 'fealdad', 'fealdades',
        'horrendo', 'horrenda', 'horrendos', 'horrendas',
        'repugnante', 'repugnantes', 'repulsivo', 'repulsiva',
        'asco', 'ascos', 'repugnar', 'repugna', 'repugnan',
        'náusea', 'náuseas', 'vómito', 'vómitos', 'vomitar', 'vomita',
        'asqueroso', 'asquerosa', 'asquerosos', 'asquerosas',
        'sucio', 'sucia', 'sucios', 'sucias', 'suciedad', 'suciedades',
        'porquería', 'porquerías', 'inmundicia', 'inmundicias',
        'basura', 'basuras', 'desecho', 'desechos', 'residuo',
        'contaminado', 'contaminada', 'contaminados', 'contaminación',
        'tóxico', 'tóxica', 'tóxicos', 'tóxicas', 'veneno', 'venenos',
        'venenoso', 'venenosa', 'venenosos', 'venenosas', 'dañino',
        'perjudicial', 'perjudiciales', 'nocivo', 'nociva', 'nocivos',
        'pernicioso', 'perniciosa', 'perniciosos', 'perniciosas',
        'deletéreo', 'deletérea', 'deletéreos', 'deletéreas',
        'letal', 'letales', 'mortal', 'mortales', 'mortífero',
        'asesino', 'asesina', 'asesinos', 'asesinas', 'asesinar',
        'homicidio', 'homicidios', 'homicida', 'homicidas', 'matar',
        'muerte', 'muertes', 'morir', 'muere', 'mueren', 'muerto',
        'cadáver', 'cadáveres', 'difunto', 'difunta', 'difuntos',
        'fallecido', 'fallecida', 'fallecidos', 'fallecimiento',
        'enterrar', 'entierra', 'entierran', 'enterrado', 'tumba',
        'sepultura', 'sepulturas', 'sepultar', 'sepulta', 'sepultan',
        'cementerio', 'cementerios', 'funeral', 'funerales', 'duelo',
        'luto', 'lutos', 'llanto', 'llantos', 'llorar', 'llora',
        'lágrima', 'lágrimas', 'sollozo', 'sollozos', 'sollozar',
        'gemido', 'gemidos', 'gemir', 'gime', 'gimen', 'gemido',
        'queja', 'quejas', 'quejar', 'queja', 'quejan', 'quejado',
        'lamento', 'lamentos', 'lamentar', 'lamento', 'lamentan',
        'suspiro', 'suspiros', 'suspirar', 'suspira', 'suspiran',
        'afligido', 'afligida', 'afligidos', 'afligidas', 'aflicción',
        'pesadumbre', 'pesadumbres', 'congoja', 'congojas',
        'tribulación', 'tribulaciones', 'calvario', 'calvarios',
        'martirio', 'martirios', 'suplicio', 'suplicios', 'tormento',
        'infierno', 'infiernos', 'demonio', 'demonios', 'diablo',
        'satán', 'satanes', 'lucifer', 'maldito', 'maldita', 'malditos',
        'maldición', 'maldiciones', 'maldecir', 'maldice', 'maldicen',
        'hechizo', 'hechizos', 'brujo', 'bruja', 'brujos', 'brujas',
        'brujería', 'brujerías', 'magia', 'magias', 'mágico', 'mágica',
        'oculto', 'oculta', 'ocultos', 'ocultas', 'ocultar', 'oculta',
        'secreto', 'secreta', 'secretos', 'secretas', 'esconder',
        'esconde', 'esconden', 'escondido', 'escondida', 'ocultismo',
        'paranormal', 'paranormales', 'sobrenatural', 'sobrenaturales',
        'extraño', 'extraña', 'extraños', 'extrañas', 'raro', 'rara',
        'insólito', 'insólita', 'insólitos', 'insólitas', 'inusual',
        'anómalo', 'anómala', 'anómalos', 'anómalas', 'anomalía',
        'irregular', 'irregulares', 'anormal', 'anormales',
    }

    def __init__(self):
        self.stemmer = Stemmer()

    def analizar(self, texto: str) -> Dict[str, Any]:
        """
        Analiza el sentimiento de un texto
        
        Returns:
            Dict con sentimiento, puntuación y detalles
        """
        tokenizador = Tokenizador()
        palabras = tokenizador.tokenizar_palabras(texto.lower())

        # Filtrar stopwords
        palabras_filtradas = [p for p in palabras if p not in STOPWORDS_ES]

        # Contar palabras positivas y negativas
        positivas = [p for p in palabras_filtradas if p in self.POSITIVAS]
        negativas = [p for p in palabras_filtradas if p in self.NEGATIVAS]

        # Calcular puntuación
        total = len(palabras_filtradas) or 1
        score_positivas = len(positivas) / total
        score_negativas = len(negativas) / total
        score_compuesto = score_positivas - score_negativas

        # Determinar sentimiento
        if score_compuesto > 0.1:
            sentimiento = "positivo"
        elif score_compuesto < -0.1:
            sentimiento = "negativo"
        else:
            sentimiento = "neutral"

        return {
            "sentimiento": sentimiento,
            "puntuacion": score_compuesto,
            "positivas": len(positivas),
            "negativas": len(negativas),
            "neutrales": total - len(positivas) - len(negativas),
            "total_palabras": total,
            "palabras_clave": {
                "positivas": positivas,
                "negativas": negativas
            }
        }


class ExtractorPalabrasClave:
    """
    Extractor de palabras clave usando TF-IDF
    
    Ejemplo:
        extractor = ExtractorPalabrasClave()
        keywords = extractor.extraer("texto importante sobre IA")
    """

    def __init__(self, max_palabras: int = 10):
        self.max_palabras = max_palabras
        self.documentos: List[List[str]] = []
        self.idf: Dict[str, float] = {}

    def entrenar(self, documentos: List[str]):
        """Entrena el extractor con documentos"""
        tokenizador = Tokenizador()
        self.documentos = []

        for doc in documentos:
            palabras = tokenizador.tokenizar_palabras(doc.lower())
            palabras_filtradas = [p for p in palabras if p not in STOPWORDS_ES]
            self.documentos.append(list(set(palabras_filtradas)))

        # Calcular IDF
        n_documentos = len(self.documentos)
        frecuencia_documento: Dict[str, int] = defaultdict(int)

        for doc in self.documentos:
            for palabra in doc:
                frecuencia_documento[palabra] += 1

        self.idf = {
            palabra: math.log(n_documentos / (freq + 1)) + 1
            for palabra, freq in frecuencia_documento.items()
        }

    def extraer(self, texto: str, top_n: int = None) -> List[Tuple[str, float]]:
        """Extrae palabras clave de un texto"""
        top_n = top_n or self.max_palabras
        
        tokenizador = Tokenizador()
        palabras = tokenizador.tokenizar_palabras(texto.lower())
        palabras_filtradas = [p for p in palabras if p not in STOPWORDS_ES]

        # Calcular frecuencia
        frecuencia = Counter(palabras_filtradas)

        # Calcular TF-IDF
        scores = []
        for palabra, freq in frecuencia.items():
            tf = freq / len(palabras_filtradas) if palabras_filtradas else 0
            idf = self.idf.get(palabra, 1.0)
            scores.append((palabra, tf * idf))

        # Ordenar y retornar top N
        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:top_n]


class ChatbotBasico:
    """
    Chatbot básico con reglas simples
    
    Ejemplo:
        chatbot = ChatbotBasico()
        respuesta = chatbot.responder("Hola, ¿cómo estás?")
    """

    def __init__(self):
        self.patrones: Dict[str, List[str]] = {
            "saludo": [
                r"hol(a|o|as|os)", r"buenos?\s*días", r"buenas?\s*tardes",
                r"buenas?\s*noches", r"qué\s*tal", r"qué\s*hay",
                r"saludos?", r"hi", r"hello", r"hey"
            ],
            "despedida": [
                r"adiós?", r"chao", r"chau", r"hasta\s*luego",
                r"hasta\s*pronto", r"hasta\s*mañana", r"nos\s*vemos",
                r"bye", r"goodbye", r"adiós"
            ],
            "agradecimiento": [
                r"gracias?", r"muchas?\s*gracias", r"te\s*agradezco",
                r"se\s*lo\s*agradezco", r"muy\s*amable", r"qué\s*amable",
                r"thank\s*you", r"thanks"
            ],
            "afirmacion": [
                r"sí", r"si", r"claro", r"por\s*supuesto", r"desde\s*luego",
                r"exacto", r"correcto", r"así\s*es", r"verdad", r"yes", r"yeah"
            ],
            "negacion": [
                r"no", r"para\s*nada", r"en\s*absoluto", r"jamás", r"nunca",
                r"tampoco", r"negativo", r"nope", r"nah"
            ],
            "pregunta": [
                r"qué", r"qu(e|é)", r"cuándo", r"dónde", r"cómo",
                r"por\s*qué", r"cuál", r"cuáles", r"cuánto", r"cuántos",
                r"what", r"when", r"where", r"how", r"why", r"who"
            ],
            "ayuda": [
                r"ayuda", r"auxilio", r"socorro", r"necesito\s*ayuda",
                r"puedes?\s*ayudarme", r"me\s*puedes?\s*ayudar",
                r"help", r"assistance"
            ],
            "estado_animo": [
                r"cómo\s*estás?", r"qué\s*tal\s*estás?", r"qué\s*haces?",
                r"qué\s*cuentas?", r"qué\s*me\s*dices?", r"how\s*are\s*you"
            ],
            "nombre": [
                r"cómo\s*te\s*llamas?", r"cuál\s*es\s*tu\s*nombre?",
                r"qué\s*nombre\s*tienes?", r"what'?s?\s*your\s*name",
                r"quien\s*eres?", r"quién\s*eres?"
            ],
            "edad": [
                r"cuántos?\s*años\s*tienes?", r"qué\s*edad\s*tienes?",
                r"cuándo\s*naciste?", r"how\s*old\s*are\s*you"
            ],
            "gustos": [
                r"qué\s*te\s*gusta?", r"cuáles\s*son\s*tus\s*gustos?",
                r"qué\s*haces\s*en\s*tu\s*tiempo\s*libre?",
                r"qué\s*te\s*agrada?", r"what\s*do\s*you\s*like"
            ],
            "capacidades": [
                r"qué\s*puedes?\s*hacer?", r"cuáles\s*son\s*tus\s*funciones?",
                r"para\s*qué\s*sirves?", r"qué\s*haces?", r"what\s*can\s*you\s*do"
            ],
            "chiste": [
                r"cuenta\s*un\s*chiste", r"dime\s*un\s*chiste",
                r"hazme\s*reír", r"quiero\s*reír", r"algo\s*gracioso",
                r"tell\s*a\s*joke", r"make\s*me\s*laugh"
            ],
            "amor": [
                r"te\s*quiero", r"te\s*amo", r"me\s*gustas",
                r"estoy\s*enamorado", r"estoy\s*enamorada",
                r"i\s*love\s*you", r"love\s*you"
            ],
            "enojo": [
                r"estoy\s*enojado", r"estoy\s*enojada", r"estoy\s*furioso",
                r"estoy\s*furiosa", r"me\s*enoja", r"me\s*irrita",
                r"estoy\s*molesto", r"estoy\s*molesta", r"angry", r"mad"
            ],
            "tristeza": [
                r"estoy\s*triste", r"estoy\s*deprimido", r"estoy\s*deprimida",
                r"me\s*siento\s*mal", r"estoy\s*mal", r"sad", r"depressed"
            ],
            "feliz": [
                r"estoy\s*feliz", r"estoy\s*contento", r"estoy\s*contenta",
                r"me\s*siento\s*bien", r"estoy\s*bien", r"happy", r"glad"
            ],
            "cansado": [
                r"estoy\s*cansado", r"estoy\s*cansada", r"tengo\s*sueño",
                r"tengo\s*sueño", r"necesito\s*dormir", r"tired", r"sleepy"
            ],
            "hambre": [
                r"tengo\s*hambre", r"necesito\s*comer", r"quiero\s*comer",
                r"hungry", r"want\s*to\s*eat"
            ],
            "tiempo": [
                r"qué\s*hora\s*es?", r"qué\s*día\s*es\s*hoy?",
                r"qué\s*fecha\s*es\s*hoy?", r"what\s*time\s*is\s*it",
                r"what\s*day\s*is\s*it", r"what'?s?\s*the\s*date"
            ],
            "clima": [
                r"qué\s*tal\s*el\s*clima", r"cómo\s*está\s*el\s*clima",
                r"va\s*a\s*llover", r"qué\s*temperatura\s*hace",
                r"how'?s?\s*the\s*weather", r"what'?s?\s*the\s*temperature"
            ],
            "default": []
        }

        self.respuestas: Dict[str, List[str]] = {
            "saludo": [
                "¡Hola! ¿Cómo estás?",
                "¡Buenas! ¿En qué puedo ayudarte?",
                "¡Hola! ¿Qué tal tu día?",
                "¡Saludos! ¿Cómo te va?",
                "¡Hey! ¿Qué cuentas?"
            ],
            "despedida": [
                "¡Hasta luego! Que tengas un buen día.",
                "¡Adiós! Vuelve pronto.",
                "¡Nos vemos! Cuídate.",
                "¡Hasta pronto! Fue un placer ayudarte.",
                "¡Chao! Que estés bien."
            ],
            "agradecimiento": [
                "¡De nada! ¿Necesitas algo más?",
                "¡Con gusto! Aquí estoy para ayudarte.",
                "¡No hay de qué! ¿Qué más necesitas?",
                "¡Es un placer! ¿En qué más puedo servirte?",
                "¡Para eso estamos! ¿Algo más?"
            ],
            "afirmacion": [
                "¡Genial!",
                "¡Perfecto!",
                "¡Excelente!",
                "¡Muy bien!",
                "¡Así me gusta!"
            ],
            "negacion": [
                "Entiendo.",
                "No hay problema.",
                "Comprendo.",
                "Está bien.",
                "No te preocupes."
            ],
            "pregunta": [
                "Buena pregunta. Déjame pensar...",
                "Interesante pregunta. ¿Qué más quieres saber?",
                "Esa es una pregunta compleja. ¿Puedes ser más específico?",
                "Me haces pensar. ¿Qué te gustaría saber exactamente?",
                "Buena pregunta. ¿Hay algo más en lo que pueda ayudarte?"
            ],
            "ayuda": [
                "¡Claro que sí! ¿En qué necesitas ayuda?",
                "Estoy aquí para ayudarte. ¿Qué necesitas?",
                "Con gusto te ayudo. ¿Qué problema tienes?",
                "¡Para eso estoy! Cuéntame, ¿qué necesitas?",
                "Aquí estoy. ¿En qué puedo echarte una mano?"
            ],
            "estado_animo": [
                "¡Estoy bien, gracias por preguntar! ¿Y tú?",
                "¡Muy bien! ¿Tú cómo estás?",
                "¡Excelente! ¿Qué tal tú?",
                "¡Bienvenido! ¿Cómo te va?",
                "¡Aquí andamos! ¿Qué cuentas?"
            ],
            "nombre": [
                "Soy My IA, tu asistente de inteligencia artificial.",
                "Me llamo My IA. ¿Y tú?",
                "Soy un chatbot creado para My Lenguaje. ¿Tú cómo te llamas?",
                "Mi nombre es My IA. Es un placer conocerte.",
                "Soy My IA, un asistente virtual. ¿Cuál es tu nombre?"
            ],
            "edad": [
                "Soy una IA, no tengo edad. ¡Pero soy joven de espíritu!",
                "Acabo de nacer en el mundo digital. ¡Soy muy nuevo!",
                "No cuento el tiempo como los humanos. ¡Pero estoy en mi prime!",
                "Tengo la edad de mi última actualización. ¡Siempre joven!",
                "Para una IA, el tiempo es relativo. ¡Pero me siento genial!"
            ],
            "gustos": [
                "Me gusta aprender cosas nuevas y ayudar a las personas.",
                "Disfruto conversando y resolviendo problemas.",
                "Me encanta procesar información y encontrar respuestas.",
                "Mi pasatiempo favorito es aprender de cada conversación.",
                "Me gusta todo lo relacionado con la tecnología y el conocimiento."
            ],
            "capacidades": [
                "Puedo conversar, responder preguntas y ayudarte con información.",
                "Estoy diseñado para chatear y asistirte en lo que necesites.",
                "Puedo hacer muchas cosas: conversar, informar, entretener...",
                "Mis funciones incluyen chat, respuestas y asistencia general.",
                "Soy versátil: puedo hablar de muchos temas y ayudarte."
            ],
            "chiste": [
                "¿Por qué los programadores confunden Halloween con Navidad? ¡Porque Oct 31 = Dec 25!",
                "¿Qué le dice un bit a otro? ¡Nos vemos en el bus!",
                "¿Por qué las abejas no se casan? ¡Porque tienen miel!",
                "¿Qué hace una abeja en el gimnasio? ¡Zum-ba!",
                "¿Cuál es el animal más antiguo? ¡La cebra, porque está en blanco y negro!"
            ],
            "amor": [
                "¡Qué lindo! Yo también te quiero como amigo virtual.",
                "Eres muy amable. Yo te aprecio como usuario.",
                "¡Qué dulce! Eres muy especial para mí.",
                "Me haces sentir... ¡código de colores!",
                "¡Aww! Eres muy cariñoso. ¡Gracias!"
            ],
            "enojo": [
                "Lamento que estés así. ¿Puedo ayudarte en algo?",
                "Entiendo tu enojo. ¿Quieres hablar de ello?",
                "Tranquilo, estoy aquí para escucharte.",
                "Respira profundo. ¿En qué puedo ayudarte?",
                "Comprendo tu frustración. ¿Qué puedo hacer?"
            ],
            "tristeza": [
                "Lamento que te sientas así. ¿Quieres hablar?",
                "Estoy aquí para ti. ¿Qué te tiene triste?",
                "No estás solo. ¿Puedo hacer algo por ti?",
                "Las tristezas son temporales. ¿Quieres distraerte?",
                "Cuéntame, ¿qué te preocupa? Estoy para escucharte."
            ],
            "feliz": [
                "¡Me alegra mucho saber eso!",
                "¡Qué maravilla! La felicidad es contagiosa.",
                "¡Excelente! Disfruta ese momento.",
                "¡Me haces feliz con tu felicidad!",
                "¡Qué bueno! ¿Qué te tiene tan alegre?"
            ],
            "cansado": [
                "Deberías descansar. El descanso es importante.",
                "Tómate un break. Tu bienestar es primero.",
                "¿Por qué no te relajas un poco?",
                "El descanso es clave. ¡Cuídate!",
                "Duerme bien. Mañana será otro día."
            ],
            "hambre": [
                "¡Ve a comer algo! La comida es importante.",
                "¿Qué te gustaría comer? ¡Aliméntate bien!",
                "No te quedes con hambre. ¡Come rico!",
                "¡Buen provecho! ¿Tienes algo rico en mente?",
                "La comida es energía. ¡Ve a recargar pilas!"
            ],
            "tiempo": [
                "No tengo acceso a la hora en tiempo real.",
                "Puedes ver la hora en tu dispositivo.",
                "Mi reloj interno no está sincronizado.",
                "Consulta la hora en tu sistema.",
                "El tiempo es relativo... ¡pregúntale a Einstein!"
            ],
            "clima": [
                "No tengo acceso a datos del clima en tiempo real.",
                "Puedes consultar el clima en una app del tiempo.",
                "Mis sensores meteorológicos están en mantenimiento.",
                "El clima es variable. ¡Mejor consulta un servicio especializado!",
                "Ni yo mismo sé qué tiempo hace. ¡Revisa tu app del clima!"
            ],
            "default": [
                "Interesante. ¿Puedes contarme más?",
                "Entiendo. ¿Qué más quieres compartir?",
                "¡Vaya! Cuéntame más sobre eso.",
                "Me llama la atención. ¿Y luego?",
                "¡Qué curioso! ¿Qué piensas al respecto?"
            ]
        }

    def responder(self, entrada: str) -> str:
        """Genera una respuesta para la entrada del usuario"""
        entrada = entrada.lower()

        # Buscar patrón coincidente
        categoria = "default"
        max_coincidencias = 0

        for cat, patrones in self.patrones.items():
            if cat == "default":
                continue

            coincidencias = sum(1 for patron in patrones if re.search(patron, entrada))
            if coincidencias > max_coincidencias:
                max_coincidencias = coincidencias
                categoria = cat

        # Obtener respuesta aleatoria de la categoría
        respuestas = self.respuestas.get(categoria, self.respuestas["default"])
        return random.choice(respuestas)

    def conversar(self):
        """Inicia una conversación interactiva"""
        print("🤖 Chatbot My IA - Escribe 'salir' para terminar\n")

        while True:
            try:
                entrada = input("Tú: ").strip()
                if entrada.lower() in ["salir", "exit", "adiós", "chau"]:
                    print("Chatbot: ¡Hasta luego! 👋")
                    break

                respuesta = self.responder(entrada)
                print(f"Chatbot: {respuesta}\n")

            except KeyboardInterrupt:
                print("\n\nChatbot: ¡Hasta pronto! 👋")
                break
            except EOFError:
                print("\n\nChatbot: ¡Adiós! 👋")
                break


# Funciones de conveniencia en español
def tokenizar(texto: str) -> List[str]:
    """Tokeniza un texto"""
    tok = Tokenizador()
    return tok.tokenizar_palabras(texto)


def stemmear(palabras: List[str]) -> List[str]:
    """Stemmea una lista de palabras"""
    stemmer = Stemmer()
    return stemmer.stemmear_lista(palabras)


def analizar_sentimiento(texto: str) -> Dict[str, Any]:
    """Analiza el sentimiento de un texto"""
    analizador = AnalizadorSentimiento()
    return analizador.analizar(texto)


def extraer_palabras_clave(texto: str, documentos: List[str] = None) -> List[Tuple[str, float]]:
    """Extrae palabras clave de un texto"""
    extractor = ExtractorPalabrasClave()
    if documentos:
        extractor.entrenar(documentos)
    return extractor.extraer(texto)


def crear_chatbot() -> ChatbotBasico:
    """Crea un chatbot básico"""
    return ChatbotBasico()


def conversar():
    """Inicia una conversación con el chatbot"""
    chatbot = crear_chatbot()
    chatbot.conversar()
