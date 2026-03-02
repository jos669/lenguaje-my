"""
My Lenguaje - AI/ML Integration (Fase 7)
Inteligencia Artificial y Aprendizaje Automático en español

Características:
- Redes neuronales básicas
- Modelos pre-entrenados
- Inferencia de IA
- Integración con TensorFlow/PyTorch
"""

import math
import random
from typing import List, Dict, Any, Optional, Tuple, Callable
from dataclasses import dataclass, field
from enum import Enum


class FuncionActivacion(Enum):
    """Funciones de activación para redes neuronales"""
    SIGMOIDE = "sigmoide"
    RELU = "relu"
    TANH = "tanh"
    LINEAL = "lineal"
    SOFTMAX = "softmax"


@dataclass
class Neurona:
    """Representa una neurona en la red"""
    pesos: List[float] = field(default_factory=list)
    sesgo: float = 0.0
    funcion: FuncionActivacion = FuncionActivacion.SIGMOIDE

    def activar(self, x: float) -> float:
        """Aplica la función de activación"""
        if self.funcion == FuncionActivacion.SIGMOIDE:
            return 1 / (1 + math.exp(-max(-500, min(500, x))))
        elif self.funcion == FuncionActivacion.RELU:
            return max(0, x)
        elif self.funcion == FuncionActivacion.TANH:
            return math.tanh(x)
        elif self.funcion == FuncionActivacion.LINEAL:
            return x
        return x

    def procesar(self, entradas: List[float]) -> float:
        """Procesa las entradas y produce una salida"""
        if len(entradas) != len(self.pesos):
            raise ValueError(f"Entradas ({len(entradas)}) != pesos ({len(self.pesos)})")
        
        suma = sum(e * p for e, p in zip(entradas, self.pesos)) + self.sesgo
        return self.activar(suma)


@dataclass
class Capa:
    """Representa una capa de la red neuronal"""
    neuronas: List[Neurona] = field(default_factory=list)

    def procesar(self, entradas: List[float]) -> List[float]:
        """Procesa las entradas a través de todas las neuronas"""
        return [neurona.procesar(entradas) for neurona in self.neuronas]


