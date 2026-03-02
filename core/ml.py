"""
My Lenguaje - Machine Learning (Fase 7)
Algoritmos de Aprendizaje Automático en español

Características:
- Regresión lineal
- Regresión logística
- K-Means clustering
- K-Nearest Neighbors
- Decision Trees
- Random Forest
"""

import math
import random
from typing import List, Dict, Any, Optional, Tuple, Union
from dataclasses import dataclass, field
from collections import Counter, defaultdict


@dataclass
class PuntoDatos:
    """Representa un punto de datos con características y etiqueta"""
    caracteristicas: List[float]
    etiqueta: Any = None
    peso: float = 1.0


class RegresionLineal:
    """
    Regresión Lineal simple y múltiple
    
    Ejemplo:
        modelo = RegresionLineal()
        modelo.ajustar(X, y)
        predicciones = modelo.predecir(X_nuevo)
    """

    def __init__(self):
        self.coeficientes: List[float] = []
        self.intercepto: float = 0.0
        self.r_cuadrado: float = 0.0

    def ajustar(self, X: List[List[float]], y: List[float]):
        """
        Ajusta el modelo de regresión lineal
        
        Args:
            X: Matriz de características (n_samples x n_features)
            y: Vector de valores objetivo
        """
        n_muestras = len(X)
        n_features = len(X[0]) if X else 0

        # Añadir columna de 1s para el intercepto
        X_aug = [[1] + list(x) for x in X]

        # Calcular (X'X)^-1 X'y usando mínimos cuadrados
        # Implementación simplificada con gradiente descendente
        
        self.coeficientes = [0.0] * (n_features + 1)
        tasa_aprendizaje = 0.01
        epocas = 1000

        for _ in range(epocas):
            gradientes = [0.0] * (n_features + 1)
            
            for i in range(n_muestras):
                prediccion = self._predecir_uno(X_aug[i])
                error = prediccion - y[i]
                
                for j in range(n_features + 1):
                    gradientes[j] += error * X_aug[i][j]
            
            for j in range(n_features + 1):
                self.coeficientes[j] -= tasa_aprendizaje * gradientes[j] / n_muestras

        self.intercepto = self.coeficientes[0]
        self.coeficientes = self.coeficientes[1:]

        # Calcular R²
        self.r_cuadrado = self._calcular_r_cuadrado(X, y)

    def _predecir_uno(self, x: List[float]) -> float:
        """Predice un solo valor"""
        return self.intercepto + sum(c * v for c, v in zip(self.coeficientes, x))

    def predecir(self, X: List[List[float]]) -> List[float]:
        """Predice múltiples valores"""
        return [self._predecir_uno(x) for x in X]

    def _calcular_r_cuadrado(self, X: List[List[float]], y: List[float]) -> float:
        """Calcula el coeficiente de determinación R²"""
        predicciones = self.predecir(X)
        
        y_media = sum(y) / len(y)
        ss_tot = sum((yi - y_media) ** 2 for yi in y)
        ss_res = sum((yi - pi) ** 2 for yi, pi in zip(y, predicciones))

        if ss_tot == 0:
            return 1.0 if ss_res == 0 else 0.0

        return 1 - (ss_res / ss_tot)

    def obtener_coeficientes(self) -> Dict[str, Any]:
        """Obtiene los coeficientes del modelo"""
        return {
            "coeficientes": self.coeficientes,
            "intercepto": self.intercepto,
            "r_cuadrado": self.r_cuadrado
        }


class RegresionLogistica:
    """
    Regresión Logística para clasificación binaria
    
    Ejemplo:
        modelo = RegresionLogistica()
        modelo.ajustar(X, y)
        predicciones = modelo.predecir(X_nuevo)
    """

    def __init__(self, tasa_aprendizaje: float = 0.01, epocas: int = 1000):
        self.tasa_aprendizaje = tasa_aprendizaje
        self.epocas = epocas
        self.coeficientes: List[float] = []
        self.intercepto: float = 0.0

    def _sigmoide(self, z: float) -> float:
        """Función sigmoide"""
        return 1 / (1 + math.exp(-max(-500, min(500, z))))

    def ajustar(self, X: List[List[float]], y: List[int]):
        """Ajusta el modelo"""
        n_muestras = len(X)
        n_features = len(X[0]) if X else 0

        self.coeficientes = [0.0] * n_features
        self.intercepto = 0.0

        for _ in range(self.epocas):
            gradientes_coef = [0.0] * n_features
            gradiente_inter = 0.0

            for i in range(n_muestras):
                z = self.intercepto + sum(c * v for c, v in zip(self.coeficientes, X[i]))
                prediccion = self._sigmoide(z)
                error = prediccion - y[i]

                for j in range(n_features):
                    gradientes_coef[j] += error * X[i][j]
                gradiente_inter += error

            for j in range(n_features):
                self.coeficientes[j] -= self.tasa_aprendizaje * gradientes_coef[j] / n_muestras
            self.intercepto -= self.tasa_aprendizaje * gradiente_inter / n_muestras

    def predecir_proba(self, X: List[List[float]]) -> List[float]:
        """Predice probabilidades"""
        resultados = []
        for x in X:
            z = self.intercepto + sum(c * v for c, v in zip(self.coeficientes, x))
            resultados.append(self._sigmoide(z))
        return resultados

    def predecir(self, X: List[List[float]], umbral: float = 0.5) -> List[int]:
        """Predice clases (0 o 1)"""
        probabilidades = self.predecir_proba(X)
        return [1 if p >= umbral else 0 for p in probabilidades]


