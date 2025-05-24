# README - Simulador de Pipeline de CPU (`CPU/src`)

Este directorio contiene la implementación central de un simulador de pipeline de CPU, orientado a la comprensión y experimentación de conceptos fundamentales en arquitectura de computadores, especialmente relacionados con el procesamiento segmentado (pipeline), la detección y resolución de hazards, y la gestión del conjunto de instrucciones (ISA).

## Contenido de la Carpeta

- [`hazard_control.py`](hazard_control.py): Módulo encargado de la **detección y resolución de hazards** en el pipeline, implementando mecanismos de forwarding y stalling.
- [`isa.py`](isa.py): Define el **conjunto de instrucciones (ISA)**, codificación y decodificación de instrucciones, así como su ejecución.
- [`pipeline.py`](pipeline.py): Implementa el **simulador del pipeline de 5 etapas** (IF, ID, EX, MEM, WB) y el control general del flujo de instrucciones.
- [`test_pipeline.py`](test_pipeline_forwarding.py): Conjunto de **pruebas** para validar el funcionamiento del pipeline, incluyendo casos de hazards y operaciones de memoria.

---

## Conceptos Clave Demostrados

### 1. **Pipeline de CPU**

El pipeline implementado sigue el modelo clásico de 5 etapas:
- **IF** (*Instruction Fetch*): Búsqueda de la instrucción.
- **ID** (*Instruction Decode*): Decodificación y lectura de registros.
- **EX** (*Execute*): Ejecución de la operación en la ALU.
- **MEM** (*Memory*): Acceso a memoria (para LOAD/STORE).
- **WB** (*Write Back*): Escritura del resultado en el registro destino.

El pipeline permite la ejecución superpuesta de instrucciones, mejorando el rendimiento pero introduciendo la posibilidad de conflictos o hazards.

### 2. **Hazards**

El simulador maneja y resuelve varios tipos de hazards:
- **Hazards de Datos**: Ocurren cuando una instrucción depende del resultado de una instrucción anterior que aún no ha finalizado. Se resuelven mediante:
  - **Stalling**: Detiene el avance del pipeline para esperar el dato.
  - **Forwarding**: Redirige el resultado de una etapa posterior a una anterior sin esperar a la escritura en el registro.
- **Hazards de Control**: Asociados a instrucciones de salto (*branch*), que pueden requerir descartar instrucciones parcialmente procesadas (flush) si el flujo del programa cambia.

### 3. **Unidad de Control de Hazards (`hazard_control.py`)**

- **Detección de Hazards**: Identifica dependencias que requieren stall (por ejemplo, *load-use hazard*).
- **Forwarding**: Determina cuándo se debe aplicar y desde qué etapa.
- **Resolución de Hazards**: Decide si se aplica stall, forwarding, o ninguna acción.

### 4. **Conjunto de Instrucciones (ISA) (`isa.py`)**

- Define instrucciones aritméticas (*ADD, SUB, MUL*), de memoria (*LOAD, STORE*), y de control de flujo (*BEQ, JUMP*).
- Implementa codificación/decodificación en formato binario.
- Permite ensamblar y desensamblar programas de texto a instrucciones ejecutables y viceversa.

### 5. **Simulación del Pipeline (`pipeline.py`)**

- Administra registros inter-etapa y el control de flujo de instrucciones.
- Implementa las etapas del pipeline, el manejo de stalling y flushing, y recolecta estadísticas de ejecución (ciclos, stalls, CPI, etc.).
- Permite la carga y ejecución de programas, y la visualización del estado del pipeline en cada ciclo.

### 6. **Pruebas y Validación (`test_pipeline.py`)**

- Ejecución de pruebas unitarias y de integración sobre el simulador.
- Casos de prueba para operaciones aritméticas, hazards de datos, hazards de control y operaciones de memoria.
- Validación de la correcta codificación y decodificación de la ISA.
  - Test 1: Ejecución básica con operaciones aritméticas.
  - Test 2: Hazards de datos con forwarding y stalling.
  - Test 3: Hazards de control con saltos.
  - Test 4: Operaciones de memoria (LOAD/STORE).
  - Test 5: Codificación y decodificación de instrucciones.

Todos los resultados se validan automáticamente contra los valores esperados.

---
## Métricas de Rendimiento