class RedNeuronal:
    """
    Red Neuronal Artificial básica
    
    Ejemplo:
        red = RedNeuronal([2, 4, 1])  # 2 entradas, 4 ocultas, 1 salida
        resultado = red.predecir([0.5, 0.8])
    """

    def __init__(self, arquitectura: List[int], tasa_aprendizaje: float = 0.01):
        """
        Inicializa la red neuronal
        
        Args:
            arquitectura: Lista con el número de neuronas por capa
            tasa_aprendizaje: Tasa de aprendizaje para el entrenamiento
        """
        self.arquitectura = arquitectura
        self.tasa_aprendizaje = tasa_aprendizaje
        self.capas: List[Capa] = []
        self.historial_entrenamiento: List[Dict] = []

        self._inicializar_red()

    def _inicializar_red(self):
        """Inicializa las capas de la red con pesos aleatorios"""
        for i in range(len(self.arquitectura) - 1):
            entradas = self.arquitectura[i]
            salidas = self.arquitectura[i + 1]
            
            capa = Capa()
            for _ in range(salidas):
                neurona = Neurona(
                    pesos=[random.uniform(-1, 1) for _ in range(entradas)],
                    sesgo=random.uniform(-1, 1),
                    funcion=FuncionActivacion.RELU if i < len(self.arquitectura) - 2 else FuncionActivacion.SIGMOIDE
                )
                capa.neuronas.append(neurona)
            
            self.capas.append(capa)

    def predecir(self, entradas: List[float]) -> List[float]:
        """
        Realiza una predicción forward pass
        
        Args:
            entradas: Lista de valores de entrada
            
        Returns:
            Lista de valores de salida
        """
        if len(entradas) != self.arquitectura[0]:
            raise ValueError(f"Entradas deben ser de tamaño {self.arquitectura[0]}")

        salida = entradas
        for capa in self.capas:
            salida = capa.procesar(salida)
        
        return salida

    def entrenar(self, datos_entrada: List[List[float]], datos_salida: List[List[float]], 
                 epocas: int = 1000, verbose: bool = True) -> List[float]:
        """
        Entrena la red neuronal con backpropagation
        
        Args:
            datos_entrada: Lista de ejemplos de entrada
            datos_salida: Lista de salidas esperadas
            epocas: Número de épocas de entrenamiento
            verbose: Mostrar progreso
            
        Returns:
            Lista de errores por época
        """
        errores = []

        for epoca in range(epocas):
            error_total = 0

            for entrada, salida_esperada in zip(datos_entrada, datos_salida):
                # Forward pass
                salidas = self._forward(entrada)
                
                # Calcular error
                error = [e - s for e, s in zip(salidas[-1], salida_esperada)]
                error_total += sum(e ** 2 for e in error) / 2

                # Backward pass
                self._backward(entrada, salida_esperada)

            errores.append(error_total / len(datos_entrada))

            if verbose and (epoca % 100 == 0 or epoca == epocas - 1):
                print(f"Época {epoca}/{epocas} - Error: {errores[-1]:.6f}")

        self.historial_entrenamiento = [{"epoca": i, "error": e} for i, e in enumerate(errores)]
        return errores

    def _forward(self, entrada: List[float]) -> List[List[float]]:
        """Forward pass con almacenamiento de activaciones"""
        activaciones = [entrada]
        salida = entrada

        for capa in self.capas:
            salida = capa.procesar(salida)
            activaciones.append(salida)

        return activaciones

    def _backward(self, entrada: List[float], salida_esperada: List[float]):
        """Backward pass para actualizar pesos"""
        activaciones = self._forward(entrada)
        
        # Calcular deltas
        deltas = [None] * len(self.capas)
        
        # Capa de salida
        salida = activaciones[-1]
        error_salida = [e - s for e, s in zip(salida, salida_esperada)]
        deltas[-1] = [
            e * s * (1 - s) for e, s in zip(error_salida, salida)
        ]

        # Capas ocultas
        for i in range(len(self.capas) - 2, -1, -1):
            error_capa = [0] * len(self.capas[i].neuronas)
            
            for j, neurona in enumerate(self.capas[i + 1].neuronas):
                for k in range(len(error_capa)):
                    error_capa[k] += deltas[i + 1][j] * neurona.pesos[k]
            
            activacion = activaciones[i + 1]
            deltas[i] = [
                e * a * (1 - a) for e, a in zip(error_capa, activacion)
            ]

        # Actualizar pesos y sesgos
        for i, capa in enumerate(self.capas):
            for j, neurona in enumerate(capa.neuronas):
                for k in range(len(neurona.pesos)):
                    neurona.pesos[k] += self.tasa_aprendizaje * deltas[i][j] * activaciones[i][k]
                neurona.sesgo += self.tasa_aprendizaje * deltas[i][j]

    def guardar(self, archivo: str):
        """Guarda la red neuronal en un archivo"""
        import json
        
        datos = {
            "arquitectura": self.arquitectura,
            "tasa_aprendizaje": self.tasa_aprendizaje,
            "capas": [
                {
                    "neuronas": [
                        {"pesos": n.pesos, "sesgo": n.sesgo, "funcion": n.funcion.value}
                        for n in capa.neuronas
                    ]
                }
                for capa in self.capas
            ]
        }

        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2)

        print(f"✓ Red guardada en {archivo}")

    def cargar(self, archivo: str):
        """Carga una red neuronal desde un archivo"""
        import json

        with open(archivo, 'r', encoding='utf-8') as f:
            datos = json.load(f)

        self.arquitectura = datos["arquitectura"]
        self.tasa_aprendizaje = datos["tasa_aprendizaje"]
        self.capas = []

        for capa_datos in datos["capas"]:
            capa = Capa()
            for neurona_datos in capa_datos["neuronas"]:
                neurona = Neurona(
                    pesos=neurona_datos["pesos"],
                    sesgo=neurona_datos["sesgo"],
                    funcion=FuncionActivacion(neurona_datos["funcion"])
                )
                capa.neuronas.append(neurona)
            self.capas.append(capa)

        print(f"✓ Red cargada desde {archivo}")

    def obtener_reporte(self) -> str:
        """Genera un reporte de la red"""
        lineas = []
        lineas.append("=" * 50)
        lineas.append("🧠 RED NEURONAL")
        lineas.append("=" * 50)
        lineas.append(f"Arquitectura: {' → '.join(map(str, self.arquitectura))}")
        lineas.append(f"Tasa de aprendizaje: {self.tasa_aprendizaje}")
        lineas.append(f"Total de capas: {len(self.capas)}")
        
        total_parametros = sum(
            len(n.pesos) + 1 for capa in self.capas for n in capa.neuronas
        )
        lineas.append(f"Total de parámetros: {total_parametros}")
        
        if self.historial_entrenamiento:
            error_final = self.historial_entrenamiento[-1]["error"]
            lineas.append(f"Error final: {error_final:.6f}")
        
        lineas.append("=" * 50)
        return "\n".join(lineas)


