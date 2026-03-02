import math as m
import random as r


class Logger:
    def __init__(self):
        self.historial = list([])

    def registrar(self, mensaje):
        self.historial.append(mensaje)
        print("[LOG]:", mensaje)

    def mostrar(self):
        for item in self.historial:
            print(" -", item)


class Persona:
    def __init__(self, nombre, edad):
        self.nombre = nombre
        self.edad = edad

    def es_mayor(self):
        return self.edad >= 18


class Empleado(Persona):
    def __init__(self, nombre, edad, salario):
        Persona.__init__(self, nombre, edad)
        self.salario = salario

    def bono(self):
        if self.salario > 5000:
            return self.salario * 0.10
        elif self.salario > 3000:
            return self.salario * 0.05
        else:
            return 0


def fibonacci(n):
    if n <= 1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)


def analizar_diccionario(datos):
    total = 0
    mayores = 0

    for clave in datos:
        edad = datos[clave]
        total = total + edad
        if edad >= 18:
            mayores = mayores + 1

    promedio = total / len(datos)

    return dict({
        "total": total,
        "promedio": promedio,
        "mayores": mayores
    })


def prueba_logica(x):
    if (x > 5 and x < 20) or x == 100:
        return True
    else:
        return False


def simulacion():
    print("===== SIMULACIÓN =====")

    logger = Logger()

    try:
        nombre = input("Nombre: ")
        edad = int(input("Edad: "))
        salario = float(input("Salario: "))

        emp = Empleado(nombre, edad, salario)

        logger.registrar("Empleado creado correctamente")

        if emp.es_mayor():
            logger.registrar("Es mayor de edad")
        else:
            logger.registrar("Es menor de edad")

        bono = emp.bono()
        print("Bono calculado:", bono)

        nums = list([])
        contador = 0

        while contador < 10:
            nums.append(contador)
            contador = contador + 1

        print("Lista generada:", nums)

        datos = dict({
            "Ana": 20,
            "Luis": 17,
            "Carlos": 30,
            "Maria": 15
        })

        resultado = analizar_diccionario(datos)

        print("Total edades:", resultado["total"])
        print("Promedio edades:", resultado["promedio"])
        print("Mayores:", resultado["mayores"])

        print("Fibonacci 6:", fibonacci(6))

        aleatorio = r.randint(1, 120)

        if prueba_logica(aleatorio):
            print("Número especial detectado:", aleatorio)
        else:
            print("Número normal:", aleatorio)

        print("Raíz de 25:", m.sqrt(25))

    except:
        print("Ocurrió un error en la simulación")

    finally:
        logger.registrar("Simulación finalizada")
        logger.mostrar()


simulacion()