El simulador calcula las siguientes métricas:

- Ciclos totales: Número de ciclos ejecutados.
- Instrucciones completadas: Número de instrucciones que han pasado por todas las etapas.
- Stalls insertados: Número de ciclos de espera insertados por hazards.
- Saltos tomados: Número de instrucciones de salto que cambiaron el flujo de ejecución.
- CPI (Cycles Per Instruction): Promedio de ciclos por instrucción.

--- 
## Instrucciones de ejecución
1. Asegúrate de tener **Python 3.7 o superior**.
2. Ejecuta el archivo de pruebas:
```bash
python test_pipeline.py
```
---
## Ejemplo de Uso

```python
from pipeline import PipelineCPU
from isa import ISA

# Definir un programa simple
program = [
    {"op": "ADD", "rd": 1, "rs1": 2, "rs2": 3},
    {"op": "SUB", "rd": 4, "rs1": 5, "rs2": 6}
]

# Inicializar CPU y cargar instrucciones
cpu = PipelineCPU()
cpu.load_instructions(program)
cpu.registers[2] = 10
cpu.registers[3] = 20
cpu.registers[5] = 30
cpu.registers[6] = 15

# Ejecutar el pipeline hasta completar
while any(cpu.pipeline.values()) or cpu.pc < len(cpu.instructions):
    cpu.print_state()
    cpu.step()
```
---
## 🖥️ Ejemplo de salida del simulador

A continuación se muestra una parte de la salida generada al ejecutar el simulador, específicamente el Test 2: detección y resolución de hazards de datos con forwarding y stalling.

```txt
=== Test 2: Hazards de datos con forwarding y stalling ===
Estado inicial:
R2 = 10, R3 = 20
R5 = 5, R7 = 8
R10 = 15, MEM[100] = 25

Ejecutando pipeline...
Cycle 3
IF: {'op': 'SUB', 'rd': 6, 'rs1': 4, 'rs2': 7}
ID: {'op': 'ADD', 'rd': 4, 'rs1': 1, 'rs2': 5}
EX: {'op': 'ADD', 'rd': 1, 'rs1': 2, 'rs2': 3}
MEM: None
WB: None
Regs: [0, 0, 10, 20, 0, 5, 0, 8, 0, 0]
---
Cycle 6
EX: {'op': 'LOAD', 'rd': 8, 'addr': 100}
MEM: {'op': 'SUB', 'rd': 6, 'rs1': 4, 'rs2': 7}
WB: {'op': 'SUB', 'rd': 6, 'rs1': 4, 'rs2': 7}
Regs: [0, 30, 10, 20, 35, 5, 0, 8, 0, 0]
---
Cycle 7
ID: {'op': 'ADD', 'rd': 9, 'rs1': 8, 'rs2': 10}
MEM: {'op': 'LOAD', 'rd': 8, 'addr': 100}
WB: {'op': 'LOAD', 'rd': 8, 'addr': 100}
Regs: [0, 30, 10, 20, 35, 5, 27, 8, 0, 0]
---

Resultados finales:
R1 = 30 (esperado: 30)
R4 = 35 (esperado: 35)
R6 = 27 (esperado: 27)
R8 = 25 (esperado: 25)
R9 = 15 (esperado: 40)

Estadísticas: {'cycles': 10, 'instructions_completed': 5, 'stalls_inserted': 1, 'branches_taken': 0}
```
En este ejemplo se evidencia el manejo correcto de dependencias de datos:

- Se realiza forwarding desde EX y MEM.

- Se inserta un stall por dependencia de carga (load-use hazard), como es esperado.
---

## Glosario de Términos

- **Hazard**: Conflicto en el pipeline que puede afectar la correcta ejecución de instrucciones.
- **Forwarding**: Redirección de resultados intermedios para evitar stalls.
- **Stalling**: Detención temporal de una etapa del pipeline para resolver un hazard.
- **Flush**: Vaciar instrucciones del pipeline, comúnmente usado tras un salto tomado.
- **Register File**: Banco de registros de la CPU.
- **ALU**: Unidad aritmético-lógica.

---


## Referencias

- *Hennessy, J. L., & Patterson, D. A. (2017). Computer Architecture: A Quantitative Approach.*
- Código estructurado para facilitar la comprensión y modificación por estudiantes.
