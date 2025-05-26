# ArquitecturaDeComputadoresCR3-Parcial

# Proyecto Final 
Este proyecto reúne dos simuladores diseñados con el fin para entender conceptos clave de la arquitectura de computadores: un simulador de pipeline de CPU de 5 etapas y un simulador combinado de memoria caché y de interfaz E/S. Ambos fueron desarrollados en Python y permiten visualizar el comportamiento interno de estas unidades fundamentales, así como recolectar métricas para su análisis y comparación.

# Objetivo General
Diseñar, implementar y analizar simuladores educativos que representen el funcionamiento de diferentes componentes de una arquitectura de computador (CPU con pipeline, memoria caché y E/S), facilitando la comprensión de sus procesos internos, rendimiento e interacción.

# Objetivos Específicos

* Simular el pipeline clásico de 5 etapas de una CPU, incluyendo la gestión de hazards mediante forwarding y stalling.

* Modelar una memoria caché configurable que permita observar el impacto de diferentes políticas de reemplazo y tipos de acceso.

* Comparar el rendimiento de E/S programada (polling) frente a E/S por interrupciones en una situación controlada.

* Presentar resultados medibles como CPI, tasa de aciertos, tiempo de respuesta, entre otros.

* Documentar todo el proyecto con instrucciones claras, pruebas de ejecución, comentarios explicativos y análisis de resultados.

# Estructura del Proyecto
```
proyecto_arquitectura/
│
├── CPU/
│   └── src/
│       ├── pipeline.py
│       ├── isa.py
│       ├── hazard_control.py
│       ├── test_pipeline.py
│       └── diagramas/
│
├── Memoria_E_S/
│   ├── cache_simulator.py
│   ├── io_simulator.py
│   ├── cache_resultados.txt
│   ├── io_resultados.txt
│
├── README.md  
└── Informe_Tecnico.docx  
```
# Instrucciones de Ejecución
Asegúrate de tener Python 3 instalado. Desde terminal, navega a la carpeta del simulador que deseas probar y ejecuta los archivos según el caso:

Simulador de CPU con Pipeline
```
cd CPU/src
python test_pipeline.py
Simulador de Memoria Caché
```
```
cd Memoria_E_S
python cache_simulator.py
Simulador de Interfaz E/S
```
```
cd Memoria_E_S
python io_simulator.py
```
# ¿Qué hace cada simulador?
* Simulador de Pipeline de CPU

* Implementa las 5 etapas clásicas: IF, ID, EX, MEM, WB.

* Detecta y resuelve hazards de datos (mediante forwarding y stalling) y de control (mediante flush).

* Usa un conjunto de instrucciones (ISA) definido con operaciones aritméticas, de memoria y de control de flujo.

* Permite observar el avance de cada instrucción en el pipeline ciclo por ciclo.

* Genera métricas como número de ciclos, instrucciones ejecutadas, ciclos de stall y CPI.

# Estructura:

* simulador_pipeline/
*├── pipeline.py # Núcleo del simulador de pipeline
*├── hazard_control.py # Lógica para detectar y manejar hazards
*├── isa.py # Definición de operaciones (ISA simulada)
*└── test_pipeline.py # Archivo con pruebas de simulación

# Ejemplo de instrucciones cargadas:

```
Instrucciones originales:
0: ADD R1, R2, R3
1: SUB R4, R5, R6
2: MUL R7, R8, R9
3: LOAD R10, 100
4: STORE R11, 200
5: BEQ R12, R13, 5
6: JUMP 10
```
# Resultado esperado :

```
Instrucción: ADD R1, R2, R3
Codificada: 0x00430800

Instrucción: SUB R4, R5, R6
Codificada: 0x04a62000

Instrucción: MUL R7, R8, R9
Codificada: 0x09093800

Instrucción: LOAD R10, 100
Codificada: 0x0c0a0064

Instrucción: STORE R11, 200
Codificada: 0x116000c8

Instrucción: BEQ R12, R13, 5
Codificada: 0x158d0005

Instrucción: JUMP 10
Codificada: 0x1800000a

Instrucciones decodificadas:
0: ADD R1, R2, R3
1: SUB R4, R5, R6
2: MUL R7, R8, R9
3: LOAD R10, 100
4: STORE R11, 200
5: BEQ R12, R13, 5
6: JUMP 10
```
# Simulador de Memoria Caché