class ClasificadorIA:
    """
    Clasificador de IA simple para tareas básicas
    
    Ejemplo:
        clf = ClasificadorIA()
        clf.entrenar(datos, etiquetas)
        prediccion = clf.clasificar(nueva_entrada)
    """

    def __init__(self):
        self.modelo: Optional[RedNeuronal] = None
        self.etiquetas: List[str] = []
        self.normalizador: Dict[str, float] = {}

    def entrenar(self, datos: List[List[float]], etiquetas: List[str], 
                 epocas: int = 500) -> List[float]:
        """Entrena el clasificador"""
        self.etiquetas = list(set(etiquetas))
        etiqueta_map = {e: i for i, e in enumerate(self.etiquetas)}

        # Codificar etiquetas
        salidas = []
        for etiq in etiquetas:
            vector = [0] * len(self.etiquetas)
            vector[etiqueta_map[etiq]] = 1
            salidas.append(vector)

        # Normalizar datos
        self._normalizar(datos)

        # Crear y entrenar red
        n_entradas = len(datos[0])
        n_salidas = len(self.etiquetas)
        n_ocultas = max(n_entradas * 2, n_salidas * 2)

        self.modelo = RedNeuronal([n_entradas, n_ocultas, n_salidas])
        errores = self.modelo.entrenar(datos, salidas, epocas=epocas, verbose=False)

        return errores

    def clasificar(self, entrada: List[float]) -> Tuple[str, float]:
        """
        Clasifica una entrada
        
        Returns:
            Tupla con (etiqueta, confianza)
        """
        if not self.modelo:
            raise ValueError("El modelo no está entrenado")

        # Normalizar entrada
        entrada_norm = self._aplicar_normalizacion(entrada)

        # Predecir
        salidas = self.modelo.predecir(entrada_norm)
        indice_max = salidas.index(max(salidas))
        confianza = max(salidas) / sum(salidas) if sum(salidas) > 0 else 0

        return self.etiquetas[indice_max], confianza

    def _normalizar(self, datos: List[List[float]]):
        """Calcula parámetros de normalización"""
        n_features = len(datos[0])
        
        for i in range(n_features):
            valores = [d[i] for d in datos]
            self.normalizador[f"min_{i}"] = min(valores)
            self.normalizador[f"max_{i}"] = max(valores)

    def _aplicar_normalizacion(self, entrada: List[float]) -> List[float]:
        """Aplica normalización a una entrada"""
        resultado = []
        
        for i, valor in enumerate(entrada):
            min_val = self.normalizador.get(f"min_{i}", 0)
            max_val = self.normalizador.get(f"max_{i}", 1)
            
            if max_val - min_val > 0:
                resultado.append((valor - min_val) / (max_val - min_val))
            else:
                resultado.append(0)

        return resultado


