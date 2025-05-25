# Simulación de Memoria Caché e Interfaz E/S

Este proyecto implementa una simulación de memoria caché y mecanismos de E/S para un curso de Arquitectura de Computadores. El proyecto se centra en la implementación de dos componentes principales:

1. **Simulador de Memoria Caché**: Implementa caché de mapeo directo y asociativo por conjuntos (2-way).
2. **Simulador de Interfaz E/S**: Implementa E/S programada (polling) e interrupciones para la lectura de datos de un dispositivo ficticio (sensor de temperatura).

## Estructura del Proyecto

```
proyecto_arquitectura/
├── cache_simulator.py     # Simulador de memoria caché
├── io_simulator.py        # Simulador de interfaz E/S
├── cache_resultados.txt   # Resultados de las pruebas de caché
├── io_resultados.txt      # Resultados de las pruebas de E/S
└── README.md              # Este archivo
```

## Simulador de Memoria Caché

### Descripción

El simulador de memoria caché implementa dos tipos de organización:

1. **Caché de Mapeo Directo**: Cada bloque de memoria principal solo puede ubicarse en una única línea de caché específica.
2. **Caché Asociativa por Conjuntos (2-way)**: Cada bloque de memoria principal puede ubicarse en cualquiera de las dos vías dentro de un conjunto específico.

Ambas implementaciones son parametrizables en términos de tamaño de bloque y número de líneas/conjuntos.

### Esquema de Funcionamiento

```
                  +-------------------+
                  |    Dirección      |
                  +-------------------+
                           |
                           v
          +--------------------------------+
          |  Etiqueta  |  Índice  | Offset |
          +--------------------------------+
                  |          |         |
                  v          v         v
+----------------+    +-------------+   +------------+
| Comparar Tags  |<---| Seleccionar |   | Seleccionar|
+----------------+    | Línea/Conj. |   | Palabra    |
        |             +-------------+   +------------+
        v                    |                |
+----------------+           |                |
| ¿Coincidencia? |           |                |
+----------------+           |                |
   |        |                |                |
   | Sí     | No             |                |
   v        v                v                v
+-------+ +----------------+ +--------------------------------+
| Hit   | | Miss -> Cargar | | Retornar/Escribir Dato        |
+-------+ | desde Memoria  | +--------------------------------+
          +----------------+
```

### Características Principales

- **Parametrización**: Tamaño de bloque y número de líneas configurables.
- **Políticas de Reemplazo**: LRU (Least Recently Used) para caché asociativa.
- **Política de Escritura**: Write-through (escritura simultánea en caché y memoria principal).
- **Estadísticas**: Conteo de accesos, aciertos, fallos y cálculo de tasas.

### Uso

```python
# Crear instancias de caché
cache_directo = CacheMapeoDirecto(tamano_bloque=4, num_lineas=16, tamano_memoria=1024)
cache_asociativo = CacheAsociativaConjuntos(tamano_bloque=4, num_conjuntos=8, tamano_memoria=1024)

# Leer datos
dato = cache_directo.leer(direccion)
dato = cache_asociativo.leer(direccion)

# Escribir datos
cache_directo.escribir(direccion, dato)
cache_asociativo.escribir(direccion, dato)

# Obtener estadísticas
stats = cache_directo.obtener_estadisticas()
```

### Resultados de Pruebas

Se realizaron tres pruebas diferentes:

1. **Acceso Secuencial**: Acceso a 32 direcciones consecutivas.
2. **Acceso con Localidad Espacial**: Acceso a grupos de direcciones contiguas.
3. **Acceso Aleatorio**: Acceso a 100 direcciones aleatorias.

Resultados:

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
  Aciertos: 156
  Fallos: 94
  Tasa de aciertos: 62.40%
Resultados para asociativo por conjuntos:
  Accesos: 250
  Aciertos: 155
  Fallos: 95
  Tasa de aciertos: 62.00%

Ejemplo 3: Acceso aleatorio a 100 direcciones
Resultados para mapeo directo:
  Accesos: 100
  Aciertos: 4
  Fallos: 96
  Tasa de aciertos: 4.00%
Resultados para asociativo por conjuntos:
  Accesos: 100
  Aciertos: 7
  Fallos: 93
  Tasa de aciertos: 7.00%
```

### Análisis de Resultados

- **Acceso Secuencial**: Ambos tipos de caché muestran un rendimiento idéntico con una tasa de aciertos del 75%. Esto se debe a que, con un tamaño de bloque de 4 palabras, cada fallo carga 4 palabras consecutivas, lo que resulta en 3 aciertos posteriores.

- **Acceso con Localidad Espacial**: Ambos tipos de caché muestran un rendimiento similar (62.40% vs 62.00%). La localidad espacial beneficia a ambos tipos de caché ya que aprovechan la carga de bloques completos.

- **Acceso Aleatorio**: El rendimiento es bajo para ambos tipos de caché, pero la caché asociativa muestra una ligera ventaja (7.00% vs 4.00%) debido a su mayor flexibilidad en la ubicación de bloques.

## Simulador de Interfaz E/S

### Descripción

El simulador de interfaz E/S implementa dos mecanismos de E/S:

1. **E/S Programada (Polling)**: La CPU verifica periódicamente el estado de los dispositivos para determinar si están listos para transferir datos.
2. **E/S por Interrupciones**: Los dispositivos generan interrupciones cuando están listos para transferir datos, evitando que la CPU tenga que verificar constantemente.

Se simula un dispositivo ficticio (sensor de temperatura) para demostrar ambos mecanismos.

### Esquema de Funcionamiento

#### E/S Programada (Polling)

```
+-------+    1. Verificar estado    +-------------+
|       |------------------------>  |             |
|  CPU  |                           | Dispositivo |
|       | <------------------------  |             |
+-------+    2. Leer datos si       +-------------+
              está listo
