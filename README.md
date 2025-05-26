# ArquitecturaDeComputadoresCR3-Parcial

# Proyecto Final 
Este proyecto reúne dos simuladores diseñados con el fin para entender conceptos clave de la arquitectura de computadores: un simulador de pipeline de CPU de 5 etapas y un simulador combinado de memoria caché y de interfaz E/S. Ambos fueron desarrollados en Python y permiten visualizar el comportamiento interno de estas unidades fundamentales, así como recolectar métricas para su análisis y comparación.

# Objetivo General
Diseñar, implementar y analizar simuladores educativos que representen el funcionamiento de diferentes componentes de una arquitectura de computador (CPU con pipeline, memoria caché y E/S), facilitando la comprensión de sus procesos internos, rendimiento e interacción.

# Objetivos Específicos
Simular el pipeline clásico de 5 etapas de una CPU, incluyendo la gestión de hazards mediante forwarding y stalling.

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
├── README.md  ← (este archivo)
└── Informe_Tecnico.docx  ← (documento detallado con análisis)
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
Implementa las 5 etapas clásicas: IF, ID, EX, MEM, WB.

Detecta y resuelve hazards de datos (mediante forwarding y stalling) y de control (mediante flush).

Usa un conjunto de instrucciones (ISA) definido con operaciones aritméticas, de memoria y de control de flujo.

Permite observar el avance de cada instrucción en el pipeline ciclo por ciclo.

Genera métricas como número de ciclos, instrucciones ejecutadas, ciclos de stall y CPI.

# Ejemplo de instrucciones cargadas:

```
programa = [
    {"op": "ADD", "rd": 1, "rs1": 2, "rs2": 3},
    {"op": "SUB", "rd": 4, "rs1": 5, "rs2": 6}
]
```
# Resultado esperado (resumen):

```
Cycle 1: IF → ADD
Cycle 2: ID → ADD, IF → SUB
...
R1 = 30
R4 = 35
CPI = 2.0
```
# Simulador de Memoria Caché
Soporta mapeo directo y asociativa por conjuntos (2-way).

Aplica política LRU para reemplazo y write-through para escrituras.

Configurable en tamaño de bloque, líneas y memoria.

Mide accesos, aciertos, fallos y tasa de aciertos.

# Ejemplo de salida:

```
Caché de mapeo directo:
  Accesos: 32
  Aciertos: 24
  Fallos: 8
  Tasa de acierto: 75%
```
# Simulador de E/S
Compara polling vs interrupciones en un entorno simulado.

Usa un sensor de temperatura que genera datos.

Mide el tiempo promedio de respuesta en cada modo.

# Resultado esperado:

```
Modo polling:
  Tiempo de respuesta promedio: 5 ms
Modo interrupciones:
  Tiempo de respuesta promedio: 2 ms
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