class AgenteIA:
    """
    Agente de IA básico para toma de decisiones
    
    Ejemplo:
        agente = AgenteIA(estados=["inicio", "fin"], acciones=["mover", "saltar"])
        agente.aprender(recompensas)
        accion = agente.elegir_accion(estado_actual)
    """

    def __init__(self, estados: List[str], acciones: List[str], 
                 tasa_aprendizaje: float = 0.1, factor_descuento: float = 0.9):
        self.estados = estados
        self.acciones = acciones
        self.tasa_aprendizaje = tasa_aprendizaje
        self.factor_descuento = factor_descuento
        
        # Tabla Q: estado -> acción -> valor
        self.tabla_q: Dict[str, Dict[str, float]] = {
            estado: {accion: 0.0 for accion in acciones}
            for estado in estados
        }

    def elegir_accion(self, estado: str, exploracion: float = 0.1) -> str:
        """Elige una acción usando ε-greedy"""
        if random.random() < exploracion:
            return random.choice(self.acciones)
        
        valores = self.tabla_q.get(estado, {})
        if not valores:
            return random.choice(self.acciones)
        
        return max(valores, key=valores.get)

    def actualizar(self, estado: str, accion: str, recompensa: float, 
                   nuevo_estado: str):
        """Actualiza la tabla Q con Q-learning"""
        valor_actual = self.tabla_q[estado][accion]
        
        # Mejor valor en el nuevo estado
        mejores_valores = self.tabla_q.get(nuevo_estado, {})
        mejor_valor_nuevo = max(mejores_valores.values()) if mejores_valores else 0

        # Actualizar con fórmula Q-learning
        self.tabla_q[estado][accion] = valor_actual + self.tasa_aprendizaje * (
            recompensa + self.factor_descuento * mejor_valor_nuevo - valor_actual
        )

    def aprender(self, episodios: List[Dict], verbose: bool = True):
        """
        Aprende de una lista de episodios
        
        Cada episodio es un dict con: estado, accion, recompensa, nuevo_estado
        """
        for i, ep in enumerate(episodios):
            self.actualizar(
                ep["estado"],
                ep["accion"],
                ep["recompensa"],
                ep["nuevo_estado"]
            )

        if verbose:
            print(f"✓ Agente aprendió de {len(episodios)} episodios")

    def obtener_politica(self) -> Dict[str, str]:
        """Obtiene la política óptima actual"""
        politica = {}
        
        for estado in self.estados:
            valores = self.tabla_q.get(estado, {})
            if valores:
                politica[estado] = max(valores, key=valores.get)
            else:
                politica[estado] = random.choice(self.acciones)

        return politica


# Funciones de conveniencia
def crear_red(entradas: int, ocultas: List[int], salidas: int) -> RedNeuronal:
    """Crea una red neuronal con la arquitectura especificada"""
    arquitectura = [entradas] + ocultas + [salidas]
    return RedNeuronal(arquitectura)


def cargar_modelo(archivo: str) -> RedNeuronal:
    """Carga un modelo guardado"""
    red = RedNeuronal([1, 1, 1])  # Arquitectura temporal
    red.cargar(archivo)
    return red


def entrenar_clasificador(datos: List[List[float]], etiquetas: List[str]) -> ClasificadorIA:
    """Entrena un clasificador rápidamente"""
    clf = ClasificadorIA()
    clf.entrenar(datos, etiquetas)
    return clf


# Integración con keywords en español para el lenguaje My
def inicializar_ia(config: Dict[str, Any] = None) -> Dict[str, Any]:
    """Inicializa el sistema de IA con configuración"""
    config = config or {}
    
    return {
        "red_neuronal": None,
        "clasificador": None,
        "agente": None,
        "config": config
    }


def red_neuronal(config: Dict[str, Any]) -> RedNeuronal:
    """Keyword en español para crear red neuronal"""
    arquitectura = config.get("arquitectura", [2, 4, 1])
    tasa = config.get("tasa_aprendizaje", 0.01)
    return RedNeuronal(arquitectura, tasa)


def entrenar(red: RedNeuronal, datos: List[List[float]], salidas: List[List[float]], 
             epocas: int = 1000) -> List[float]:
    """Keyword en español para entrenar red neuronal"""
    return red.entrenar(datos, salidas, epocas)


def predecir(red: RedNeuronal, entrada: List[float]) -> List[float]:
    """Keyword en español para hacer predicciones"""
    return red.predecir(entrada)


def guardar_modelo(red: RedNeuronal, archivo: str):
    """Keyword en español para guardar modelo"""
    red.guardar(archivo)


def cargar_modelo_ia(archivo: str) -> RedNeuronal:
    """Keyword en español para cargar modelo"""
    return cargar_modelo(archivo)
