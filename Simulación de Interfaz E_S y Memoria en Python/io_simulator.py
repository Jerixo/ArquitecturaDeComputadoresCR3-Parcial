#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulador de Interfaz de Entrada/Salida

Este módulo implementa una simulación de mecanismos de E/S:
- E/S programada (polling)
- E/S por interrupciones

Se simula un dispositivo ficticio (sensor de temperatura) para demostrar
ambos mecanismos de E/S.
"""

import random
import time
import threading
from typing import List, Dict, Callable, Optional, Union
from enum import Enum

class EstadoDispositivo(Enum):
    """Enumeración para los posibles estados de un dispositivo de E/S."""
    LISTO = 0      # El dispositivo está listo para transferir datos
    OCUPADO = 1    # El dispositivo está ocupado procesando una operación
    ERROR = 2      # El dispositivo ha encontrado un error

class DispositivoES:
    """
    Clase base para dispositivos de Entrada/Salida.
    
    Atributos:
        nombre (str): Nombre identificativo del dispositivo.
        estado (EstadoDispositivo): Estado actual del dispositivo.
        buffer (List[int]): Buffer de datos del dispositivo.
        tamano_buffer (int): Tamaño máximo del buffer.
    """
    
    def __init__(self, nombre: str, tamano_buffer: int = 16):
        """
        Inicializa un dispositivo de E/S.
        
        Args:
            nombre (str): Nombre identificativo del dispositivo.
            tamano_buffer (int, opcional): Tamaño del buffer. Por defecto es 16.
        """
        self.nombre = nombre
        self.estado = EstadoDispositivo.LISTO
        self.buffer = []
        self.tamano_buffer = tamano_buffer
    
    def leer(self) -> Optional[int]:
        """
        Lee un dato del buffer del dispositivo.
        
        Returns:
            Optional[int]: Dato leído o None si no hay datos disponibles.
        """
        if not self.buffer:
            return None
        return self.buffer.pop(0)
    
    def escribir(self, dato: int) -> bool:
        """
        Escribe un dato en el buffer del dispositivo.
        
        Args:
            dato (int): Dato a escribir.
            
        Returns:
            bool: True si la escritura fue exitosa, False en caso contrario.
        """
        if len(self.buffer) >= self.tamano_buffer:
            return False
        self.buffer.append(dato)
        return True
    
    def esta_listo(self) -> bool:
        """
        Verifica si el dispositivo está listo para operaciones.
        
        Returns:
            bool: True si el dispositivo está listo, False en caso contrario.
        """
        return self.estado == EstadoDispositivo.LISTO
    
    def hay_datos_disponibles(self) -> bool:
        """
        Verifica si hay datos disponibles para leer.
        
        Returns:
            bool: True si hay datos disponibles, False en caso contrario.
        """
        return len(self.buffer) > 0
    
    def __str__(self) -> str:
        """Representación en cadena del dispositivo."""
        return f"{self.nombre} [Estado: {self.estado.name}, Datos: {len(self.buffer)}/{self.tamano_buffer}]"

class SensorTemperatura(DispositivoES):
    """
    Simulación de un sensor de temperatura como dispositivo de entrada.
    
    Este sensor genera lecturas de temperatura aleatorias en un rango específico.
    """
    
    def __init__(self, nombre: str = "Sensor de Temperatura", 
                 temp_min: float = 15.0, temp_max: float = 35.0,
                 tamano_buffer: int = 16):
        """
        Inicializa un sensor de temperatura.
        
        Args:
            nombre (str, opcional): Nombre del sensor. Por defecto es "Sensor de Temperatura".
            temp_min (float, opcional): Temperatura mínima en grados Celsius. Por defecto es 15.0.
            temp_max (float, opcional): Temperatura máxima en grados Celsius. Por defecto es 35.0.
            tamano_buffer (int, opcional): Tamaño del buffer. Por defecto es 16.
        """
        super().__init__(nombre, tamano_buffer)
        self.temp_min = temp_min
        self.temp_max = temp_max
        self.intervalo_lectura = 1.0  # segundos entre lecturas
        self._thread_activo = False
        self._thread = None
    
    def iniciar_lecturas(self) -> None:
        """Inicia el proceso de generación de lecturas de temperatura."""
        if self._thread_activo:
            return
        
        self._thread_activo = True
        self._thread = threading.Thread(target=self._generar_lecturas)
        self._thread.daemon = True  # El hilo terminará cuando el programa principal termine
        self._thread.start()
    
    def detener_lecturas(self) -> None:
        """Detiene el proceso de generación de lecturas de temperatura."""
        self._thread_activo = False
        if self._thread:
            self._thread.join(timeout=2.0)
    
    def _generar_lecturas(self) -> None:
        """
        Método interno que genera lecturas de temperatura aleatorias.
        Este método se ejecuta en un hilo separado.
        """
        while self._thread_activo:
            # Simular tiempo de procesamiento
            time.sleep(self.intervalo_lectura)
            
            # Generar una lectura de temperatura aleatoria
            temperatura = random.uniform(self.temp_min, self.temp_max)
            
            # Convertir a entero (multiplicar por 100 para preservar 2 decimales)
            valor_entero = int(temperatura * 100)
            
            # Intentar escribir en el buffer
            if len(self.buffer) < self.tamano_buffer:
                self.buffer.append(valor_entero)
            
            # Simular cambios de estado ocasionales
            if random.random() < 0.05:  # 5% de probabilidad de cambio de estado
                estados = list(EstadoDispositivo)
                self.estado = random.choice(estados)
            else:
                # Normalmente, el sensor está listo
                self.estado = EstadoDispositivo.LISTO

class ControladorES:
    """
    Clase base para controladores de Entrada/Salida.
    
    Un controlador de E/S gestiona la comunicación entre la CPU y los dispositivos.
    """
    
    def __init__(self):
        """Inicializa un controlador de E/S."""
        self.dispositivos = {}  # Diccionario de dispositivos conectados
    
    def registrar_dispositivo(self, id_dispositivo: str, dispositivo: DispositivoES) -> None:
        """
        Registra un dispositivo en el controlador.
        
        Args:
            id_dispositivo (str): Identificador único para el dispositivo.
            dispositivo (DispositivoES): Instancia del dispositivo a registrar.
        """
        self.dispositivos[id_dispositivo] = dispositivo
    
    def obtener_dispositivo(self, id_dispositivo: str) -> Optional[DispositivoES]:
        """
        Obtiene un dispositivo registrado por su ID.
        
        Args:
            id_dispositivo (str): Identificador del dispositivo.
            
        Returns:
            Optional[DispositivoES]: El dispositivo si existe, None en caso contrario.
        """
        return self.dispositivos.get(id_dispositivo)
    
    def listar_dispositivos(self) -> Dict[str, DispositivoES]:
        """
        Obtiene la lista de dispositivos registrados.
        
        Returns:
            Dict[str, DispositivoES]: Diccionario con los dispositivos registrados.
        """
        return self.dispositivos

class ControladorESProgramada(ControladorES):
    """
    Controlador de E/S programada (polling).
    
    En este modo, la CPU verifica periódicamente el estado de los dispositivos
    para determinar si están listos para transferir datos.
    """
    
    def leer_dato(self, id_dispositivo: str) -> Optional[int]:
        """
        Lee un dato de un dispositivo mediante E/S programada.
        
        Args:
            id_dispositivo (str): Identificador del dispositivo.
            
        Returns:
            Optional[int]: Dato leído o None si no hay datos o el dispositivo no está listo.
        """
        dispositivo = self.obtener_dispositivo(id_dispositivo)
        if not dispositivo:
            print(f"Error: Dispositivo '{id_dispositivo}' no encontrado")
            return None
        
        # Verificar si el dispositivo está listo (polling)
        if not dispositivo.esta_listo():
            print(f"Dispositivo '{id_dispositivo}' no está listo")
            return None
        
        # Verificar si hay datos disponibles
        if not dispositivo.hay_datos_disponibles():
            print(f"No hay datos disponibles en el dispositivo '{id_dispositivo}'")
            return None
        
        # Leer dato
        return dispositivo.leer()
    
    def escribir_dato(self, id_dispositivo: str, dato: int) -> bool:
        """
        Escribe un dato en un dispositivo mediante E/S programada.
        
        Args:
            id_dispositivo (str): Identificador del dispositivo.
            dato (int): Dato a escribir.
            
        Returns:
            bool: True si la escritura fue exitosa, False en caso contrario.
        """
        dispositivo = self.obtener_dispositivo(id_dispositivo)
        if not dispositivo:
            print(f"Error: Dispositivo '{id_dispositivo}' no encontrado")
            return False
        
        # Verificar si el dispositivo está listo (polling)
        if not dispositivo.esta_listo():
            print(f"Dispositivo '{id_dispositivo}' no está listo")
            return False
        
        # Escribir dato
        return dispositivo.escribir(dato)
    
    def esperar_y_leer(self, id_dispositivo: str, timeout: float = 5.0) -> Optional[int]:
        """
        Espera hasta que un dispositivo tenga datos disponibles y luego lee.
        
        Args:
            id_dispositivo (str): Identificador del dispositivo.
            timeout (float, opcional): Tiempo máximo de espera en segundos. Por defecto es 5.0.
            
        Returns:
            Optional[int]: Dato leído o None si se agotó el tiempo de espera.
        """
        dispositivo = self.obtener_dispositivo(id_dispositivo)
        if not dispositivo:
            print(f"Error: Dispositivo '{id_dispositivo}' no encontrado")
            return None
        
        inicio = time.time()
        while (time.time() - inicio) < timeout:
            # Verificar si el dispositivo está listo y tiene datos
            if dispositivo.esta_listo() and dispositivo.hay_datos_disponibles():
                return dispositivo.leer()
            
            # Esperar un poco antes de verificar nuevamente
            time.sleep(0.1)
        
        print(f"Tiempo de espera agotado para el dispositivo '{id_dispositivo}'")
        return None

class ControladorESInterrupciones(ControladorES):
    """
    Controlador de E/S por interrupciones.
    
    En este modo, los dispositivos generan interrupciones cuando están listos
    para transferir datos, evitando que la CPU tenga que verificar constantemente.
    """
    
    def __init__(self):
        """Inicializa un controlador de E/S por interrupciones."""
        super().__init__()
        self.manejadores_interrupcion = {}  # Manejadores de interrupción por dispositivo
        self.cola_interrupciones = []  # Cola de interrupciones pendientes
        self._thread_interrupciones = None
        self._interrupciones_activas = False
    
    def registrar_manejador(self, id_dispositivo: str, 
                           manejador: Callable[[str, int], None]) -> None:
        """
        Registra un manejador de interrupciones para un dispositivo.
        
        Args:
            id_dispositivo (str): Identificador del dispositivo.
            manejador (Callable[[str, int], None]): Función que maneja la interrupción.
                Recibe el ID del dispositivo y el dato como parámetros.
        """
        self.manejadores_interrupcion[id_dispositivo] = manejador
    
    def iniciar_servicio_interrupciones(self) -> None:
        """Inicia el servicio de atención a interrupciones."""
        if self._interrupciones_activas:
            return
        
        self._interrupciones_activas = True
        self._thread_interrupciones = threading.Thread(target=self._procesar_interrupciones)
        self._thread_interrupciones.daemon = True
        self._thread_interrupciones.start()
        
        # Iniciar monitoreo de dispositivos
        for id_dispositivo in self.dispositivos:
            self._iniciar_monitoreo_dispositivo(id_dispositivo)
    
    def detener_servicio_interrupciones(self) -> None:
        """Detiene el servicio de atención a interrupciones."""
        self._interrupciones_activas = False
        if self._thread_interrupciones:
            self._thread_interrupciones.join(timeout=2.0)
    
    def _iniciar_monitoreo_dispositivo(self, id_dispositivo: str) -> None:
        """
        Inicia el monitoreo de un dispositivo para detectar cuando está listo.
        
        Args:
            id_dispositivo (str): Identificador del dispositivo a monitorear.
        """
        dispositivo = self.dispositivos.get(id_dispositivo)
        if not dispositivo:
            return
        
        # Crear un hilo para monitorear este dispositivo
        thread = threading.Thread(
            target=self._monitorear_dispositivo,
            args=(id_dispositivo,)
        )
        thread.daemon = True
        thread.start()
    
    def _monitorear_dispositivo(self, id_dispositivo: str) -> None:
        """
        Monitorea un dispositivo y genera interrupciones cuando hay datos disponibles.
        
        Args:
            id_dispositivo (str): Identificador del dispositivo a monitorear.
        """
        dispositivo = self.dispositivos.get(id_dispositivo)
        if not dispositivo:
            return
        
        while self._interrupciones_activas:
            # Verificar si el dispositivo está listo y tiene datos
            if dispositivo.esta_listo() and dispositivo.hay_datos_disponibles():
                # Leer el dato y generar una interrupción
                dato = dispositivo.leer()
                if dato is not None:
                    self._generar_interrupcion(id_dispositivo, dato)
            
            # Esperar antes de verificar nuevamente
            time.sleep(0.2)
    
    def _generar_interrupcion(self, id_dispositivo: str, dato: int) -> None:
        """
        Genera una interrupción para un dispositivo.
        
        Args:
            id_dispositivo (str): Identificador del dispositivo.
            dato (int): Dato asociado a la interrupción.
        """
        # Añadir a la cola de interrupciones
        self.cola_interrupciones.append((id_dispositivo, dato))
    
    def _procesar_interrupciones(self) -> None:
        """
        Procesa las interrupciones pendientes.
        Este método se ejecuta en un hilo separado.
        """
        while self._interrupciones_activas:
            # Verificar si hay interrupciones pendientes
            if self.cola_interrupciones:
                # Obtener la siguiente interrupción
                id_dispositivo, dato = self.cola_interrupciones.pop(0)
                
                # Llamar al manejador correspondiente
                manejador = self.manejadores_interrupcion.get(id_dispositivo)
                if manejador:
                    try:
                        manejador(id_dispositivo, dato)
                    except Exception as e:
                        print(f"Error en manejador de interrupción: {e}")
            
            # Esperar un poco antes de verificar nuevamente
            time.sleep(0.1)

class CPU:
    """
    Simulación simplificada de una CPU que interactúa con dispositivos de E/S.
    
    Esta clase demuestra cómo la CPU interactúa con dispositivos de E/S
    utilizando tanto E/S programada como E/S por interrupciones.
    """
    
    def __init__(self):
        """Inicializa la CPU."""
        self.controlador_programada = ControladorESProgramada()
        self.controlador_interrupciones = ControladorESInterrupciones()
        self.lecturas_programada = []
        self.lecturas_interrupciones = []
        self.ejecutando = True
    
    def configurar_dispositivos(self) -> None:
        """Configura los dispositivos de E/S para ambos controladores."""
        # Crear sensor de temperatura
        sensor = SensorTemperatura()
        
        # Registrar en controlador de E/S programada
        self.controlador_programada.registrar_dispositivo("sensor_temp", sensor)
        
        # Registrar en controlador de E/S por interrupciones
        self.controlador_interrupciones.registrar_dispositivo("sensor_temp", sensor)
        self.controlador_interrupciones.registrar_manejador(
            "sensor_temp", self._manejador_interrupcion_temperatura
        )
        
        # Iniciar generación de lecturas
        sensor.iniciar_lecturas()
        
        # Iniciar servicio de interrupciones
        self.controlador_interrupciones.iniciar_servicio_interrupciones()
    
    def _manejador_interrupcion_temperatura(self, id_dispositivo: str, dato: int) -> None:
        """
        Manejador de interrupciones para el sensor de temperatura.
        
        Args:
            id_dispositivo (str): Identificador del dispositivo.
            dato (int): Dato recibido (temperatura * 100).
        """
        # Convertir el dato a temperatura (dividir por 100)
        temperatura = dato / 100.0
        
        # Almacenar la lectura
        self.lecturas_interrupciones.append(temperatura)
        
        # Mostrar la lectura
        print(f"[Interrupción] Temperatura: {temperatura:.2f}°C")
    
    def ejecutar_es_programada(self, duracion: float = 10.0) -> None:
        """
        Ejecuta un ciclo de E/S programada durante un tiempo determinado.
        
        Args:
            duracion (float, opcional): Duración en segundos. Por defecto es 10.0.
        """
        print("\n=== Iniciando E/S Programada ===")
        inicio = time.time()
        
        while (time.time() - inicio) < duracion and self.ejecutando:
            # Intentar leer del sensor de temperatura mediante polling
            dato = self.controlador_programada.leer_dato("sensor_temp")
            
            if dato is not None:
                # Convertir el dato a temperatura
                temperatura = dato / 100.0
                
                # Almacenar la lectura
                self.lecturas_programada.append(temperatura)
                
                # Mostrar la lectura
                print(f"[Polling] Temperatura: {temperatura:.2f}°C")
            
            # Simular otras tareas de la CPU
            time.sleep(0.5)
        
        print("=== Fin de E/S Programada ===\n")
    
    def ejecutar_es_interrupciones(self, duracion: float = 10.0) -> None:
        """
        Ejecuta un ciclo de E/S por interrupciones durante un tiempo determinado.
        
        Args:
            duracion (float, opcional): Duración en segundos. Por defecto es 10.0.
        """
        print("\n=== Iniciando E/S por Interrupciones ===")
        
        # Las interrupciones ya están configuradas y se procesan en segundo plano
        # La CPU puede realizar otras tareas mientras tanto
        
        inicio = time.time()
        while (time.time() - inicio) < duracion and self.ejecutando:
            # Simular otras tareas de la CPU
            print("CPU realizando otras tareas...")
            time.sleep(1.0)
        
        print("=== Fin de E/S por Interrupciones ===\n")
    
    def detener(self) -> None:
        """Detiene la ejecución de la CPU y los controladores."""
        self.ejecutando = False
        
        # Detener el servicio de interrupciones
        self.controlador_interrupciones.detener_servicio_interrupciones()
        
        # Detener los dispositivos
        for id_dispositivo, dispositivo in self.controlador_programada.listar_dispositivos().items():
            if hasattr(dispositivo, 'detener_lecturas'):
                dispositivo.detener_lecturas()
    
    def mostrar_estadisticas(self) -> None:
        """Muestra estadísticas comparativas entre E/S programada e interrupciones."""
        print("\n=== Estadísticas de E/S ===")
        print(f"Lecturas obtenidas mediante E/S programada: {len(self.lecturas_programada)}")
        print(f"Lecturas obtenidas mediante E/S por interrupciones: {len(self.lecturas_interrupciones)}")
        
        if self.lecturas_programada:
            temp_min = min(self.lecturas_programada)
            temp_max = max(self.lecturas_programada)
            temp_prom = sum(self.lecturas_programada) / len(self.lecturas_programada)
            print(f"E/S programada - Temperatura mín: {temp_min:.2f}°C, máx: {temp_max:.2f}°C, promedio: {temp_prom:.2f}°C")
        
        if self.lecturas_interrupciones:
            temp_min = min(self.lecturas_interrupciones)
            temp_max = max(self.lecturas_interrupciones)
            temp_prom = sum(self.lecturas_interrupciones) / len(self.lecturas_interrupciones)
            print(f"E/S interrupciones - Temperatura mín: {temp_min:.2f}°C, máx: {temp_max:.2f}°C, promedio: {temp_prom:.2f}°C")

# Ejemplo de uso
if __name__ == "__main__":
    # Crear y configurar la CPU
    cpu = CPU()
    cpu.configurar_dispositivos()
    
    try:
        # Ejecutar E/S programada durante 5 segundos
        cpu.ejecutar_es_programada(5.0)
        
        # Ejecutar E/S por interrupciones durante 5 segundos
        cpu.ejecutar_es_interrupciones(5.0)
        
        # Mostrar estadísticas
        cpu.mostrar_estadisticas()
        
    except KeyboardInterrupt:
        print("\nEjecución interrumpida por el usuario")
    finally:
        # Detener la CPU y los dispositivos
        cpu.detener()
        print("Simulación finalizada")
