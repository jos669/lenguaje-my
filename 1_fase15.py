import math as matematicas

class Animal:
    def __init__(self, nombre):
        self.nombre = nombre

    def hablar(self):
        print("El animal hace un sonido")


class Perro(Animal):
    def hablar(self):
        print("El perro " + self.nombre + " dice: Guau")


def factorial(n):
    if n <= 1:
        return 1
    else:
        return n * factorial(n - 1)


def es_par(numero):
    if numero % 2 == 0:
        return True
    else:
        return False


def analizar_lista(datos):
    suma = 0
    pares = 0
    impares = 0

    for n in datos:
        suma = suma + n
        if es_par(n):
            pares = pares + 1
        else:
            impares = impares + 1

    promedio = suma / len(datos)

    return dict({
        "suma": suma,
        "promedio": promedio,
        "pares": pares,
        "impares": impares
    })


def probar_excepciones():
    try:
        valor = int(input("Ingresa un número para dividir 100: "))
        resultado = 100 / valor
        print("Resultado:", resultado)
    except:
        print("Ocurrió un error en la división")
    finally:
        print("Bloque de control finalizado")


def bucle_complejo():
    contador = 0
    while contador < 5:
        if contador == 3:
            print("Número especial detectado")
        elif contador > 3:
            print("Mayor que tres")
        else:
            print("Menor que tres")

        contador = contador + 1


def sistema_principal():

    print("===== INICIANDO SISTEMA =====")

    nombre = input("Ingresa tu nombre: ")
    edad = int(input("Ingresa tu edad: "))

    persona = Perro(nombre)
    persona.hablar()

    if edad >= 18 and not False:
        print("Eres mayor de edad")
    else:
        print("Eres menor de edad")

    numeros = list([1,2,3,4,5,6,7,8,9,10])
    datos = analizar_lista(numeros)

    print("Suma total:", datos["suma"])
    print("Promedio:", datos["promedio"])
    print("Cantidad pares:", datos["pares"])
    print("Cantidad impares:", datos["impares"])

    print("Factorial de 5:", factorial(5))

    bucle_complejo()

    probar_excepciones()

    print("Raíz cuadrada de 16:", matematicas.sqrt(16))

    print("===== SISTEMA FINALIZADO =====")


sistema_principal()