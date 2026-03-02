# Ejemplo básico en My Lenguaje
# Guarda este archivo como hola.my

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
    print("Contador en cero")
else:
    print("Contador mayor a cero")

# Bucle para
for i in range(5):
    print("Iteración: " + str(i))

# Bucle mientras
while contador < 3:
    print("Contando: " + str(contador))
    contador = contador + 1

# Clase
class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad
    
    def presentarse(self):
        return "Soy " + self.nombre + " y tengo " + str(self.edad) + " años"

# Usar la clase
persona1 = Persona("Ana", 25)
print(persona1.presentarse())

# Lista
numeros = [1, 2, 3, 4, 5]
print("Lista: " + str(numeros))
print("Longitud: " + str(len(numeros)))

# Operadores lógicos
x = 10
if x > 5 and x < 15:
    print("x está en el rango correcto")

# Manejo de errores
try:
    resultado = 10 / 0
except:
    print("¡Error detectado!")
finally:
    print("Bloque finalmente ejecutado")

print("¡Programa terminado!")