* Soporta mapeo directo y asociativa por conjuntos (2-way).

* Aplica política LRU para reemplazo y write-through para escrituras.

* Configurable en tamaño de bloque, líneas y memoria.

* Mide accesos, aciertos, fallos y tasa de aciertos.

# Ejemplo de salida:

```
=== Simulación de Caché ===
Tamaño de bloque: 4 palabras
Caché de mapeo directo: 16 líneas
Caché asociativa por conjuntos: 8 conjuntos (2-way = 16 líneas)

Ejemplo 1: Acceso secuencial a 32 direcciones
Resultados para mapeo directo:
  Accesos: 32
  Aciertos: 24
  Fallos: 8
  Tasa de aciertos: 75.00%
Resultados para asociativo por conjuntos:
  Accesos: 32
  Aciertos: 24
  Fallos: 8
  Tasa de aciertos: 75.00%

Ejemplo 2: Acceso con localidad espacial
Resultados para mapeo directo:
  Accesos: 250
  Aciertos: 150
  Fallos: 100
  Tasa de aciertos: 60.00%
Resultados para asociativo por conjuntos:
  Accesos: 250
  Aciertos: 153
  Fallos: 97
  Tasa de aciertos: 61.20%

Ejemplo 3: Acceso aleatorio a 100 direcciones
Resultados para mapeo directo:
  Accesos: 100
  Aciertos: 5
  Fallos: 95
  Tasa de aciertos: 5.00%
Resultados para asociativo por conjuntos:
  Accesos: 100
  Aciertos: 5
  Fallos: 95
  Tasa de aciertos: 5.00%
```
# Simulador de E/S

Usa un sensor de temperatura que genera datos.

Mide el tiempo promedio de respuesta en cada modo.

# Resultado esperado:

```
=== Iniciando E/S Programada ===
No hay datos disponibles en el dispositivo 'sensor_temp'
No hay datos disponibles en el dispositivo 'sensor_temp'
[Polling] Temperatura: 26.22°C
No hay datos disponibles en el dispositivo 'sensor_temp'
[Polling] Temperatura: 29.70°C
No hay datos disponibles en el dispositivo 'sensor_temp'
[Polling] Temperatura: 21.65°C
No hay datos disponibles en el dispositivo 'sensor_temp'
Dispositivo 'sensor_temp' no está listo
Dispositivo 'sensor_temp' no está listo
=== Fin de E/S Programada ===


=== Iniciando E/S por Interrupciones ===
CPU realizando otras tareas...
[Interrupción] Temperatura: 26.83°C
[Interrupción] Temperatura: 23.38°C
CPU realizando otras tareas...
[Interrupción] Temperatura: 22.50°C
CPU realizando otras tareas...
[Interrupción] Temperatura: 30.22°C
CPU realizando otras tareas...
[Interrupción] Temperatura: 25.30°C
CPU realizando otras tareas...
[Interrupción] Temperatura: 30.51°C
=== Fin de E/S por Interrupciones ===


=== Estadísticas de E/S ===
Lecturas obtenidas mediante E/S programada: 3
Lecturas obtenidas mediante E/S por interrupciones: 6
E/S programada - Temperatura mín: 21.65°C, máx: 29.70°C, promedio: 25.86°C
E/S interrupciones - Temperatura mín: 22.50°C, máx: 30.51°C, promedio: 26.46°C
Simulación finalizada
```
# Resultados Generales
Módulo	Métrica Principal	Resultado (Ejemplo)
```
CPU (Pipeline)	CPI	2.0
Memoria Caché	Tasa de Aciertos	75%
Interfaz E/S	Tiempo de respuesta	2 ms (interrupciones)
```
Los resultados pueden variar dependiendo del programa o configuración utilizada.

# Conclusiones
El pipeline mejora el rendimiento al permitir ejecutar varias instrucciones en paralelo, aunque puede verse afectado por hazards si no se gestionan correctamente.

La memoria caché mejora los tiempos de acceso cuando hay buena localidad. La política de reemplazo y el tipo de acceso influyen fuertemente en la tasa de aciertos.

La interfaz por interrupciones es más eficiente que el polling en cuanto a tiempo de respuesta, ya que evita la espera activa de la CPU.

