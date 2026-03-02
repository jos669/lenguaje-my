# Ejemplo básico in My Lenguaje
# Guarda este archivo as hola.my

# Variables
saludo = "Hola Mundo"
contador = 0

# Función básica
def saludar(nombre):
    return "Hola, " + nombre

# Imprimir saludo
print(saludo)
print(saludar("Mundo"))

# Condicional
if contador == 0:
    print("Contador in cero")
else:
    print("Contador mayor a cero")

# Bucle for
for i in range(5):
    print("Iteración: " + str(i))

# Bucle while
while contador < 3:
    print("Contando: " + str(contador))
    contador = contador + 1

# Clase
class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad
    
    def presentarse(self):
        return "Soy " + self.nombre + " and tengo " + str(self.edad) + " años"

# Usar la class
persona1 = Persona("Ana", 25)
print(persona1.presentarse())

# Lista
numeros = [1, 2, 3, 4, 5]
print("Lista: " + str(numeros))
print("Longitud: " + str(len(numeros)))

# Operadores lógicos
x = 10
if x > 5 and x < 15:
    print("x está in el range correcto")

# Manejo de errores
try:
    resultado = 10 / 0
except:
    print("¡Error detectado!")
finally:
    print("Bloque finally ejecutado")

print("¡Programa terminado!")