```

#### E/S por Interrupciones

```
                   1. Solicitud de operación
+-------+       -------------------------->      +-------------+
|       |                                        |             |
|  CPU  |                                        | Dispositivo |
|       | <--------------------------            |             |
+-------+    2. Interrupción cuando             +-------------+
               hay datos disponibles
                  
                  3. Atender interrupción
              y procesar datos
```

### Características Principales

- **Dispositivo Simulado**: Sensor de temperatura que genera lecturas aleatorias.
- **Controladores**: Implementación de controladores para ambos mecanismos de E/S.
- **Multihilo**: Uso de hilos para simular operaciones concurrentes y generación de interrupciones.
- **Estadísticas**: Comparación de rendimiento entre ambos mecanismos.

### Uso

```python
# Crear y configurar la CPU
cpu = CPU()
cpu.configurar_dispositivos()

# Ejecutar E/S programada
cpu.ejecutar_es_programada(duracion=5.0)

# Ejecutar E/S por interrupciones
cpu.ejecutar_es_interrupciones(duracion=5.0)

# Mostrar estadísticas
cpu.mostrar_estadisticas()

# Detener la CPU y los dispositivos
cpu.detener()
```

### Resultados de Pruebas

Se realizaron pruebas de ambos mecanismos de E/S durante 5 segundos cada uno:

```
=== Iniciando E/S Programada ===
No hay datos disponibles en el dispositivo 'sensor_temp'
No hay datos disponibles en el dispositivo 'sensor_temp'
[Polling] Temperatura: 17.61°C
No hay datos disponibles en el dispositivo 'sensor_temp'
[Polling] Temperatura: 16.24°C
No hay datos disponibles en el dispositivo 'sensor_temp'
[Polling] Temperatura: 21.24°C
No hay datos disponibles en el dispositivo 'sensor_temp'
[Polling] Temperatura: 20.78°C
No hay datos disponibles en el dispositivo 'sensor_temp'
=== Fin de E/S Programada ===

=== Iniciando E/S por Interrupciones ===
CPU realizando otras tareas...
[Interrupción] Temperatura: 25.14°C
CPU realizando otras tareas...
[Interrupción] Temperatura: 25.47°C
CPU realizando otras tareas...
[Interrupción] Temperatura: 23.94°C
CPU realizando otras tareas...
[Interrupción] Temperatura: 18.01°C
CPU realizando otras tareas...
[Interrupción] Temperatura: 30.30°C
=== Fin de E/S por Interrupciones ===

=== Estadísticas de E/S ===
Lecturas obtenidas mediante E/S programada: 4
Lecturas obtenidas mediante E/S por interrupciones: 5
E/S programada - Temperatura mín: 16.24°C, máx: 21.24°C, promedio: 18.97°C
E/S interrupciones - Temperatura mín: 18.01°C, máx: 30.30°C, promedio: 24.57°C
```

### Análisis de Resultados

- **E/S Programada**: Se observa que la CPU debe verificar constantemente si hay datos disponibles, lo que resulta en mensajes de "No hay datos disponibles" cuando el dispositivo no está listo. Se obtuvieron 4 lecturas en 5 segundos.

- **E/S por Interrupciones**: La CPU puede realizar otras tareas mientras espera que el dispositivo genere interrupciones. Se obtuvieron 5 lecturas en 5 segundos, lo que muestra una mayor eficiencia en la obtención de datos.

- **Comparación**: La E/S por interrupciones es más eficiente ya que:
  1. Permite a la CPU realizar otras tareas mientras espera datos.
  2. Obtiene más lecturas en el mismo período de tiempo.
  3. No desperdicia ciclos verificando dispositivos que no están listos.

## Instrucciones de Ejecución

### Requisitos

- Python 3.6 o superior
- No se requieren bibliotecas adicionales

### Ejecución del Simulador de Caché

```bash
python3 cache_simulator.py
```

### Ejecución del Simulador de E/S

```bash
python3 io_simulator.py
```

## Conclusiones

1. **Memoria Caché**:
   - La caché asociativa por conjuntos muestra ventajas sobre la caché de mapeo directo en patrones de acceso aleatorio.
   - Ambos tipos de caché se benefician significativamente de la localidad espacial y temporal.
   - El tamaño de bloque adecuado es crucial para optimizar el rendimiento.

2. **Interfaz E/S**:
   - La E/S por interrupciones es más eficiente que la E/S programada en términos de utilización de CPU.
   - La E/S programada es más simple de implementar pero menos eficiente.
   - La elección del mecanismo de E/S depende del equilibrio entre simplicidad y eficiencia requerido.

Este proyecto demuestra conceptos fundamentales de arquitectura de computadores, específicamente en el ámbito de la jerarquía de memoria y los mecanismos de E/S, proporcionando una base sólida para comprender estos componentes críticos en sistemas computacionales modernos.
