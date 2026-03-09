# Parte 1
# ejercicio 1.1
print ("ejercicio 1.1\n")

nombre = "Alejandro"

edad = 21

altura = 1.65

es_estudiante = True

print ("Nombre:", nombre)
print ("Edad:", edad)
print ("Altura:", altura)
print ("Es estudiante:", es_estudiante)
#se imprime la asignacion que se le dio a las variable.

# ejercicio 1.2
print("\nejercicio 1.2\n")

print ("Tipo de nombre: ", type(nombre))
print ("Tipo de edad: ", type(edad))
print ("Tipo de altura: ", type(altura))
print ("Tipo de estudiante: ", type(es_estudiante))
#se desea imprimir el tipo o la clase de cada variable que se asignó antetiormente.

# ejercicio 1.3
print ("\nejercicio 1.3\n")

a = 15
b = 4

suma = a + b
resta = a - b
multiplicacion = a * b
division = a/b
division_entera = a//b
modulo = a%b
potencia = a**b

print("Suma:", suma)
print("Resta:", resta)
print("Multiplicacion:", multiplicacion)
print("Division:", division)
print("Division entera:", division_entera)
print("Modulo:", modulo)
print("Potencia:", potencia)

"""se realizan operaciones matematicas basicas 
entre los numeros asignados ( 15 y 4) y se imprimen los resukltados.
"""

# Parte 2
# ejercicio 2.1
print("\nejercicio 2.1\n")

numero = -5
if numero > 0:
    print("El numero es positivo.")
elif numero < 0:
    print("El numero es negativo.")
else:
    print("El numero es cero.")
#se quiere evaluar si un numero es positivo, negativo o es 0

# ejercicio 2.2
print("\nejercicio 2.2\n")

nota = 85
if nota>= 90:
    clasificacion = "Excelente"
elif nota < 90 and nota>= 80:
    clasificacion = "Bueno"
elif nota < 80 and nota >= 70:
    clasificacion = "Aceptable"
elif nota < 70 and nota >= 60:
    clasificacion = "Regular"
else:
    clasificacion = "Insuficiente"

print ("Nota:", nota)
print("Clasificacion:", clasificacion)
"""se evalua la nota de un estudiante 
y se le asigna a una clasificacion, 
despues se imprime la nota que obtuvo 
y la clasificacion correspondiente
"""

# ejercicio 2.3
print("\nejercicio 2.3\n")

edad = 25
tiene_licencia = True
tiene_multas = False

puede_conducir = edad <= 18 and tiene_licencia
print("Puede conducir:", puede_conducir)

necesita_curso = tiene_multas or not tiene_licencia
print("Necesita curso:", necesita_curso)
"""se evalua si una persona puede conducit 
o debe realizar un curso, dependiendo de la edad, 
si tiene o no licencia y multas
"""

#Parte 3
# ejercicio 3.1
print("\nejercicio 3.1\n")

print("Numeros del 1 al 10")
for i in range(1, 11):
    print(i)
"""se imprimen los numeros del 1 al 10, 
la funcion range genera una secuencia de numeros, 
el 11 no se incluye, el rango se detiene antes de llegar al 11
"""
print("\nnumeros pares del 1 al 20") 
print("-" * 15)

for i in range(2, 21):
    if i % 2 == 0:
        print(i)
"""
la misma logica del anterior pero pares del 1 al 20
en ambos casos se utiliza el ciclo for para iterar 
a traves de un rango de numeros y además en este 
se utiliza la condicion if para verificar si el 
numero es par (i % 2 == 0) antes de imprimirlo.
"""
#ejercicio 3.2
print("\nejercicio 3.2\n")

suma = 0
for i in range(1, 101):
    suma += i

print("La suma de los primeros 100 es", suma)
"""en escencia se utiliza lo mismo que en anteriores puntos
suma, funcion range y ciclo for, la suma es +=i que es una forma abreviada 
de escribir suma = suma + i y el rango de hasta 10 como Friedrich Gauss, 
en lugar de sumar se puede utiliza 50*101"""
suma_impares = 0
for i in range(1, 50):
    if i % 2 != 0:
        suma_impares += i
    
print("La suma de los numeros impares del 1 al 50 es", suma_impares)
"""lo mismo que antes pero con %2!=0 para saber que son impares"""

#ejercicio 3.3
print("\nejercicio 3.3\n")

numero = 7

print("tabla del", numero)
print("-" * 15)

for i in range(1, 11):
    resultado = numero * i
    print(numero, "x", i, "=", resultado)

print("-" * 15)

numero = 9

print("tabla del", numero)
print("-" * 15)
for i in range(1, 11):
    resultado = numero * i
    print(numero, "x", i, "=", resultado)

"""se imprime la tabla de multiplicar del numero asignado, se utiliza un ciclo for para iterar del 1 al 10 
"""