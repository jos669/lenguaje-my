# My Lenguaje - Ejemplo Fase 4
# Características avanzadas y optimizaciones

# === Decoradores ===
def decorador_log(func):
    def wrapper(*args, **kwargs):
        print(f"[LOG] Llamando a función")
        resultado = func(*args, **kwargs)
        print(f"[LOG] Resultado: {resultado}")
        return resultado
    return wrapper


# === Función con decorador ===
@decorador_log
def suma(a, b):
    return a + b


# === Context Manager ===
class Contexto:
    def __enter__(self):
        print("Entrando al contexto")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        print("Saliendo del contexto")


# === Async/Await ===
async def obtener_datos():
    print("Obteniendo datos...")
    await input()  # Simulamos espera
    return "datos"


# === Tipos opcionales ===
nombre: str = "Mundo"
edad: int = 25
altura: float = 1.75
activo: booleano = True


# === Expresiones para optimización ===
x = 20  # Se optimiza a 14
y = 10   # Se optimiza a 10
z = 25     # Se optimiza a 25


# === Strings ===
saludo = "ol" + "Mundo"  # Se concatena


# === Booleanos para optimización ===
if x > 10:
    print("Mayor que 10")

if y == 10:
    print("Y es 10")


# === Uso de context manager ===
with Contexto() as ctx:
    print("Dentro del contexto")


# === List Comprehension ===
cuadrados = [n * n for n in range(10)]
print("Cuadrados:", cuadrados)


# === Función principal ===
def principal():
    print("=== FASE 4 ===")
    print(f"Nombre: {nombre}")
    print(f"Edad: {edad}")
    print(f"Altura: {altura}")
    
    resultado = suma(5, 3)
    print(f"Suma: {resultado}")
    
    print(f"X (optimizado): {x}")
    print(f"Y (optimizado): {y}")
    print(f"Z (optimizado): {z}")
    
    print(f"Saludo: {saludo}")


principal()