class KMeans:
    """
    Algoritmo K-Means para clustering
    
    Ejemplo:
        kmeans = KMeans(k=3)
        etiquetas = kmeans.ajustar_predecir(datos)
        centroides = kmeans.centroides
    """

    def __init__(self, k: int = 3, iteraciones: int = 100):
        self.k = k
        self.iteraciones = iteraciones
        self.centroides: List[List[float]] = []
        self.etiquetas: List[int] = []

    def _distancia(self, p1: List[float], p2: List[float]) -> float:
        """Calcula distancia euclidiana"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

    def _asignar_clusters(self, datos: List[List[float]]) -> List[int]:
        """Asigna cada punto al centroide más cercano"""
        etiquetas = []
        for punto in datos:
            distancias = [self._distancia(punto, c) for c in self.centroides]
            etiquetas.append(distancias.index(min(distancias)))
        return etiquetas

    def _actualizar_centroides(self, datos: List[List[float]], 
                                etiquetas: List[int]) -> List[List[float]]:
        """Actualiza los centroides"""
        nuevos_centroides = []
        
        for i in range(self.k):
            puntos_cluster = [datos[j] for j in range(len(datos)) if etiquetas[j] == i]
            
            if puntos_cluster:
                n_features = len(puntos_cluster[0])
                centroide = [
                    sum(p[f] for p in puntos_cluster) / len(puntos_cluster)
                    for f in range(n_features)
                ]
                nuevos_centroides.append(centroide)
            else:
                # Si no hay puntos, mantener el centroide anterior
                nuevos_centroides.append(self.centroides[i] if i < len(self.centroides) 
                                         else [0] * len(datos[0]))

        return nuevos_centroides

    def ajustar_predecir(self, datos: List[List[float]]) -> List[int]:
        """
        Ajusta el modelo y predice clusters
        
        Args:
            datos: Lista de puntos de datos
            
        Returns:
            Lista de etiquetas de cluster
        """
        n_muestras = len(datos)
        n_features = len(datos[0]) if datos else 0

        # Inicializar centroides aleatoriamente
        random.shuffle(datos)
        self.centroides = [list(datos[i]) for i in range(min(self.k, n_muestras))]

        for _ in range(self.iteraciones):
            # Asignar clusters
            self.etiquetas = self._asignar_clusters(datos)
            
            # Actualizar centroides
            nuevos_centroides = self._actualizar_centroides(datos, self.etiquetas)
            
            # Verificar convergencia
            if nuevos_centroides == self.centroides:
                break
            
            self.centroides = nuevos_centroides

        return self.etiquetas

    def obtener_inercia(self, datos: List[List[float]]) -> float:
        """Calcula la inercia (suma de distancias al cuadrado)"""
        inercia = 0
        for punto, etiqueta in zip(datos, self.etiquetas):
            inercia += self._distancia(punto, self.centroides[etiqueta]) ** 2
        return inercia


class KNN:
    """
    K-Nearest Neighbors para clasificación y regresión
    
    Ejemplo:
        knn = KNN(k=5)
        knn.ajustar(X_train, y_train)
        predicciones = knn.predecir(X_test)
    """

    def __init__(self, k: int = 5):
        self.k = k
        self.X_train: List[List[float]] = []
        self.y_train: List[Any] = []

    def ajustar(self, X: List[List[float]], y: List[Any]):
        """Almacena los datos de entrenamiento"""
        self.X_train = X
        self.y_train = y

    def _distancia(self, p1: List[float], p2: List[float]) -> float:
        """Calcula distancia euclidiana"""
        return math.sqrt(sum((a - b) ** 2 for a, b in zip(p1, p2)))

    def predecir(self, X: List[List[float]]) -> List[Any]:
        """Predice para múltiples puntos"""
        return [self._predecir_uno(x) for x in X]

    def _predecir_uno(self, x: List[float]) -> Any:
        """Predice para un solo punto"""
        # Calcular distancias a todos los puntos de entrenamiento
        distancias = [(self._distancia(x, x_train), y_train) 
                      for x_train, y_train in zip(self.X_train, self.y_train)]
        
        # Ordenar por distancia y tomar los k más cercanos
        distancias.sort(key=lambda d: d[0])
        k_mas_cercanos = distancias[:self.k]

        # Votación mayoritaria para clasificación
        if isinstance(self.y_train[0], (int, float)) and set(self.y_train) <= {0, 1}:
            # Clasificación binaria
            votos = sum(y for _, y in k_mas_cercanos)
            return 1 if votos > self.k / 2 else 0
        elif all(isinstance(y, (int, float)) for _, y in k_mas_cercanos):
            # Regresión (promedio)
            return sum(y for _, y in k_mas_cercanos) / self.k
        else:
            # Clasificación multiclase
            votos = Counter(y for _, y in k_mas_cercanos)
            return votos.most_common(1)[0][0]


class ArbolDecision:
    """
    Árbol de Decisión para clasificación
    
    Ejemplo:
        arbol = ArbolDecision(max_profundidad=5)
        arbol.ajustar(X, y)
        predicciones = arbol.predecir(X_nuevo)
    """

    def __init__(self, max_profundidad: int = 10, min_muestras: int = 2):
        self.max_profundidad = max_profundidad
        self.min_muestras = min_muestras
        self.arbol: Optional[Dict] = None

    def _entropia(self, y: List[Any]) -> float:
        """Calcula la entropía de un conjunto de etiquetas"""
        if not y:
            return 0
        
        conteos = Counter(y)
        total = len(y)
        entropia = 0

        for count in conteos.values():
            if count > 0:
                p = count / total
                entropia -= p * math.log2(p)

        return entropia

    def _ganancia_informacion(self, y: List[Any], 
                              izquierda: List[Any], 
                              derecha: List[Any]) -> float:
        """Calcula la ganancia de información"""
        n = len(y)
        if n == 0:
            return 0

        entropia_padre = self._entropia(y)
        entropia_hijos = (
            len(izquierda) / n * self._entropia(izquierda) +
            len(derecha) / n * self._entropia(derecha)
        )

        return entropia_padre - entropia_hijos

    def _mejor_division(self, X: List[List[float]], y: List[Any]) -> Tuple[int, float]:
        """Encuentra la mejor división"""
        mejor_ganancia = -1
        mejor_feature = 0
        mejor_umbral = 0

        n_features = len(X[0]) if X else 0

        for feature in range(n_features):
            valores = sorted(set(x[feature] for x in X))

            for i in range(len(valores) - 1):
                umbral = (valores[i] + valores[i + 1]) / 2

                izquierda = [y[j] for j in range(len(X)) if X[j][feature] <= umbral]
                derecha = [y[j] for j in range(len(X)) if X[j][feature] > umbral]

                if izquierda and derecha:
                    ganancia = self._ganancia_informacion(y, izquierda, derecha)

                    if ganancia > mejor_ganancia:
                        mejor_ganancia = ganancia
                        mejor_feature = feature
                        mejor_umbral = umbral

        return mejor_feature, mejor_umbral

    def _construir_arbol(self, X: List[List[float]], y: List[Any], 
                         profundidad: int) -> Dict:
        """Construye el árbol recursivamente"""
        # Casos base
        if profundidad >= self.max_profundidad or len(set(y)) == 1 or len(y) < self.min_muestras:
            return {"hoja": True, "clase": Counter(y).most_common(1)[0][0] if y else None}

        # Encontrar mejor división
        feature, umbral = self._mejor_division(X, y)

        if feature is None:
            return {"hoja": True, "clase": Counter(y).most_common(1)[0][0]}

        # Dividir datos
        izquierda_idx = [i for i in range(len(X)) if X[i][feature] <= umbral]
        derecha_idx = [i for i in range(len(X)) if X[i][feature] > umbral]

        X_izq = [X[i] for i in izquierda_idx]
        y_izq = [y[i] for i in izquierda_idx]
        X_der = [X[i] for i in derecha_idx]
        y_der = [y[i] for i in derecha_idx]

        return {
            "hoja": False,
            "feature": feature,
            "umbral": umbral,
            "izquierda": self._construir_arbol(X_izq, y_izq, profundidad + 1),
            "derecha": self._construir_arbol(X_der, y_der, profundidad + 1)
        }

    def ajustar(self, X: List[List[float]], y: List[Any]):
        """Ajusta el árbol de decisión"""
        self.arbol = self._construir_arbol(X, y, 0)

    def _predecir_uno(self, x: List[float], nodo: Dict) -> Any:
        """Predice para un solo punto"""
        if nodo["hoja"]:
            return nodo["clase"]

        if x[nodo["feature"]] <= nodo["umbral"]:
            return self._predecir_uno(x, nodo["izquierda"])
        else:
            return self._predecir_uno(x, nodo["derecha"])

    def predecir(self, X: List[List[float]]) -> List[Any]:
        """Predice para múltiples puntos"""
        return [self._predecir_uno(x, self.arbol) for x in X]


class RandomForest:
    """
    Random Forest (ensamble de árboles de decisión)
    
    Ejemplo:
        rf = RandomForest(n_arboles=100)
        rf.ajustar(X, y)
        predicciones = rf.predecir(X_nuevo)
    """

    def __init__(self, n_arboles: int = 100, max_profundidad: int = 10):
        self.n_arboles = n_arboles
        self.max_profundidad = max_profundidad
        self.arboles: List[ArbolDecision] = []

    def _bootstrap(self, X: List[List[float]], y: List[Any]) -> Tuple[List[List[float]], List[Any]]:
        """Crea una muestra bootstrap"""
        n = len(X)
        indices = [random.randint(0, n - 1) for _ in range(n)]
        return [X[i] for i in indices], [y[i] for i in indices]

    def ajustar(self, X: List[List[float]], y: List[Any]):
        """Ajusta el random forest"""
        self.arboles = []

        for i in range(self.n_arboles):
            arbol = ArbolDecision(max_profundidad=self.max_profundidad)
            X_boot, y_boot = self._bootstrap(X, y)
            arbol.ajustar(X_boot, y_boot)
            self.arboles.append(arbol)

    def predecir(self, X: List[List[float]]) -> List[Any]:
        """Predice usando votación mayoritaria"""
        predicciones = []

        for x in X:
            votos_arboles = [arbol._predecir_uno(x, arbol.arbol) for arbol in self.arboles]
            voto_final = Counter(votos_arboles).most_common(1)[0][0]
            predicciones.append(voto_final)

        return predicciones


# Funciones de conveniencia en español
def crear_regresion_lineal() -> RegresionLineal:
    """Crea un modelo de regresión lineal"""
    return RegresionLineal()


def crear_regresion_logistica(tasa: float = 0.01, epocas: int = 1000) -> RegresionLogistica:
    """Crea un modelo de regresión logística"""
    return RegresionLogistica(tasa_aprendizaje=tasa, epocas=epocas)


def crear_kmeans(k: int = 3, iteraciones: int = 100) -> KMeans:
    """Crea un modelo K-Means"""
    return KMeans(k=k, iteraciones=iteraciones)


def crear_knn(k: int = 5) -> KNN:
    """Crea un modelo K-Nearest Neighbors"""
    return KNN(k=k)


def crear_arbol(max_profundidad: int = 10) -> ArbolDecision:
    """Crea un árbol de decisión"""
    return ArbolDecision(max_profundidad=max_profundidad)


def crear_random_forest(n_arboles: int = 100, max_profundidad: int = 10) -> RandomForest:
    """Crea un Random Forest"""
    return RandomForest(n_arboles=n_arboles, max_profundidad=max_profundidad)


def evaluar_precision(y_real: List[Any], y_pred: List[Any]) -> float:
    """Calcula la precisión de un modelo"""
    aciertos = sum(1 for r, p in zip(y_real, y_pred) if r == p)
    return aciertos / len(y_real) if y_real else 0


def evaluar_mse(y_real: List[float], y_pred: List[float]) -> float:
    """Calcula el error cuadrático medio"""
    return sum((r - p) ** 2 for r, p in zip(y_real, y_pred)) / len(y_real) if y_real else 0


def dividir_datos(X: List[List[float]], y: List[Any], 
                  test_size: float = 0.2) -> Tuple[List, List, List, List]:
    """Divide los datos en entrenamiento y prueba"""
    n = len(X)
    n_test = int(n * test_size)
    
    indices = list(range(n))
    random.shuffle(indices)

    test_indices = indices[:n_test]
    train_indices = indices[n_test:]

    X_train = [X[i] for i in train_indices]
    X_test = [X[i] for i in test_indices]
    y_train = [y[i] for i in train_indices]
    y_test = [y[i] for i in test_indices]

    return X_train, X_test, y_train, y_test
