#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Simulador de Memoria Caché

Este módulo implementa una simulación de memoria caché con dos tipos de mapeo:
- Mapeo directo
- Mapeo asociativo por conjuntos (2-way)

El simulador es parametrizable en términos de tamaño de bloque y número de líneas.
"""

import math
import random
from typing import Dict, List, Tuple, Optional, Union

class BloqueCache:
    """
    Clase que representa un bloque de memoria caché.
    
    Atributos:
        etiqueta (int): Etiqueta (tag) del bloque.
        datos (List[int]): Datos almacenados en el bloque.
        valido (bool): Indica si el bloque contiene datos válidos.
        contador_uso (int): Contador para política de reemplazo LRU.
    """
    
    def __init__(self, tamano_bloque: int):
        """
        Inicializa un bloque de caché.
        
        Args:
            tamano_bloque (int): Tamaño del bloque en palabras.
        """
        self.etiqueta = -1  # Etiqueta inválida por defecto
        self.datos = [0] * tamano_bloque
        self.valido = False
        self.contador_uso = 0
    
    def __str__(self) -> str:
        """Representación en cadena del bloque de caché."""
        return f"Bloque[etiqueta={self.etiqueta}, válido={self.valido}, datos={self.datos}]"

class CacheBase:
    """
    Clase base para los diferentes tipos de caché.
    
    Atributos:
        tamano_bloque (int): Tamaño de cada bloque en palabras.
        num_lineas (int): Número de líneas en la caché.
        tamano_memoria (int): Tamaño total de la memoria principal en palabras.
        accesos (int): Contador de accesos a la caché.
        aciertos (int): Contador de aciertos de caché.
        fallos (int): Contador de fallos de caché.
    """
    
    def __init__(self, tamano_bloque: int, num_lineas: int, tamano_memoria: int = 1024):
        """
        Inicializa la caché base.
        
        Args:
            tamano_bloque (int): Tamaño de cada bloque en palabras.
            num_lineas (int): Número de líneas en la caché.
            tamano_memoria (int, opcional): Tamaño de la memoria principal en palabras.
                                           Por defecto es 1024.
        """
        self.tamano_bloque = tamano_bloque
        self.num_lineas = num_lineas
        self.tamano_memoria = tamano_memoria
        
        # Estadísticas
        self.accesos = 0
        self.aciertos = 0
        self.fallos = 0
        
        # Memoria principal simulada (para propósitos de demostración)
        self.memoria_principal = [random.randint(0, 255) for _ in range(tamano_memoria)]
    
    def calcular_tasa_aciertos(self) -> float:
        """
        Calcula la tasa de aciertos de la caché.
        
        Returns:
            float: Tasa de aciertos (entre 0 y 1).
        """
        if self.accesos == 0:
            return 0.0
        return self.aciertos / self.accesos
    
    def obtener_estadisticas(self) -> Dict[str, Union[int, float]]:
        """
        Obtiene las estadísticas de rendimiento de la caché.
        
        Returns:
            Dict[str, Union[int, float]]: Diccionario con estadísticas.
        """
        return {
            "accesos": self.accesos,
            "aciertos": self.aciertos,
            "fallos": self.fallos,
            "tasa_aciertos": self.calcular_tasa_aciertos(),
            "tasa_fallos": 1.0 - self.calcular_tasa_aciertos() if self.accesos > 0 else 0.0
        }
    
    def reiniciar_estadisticas(self) -> None:
        """Reinicia los contadores de estadísticas."""
        self.accesos = 0
        self.aciertos = 0
        self.fallos = 0
    
    def leer(self, direccion: int) -> int:
        """
        Lee un dato de la caché.
        
        Args:
            direccion (int): Dirección de memoria a leer.
            
        Returns:
            int: Dato leído.
        
        Nota: Este método debe ser implementado por las subclases.
        """
        raise NotImplementedError("Este método debe ser implementado por las subclases")
    
    def escribir(self, direccion: int, dato: int) -> None:
        """
        Escribe un dato en la caché.
        
        Args:
            direccion (int): Dirección de memoria donde escribir.
            dato (int): Dato a escribir.
        
        Nota: Este método debe ser implementado por las subclases.
        """
        raise NotImplementedError("Este método debe ser implementado por las subclases")

class CacheMapeoDirecto(CacheBase):
    """
    Implementación de caché con mapeo directo.
    En este tipo de caché, cada bloque de memoria principal solo puede
    ubicarse en una única línea de caché específica.
    """
    
    def __init__(self, tamano_bloque: int, num_lineas: int, tamano_memoria: int = 1024):
        """
        Inicializa la caché de mapeo directo.
        
        Args:
            tamano_bloque (int): Tamaño de cada bloque en palabras.
            num_lineas (int): Número de líneas en la caché.
            tamano_memoria (int, opcional): Tamaño de la memoria principal en palabras.
        """
        super().__init__(tamano_bloque, num_lineas, tamano_memoria)
        
        # Inicializar las líneas de caché
        self.lineas = [BloqueCache(tamano_bloque) for _ in range(num_lineas)]
        
        # Calcular bits para offset, índice y etiqueta
        self.bits_offset = int(math.log2(tamano_bloque))
        self.bits_indice = int(math.log2(num_lineas))
        self.mascara_offset = (1 << self.bits_offset) - 1
        self.mascara_indice = ((1 << self.bits_indice) - 1) << self.bits_offset
    
    def _desglosar_direccion(self, direccion: int) -> Tuple[int, int, int]:
        """
        Desglosa una dirección en sus componentes: etiqueta, índice y offset.
        
        Args:
            direccion (int): Dirección de memoria.
            
        Returns:
            Tuple[int, int, int]: Tupla con (etiqueta, índice, offset).
        """
        offset = direccion & self.mascara_offset
        indice = (direccion & self.mascara_indice) >> self.bits_offset
        etiqueta = direccion >> (self.bits_offset + self.bits_indice)
        
        return etiqueta, indice, offset
    
    def leer(self, direccion: int) -> int:
        """
        Lee un dato de la caché de mapeo directo.
        
        Args:
            direccion (int): Dirección de memoria a leer.
            
        Returns:
            int: Dato leído.
        """
        self.accesos += 1
        
        # Desglosar la dirección
        etiqueta, indice, offset = self._desglosar_direccion(direccion)
        
        # Verificar si el bloque está en caché (hit)
        if (self.lineas[indice].valido and self.lineas[indice].etiqueta == etiqueta):
            self.aciertos += 1
            return self.lineas[indice].datos[offset]
        
        # Fallo de caché (miss)
        self.fallos += 1
        
        # Cargar el bloque desde memoria principal
        direccion_base = (etiqueta << (self.bits_offset + self.bits_indice)) | (indice << self.bits_offset)
        for i in range(self.tamano_bloque):
            dir_mem = direccion_base + i
            if dir_mem < self.tamano_memoria:
                self.lineas[indice].datos[i] = self.memoria_principal[dir_mem]
        
        # Actualizar la etiqueta y marcar como válido
        self.lineas[indice].etiqueta = etiqueta
        self.lineas[indice].valido = True
        
        # Retornar el dato solicitado
        return self.lineas[indice].datos[offset]
    
    def escribir(self, direccion: int, dato: int) -> None:
        """
        Escribe un dato en la caché de mapeo directo (política write-through).
        
        Args:
            direccion (int): Dirección de memoria donde escribir.
            dato (int): Dato a escribir.
        """
        self.accesos += 1
        
        # Desglosar la dirección
        etiqueta, indice, offset = self._desglosar_direccion(direccion)
        
        # Verificar si el bloque está en caché (hit)
        if (self.lineas[indice].valido and self.lineas[indice].etiqueta == etiqueta):
            self.aciertos += 1
        else:
            # Fallo de caché (miss)
            self.fallos += 1
            
            # Cargar el bloque desde memoria principal
            direccion_base = (etiqueta << (self.bits_offset + self.bits_indice)) | (indice << self.bits_offset)
            for i in range(self.tamano_bloque):
                dir_mem = direccion_base + i
                if dir_mem < self.tamano_memoria:
                    self.lineas[indice].datos[i] = self.memoria_principal[dir_mem]
            
            # Actualizar la etiqueta y marcar como válido
            self.lineas[indice].etiqueta = etiqueta
            self.lineas[indice].valido = True
        
        # Escribir el dato en la caché
        self.lineas[indice].datos[offset] = dato
        
        # Escribir también en memoria principal (write-through)
        if direccion < self.tamano_memoria:
            self.memoria_principal[direccion] = dato

class CacheAsociativaConjuntos(CacheBase):
    """
    Implementación de caché asociativa por conjuntos (2-way).
    En este tipo de caché, cada bloque de memoria principal puede
    ubicarse en cualquiera de las vías dentro de un conjunto específico.
    """
    
    def __init__(self, tamano_bloque: int, num_conjuntos: int, tamano_memoria: int = 1024):
        """
        Inicializa la caché asociativa por conjuntos (2-way).
        
        Args:
            tamano_bloque (int): Tamaño de cada bloque en palabras.
            num_conjuntos (int): Número de conjuntos en la caché.
            tamano_memoria (int, opcional): Tamaño de la memoria principal en palabras.
        """
        # Cada conjunto tiene 2 vías (2-way)
        super().__init__(tamano_bloque, num_conjuntos * 2, tamano_memoria)
        
        self.num_conjuntos = num_conjuntos
        self.vias_por_conjunto = 2  # 2-way
        
        # Inicializar los conjuntos de caché
        self.conjuntos = [
            [BloqueCache(tamano_bloque) for _ in range(self.vias_por_conjunto)]
            for _ in range(num_conjuntos)
        ]
        
        # Calcular bits para offset, índice y etiqueta
        self.bits_offset = int(math.log2(tamano_bloque))
        self.bits_indice = int(math.log2(num_conjuntos))
        self.mascara_offset = (1 << self.bits_offset) - 1
        self.mascara_indice = ((1 << self.bits_indice) - 1) << self.bits_offset
        
        # Contador global para LRU
        self.contador_global = 0
    
    def _desglosar_direccion(self, direccion: int) -> Tuple[int, int, int]:
        """
        Desglosa una dirección en sus componentes: etiqueta, índice y offset.
        
        Args:
            direccion (int): Dirección de memoria.
            
        Returns:
            Tuple[int, int, int]: Tupla con (etiqueta, índice, offset).
        """
        offset = direccion & self.mascara_offset
        indice = (direccion & self.mascara_indice) >> self.bits_offset
        etiqueta = direccion >> (self.bits_offset + self.bits_indice)
        
        return etiqueta, indice, offset
    
    def _encontrar_via(self, conjunto: int, etiqueta: int) -> Optional[int]:
        """
        Busca una vía en un conjunto que contenga la etiqueta especificada.
        
        Args:
            conjunto (int): Índice del conjunto.
            etiqueta (int): Etiqueta a buscar.
            
        Returns:
            Optional[int]: Índice de la vía si se encuentra, None en caso contrario.
        """
        for i in range(self.vias_por_conjunto):
            if self.conjuntos[conjunto][i].valido and self.conjuntos[conjunto][i].etiqueta == etiqueta:
                return i
        return None
    
    def _seleccionar_via_reemplazo(self, conjunto: int) -> int:
        """
        Selecciona una vía para reemplazo usando política LRU.
        
        Args:
            conjunto (int): Índice del conjunto.
            
        Returns:
            int: Índice de la vía seleccionada para reemplazo.
        """
        # Buscar primero una vía inválida
        for i in range(self.vias_por_conjunto):
            if not self.conjuntos[conjunto][i].valido:
                return i
        
        # Si todas son válidas, seleccionar la menos recientemente usada (LRU)
        lru_via = 0
        min_contador = self.conjuntos[conjunto][0].contador_uso
        
        for i in range(1, self.vias_por_conjunto):
            if self.conjuntos[conjunto][i].contador_uso < min_contador:
                min_contador = self.conjuntos[conjunto][i].contador_uso
                lru_via = i
        
        return lru_via
    
    def leer(self, direccion: int) -> int:
        """
        Lee un dato de la caché asociativa por conjuntos.
        
        Args:
            direccion (int): Dirección de memoria a leer.
            
        Returns:
            int: Dato leído.
        """
        self.accesos += 1
        self.contador_global += 1
        
        # Desglosar la dirección
        etiqueta, indice, offset = self._desglosar_direccion(direccion)
        
        # Buscar en el conjunto correspondiente
        via = self._encontrar_via(indice, etiqueta)
        
        # Verificar si el bloque está en caché (hit)
        if via is not None:
            self.aciertos += 1
            # Actualizar contador LRU
            self.conjuntos[indice][via].contador_uso = self.contador_global
            return self.conjuntos[indice][via].datos[offset]
        
        # Fallo de caché (miss)
        self.fallos += 1
        
        # Seleccionar vía para reemplazo
        via_reemplazo = self._seleccionar_via_reemplazo(indice)
        
        # Cargar el bloque desde memoria principal
        direccion_base = (etiqueta << (self.bits_offset + self.bits_indice)) | (indice << self.bits_offset)
        for i in range(self.tamano_bloque):
            dir_mem = direccion_base + i
            if dir_mem < self.tamano_memoria:
                self.conjuntos[indice][via_reemplazo].datos[i] = self.memoria_principal[dir_mem]
        
        # Actualizar la etiqueta, contador y marcar como válido
        self.conjuntos[indice][via_reemplazo].etiqueta = etiqueta
        self.conjuntos[indice][via_reemplazo].contador_uso = self.contador_global
        self.conjuntos[indice][via_reemplazo].valido = True
        
        # Retornar el dato solicitado
        return self.conjuntos[indice][via_reemplazo].datos[offset]
    
    def escribir(self, direccion: int, dato: int) -> None:
        """
        Escribe un dato en la caché asociativa por conjuntos (política write-through).
        
        Args:
            direccion (int): Dirección de memoria donde escribir.
            dato (int): Dato a escribir.
        """
        self.accesos += 1
        self.contador_global += 1
        
        # Desglosar la dirección
        etiqueta, indice, offset = self._desglosar_direccion(direccion)
        
        # Buscar en el conjunto correspondiente
        via = self._encontrar_via(indice, etiqueta)
        
        # Verificar si el bloque está en caché (hit)
        if via is not None:
            self.aciertos += 1
            # Actualizar contador LRU
            self.conjuntos[indice][via].contador_uso = self.contador_global
        else:
            # Fallo de caché (miss)
            self.fallos += 1
            
            # Seleccionar vía para reemplazo
            via_reemplazo = self._seleccionar_via_reemplazo(indice)
            via = via_reemplazo
            
            # Cargar el bloque desde memoria principal
            direccion_base = (etiqueta << (self.bits_offset + self.bits_indice)) | (indice << self.bits_offset)
            for i in range(self.tamano_bloque):
                dir_mem = direccion_base + i
                if dir_mem < self.tamano_memoria:
                    self.conjuntos[indice][via].datos[i] = self.memoria_principal[dir_mem]
            
            # Actualizar la etiqueta, contador y marcar como válido
            self.conjuntos[indice][via].etiqueta = etiqueta
            self.conjuntos[indice][via].contador_uso = self.contador_global
            self.conjuntos[indice][via].valido = True
        
        # Escribir el dato en la caché
        self.conjuntos[indice][via].datos[offset] = dato
        
        # Escribir también en memoria principal (write-through)
        if direccion < self.tamano_memoria:
            self.memoria_principal[direccion] = dato

# Ejemplo de uso
if __name__ == "__main__":
    # Parámetros de la caché
    TAMANO_BLOQUE = 4  # palabras por bloque
    NUM_LINEAS_DIRECTO = 16  # líneas para mapeo directo
    NUM_CONJUNTOS_ASOCIATIVO = 8  # conjuntos para asociativo (2-way = 16 líneas totales)
    TAMANO_MEMORIA = 1024  # palabras en memoria principal
    
    # Crear instancias de caché
    cache_directo = CacheMapeoDirecto(TAMANO_BLOQUE, NUM_LINEAS_DIRECTO, TAMANO_MEMORIA)
    cache_asociativo = CacheAsociativaConjuntos(TAMANO_BLOQUE, NUM_CONJUNTOS_ASOCIATIVO, TAMANO_MEMORIA)
    
    print("=== Simulación de Caché ===")
    print(f"Tamaño de bloque: {TAMANO_BLOQUE} palabras")
    print(f"Caché de mapeo directo: {NUM_LINEAS_DIRECTO} líneas")
    print(f"Caché asociativa por conjuntos: {NUM_CONJUNTOS_ASOCIATIVO} conjuntos (2-way = {NUM_CONJUNTOS_ASOCIATIVO*2} líneas)")
    print()
    
    # Ejemplo 1: Acceso secuencial
    print("Ejemplo 1: Acceso secuencial a 32 direcciones")
    for i in range(32):
        cache_directo.leer(i)
        cache_asociativo.leer(i)
    
    print("Resultados para mapeo directo:")
    stats_directo = cache_directo.obtener_estadisticas()
    print(f"  Accesos: {stats_directo['accesos']}")
    print(f"  Aciertos: {stats_directo['aciertos']}")
    print(f"  Fallos: {stats_directo['fallos']}")
    print(f"  Tasa de aciertos: {stats_directo['tasa_aciertos']:.2%}")
    
    print("Resultados para asociativo por conjuntos:")
    stats_asociativo = cache_asociativo.obtener_estadisticas()
    print(f"  Accesos: {stats_asociativo['accesos']}")
    print(f"  Aciertos: {stats_asociativo['aciertos']}")
    print(f"  Fallos: {stats_asociativo['fallos']}")
    print(f"  Tasa de aciertos: {stats_asociativo['tasa_aciertos']:.2%}")
    print()
    
    # Reiniciar estadísticas
    cache_directo.reiniciar_estadisticas()
    cache_asociativo.reiniciar_estadisticas()
    
    # Ejemplo 2: Acceso con localidad espacial
    print("Ejemplo 2: Acceso con localidad espacial")
    for _ in range(50):
        base = random.randint(0, TAMANO_MEMORIA - 10)
        for i in range(5):  # Acceder a 5 direcciones contiguas
            cache_directo.leer(base + i)
            cache_asociativo.leer(base + i)
    
    print("Resultados para mapeo directo:")
    stats_directo = cache_directo.obtener_estadisticas()
    print(f"  Accesos: {stats_directo['accesos']}")
    print(f"  Aciertos: {stats_directo['aciertos']}")
    print(f"  Fallos: {stats_directo['fallos']}")
    print(f"  Tasa de aciertos: {stats_directo['tasa_aciertos']:.2%}")
    
    print("Resultados para asociativo por conjuntos:")
    stats_asociativo = cache_asociativo.obtener_estadisticas()
    print(f"  Accesos: {stats_asociativo['accesos']}")
    print(f"  Aciertos: {stats_asociativo['aciertos']}")
    print(f"  Fallos: {stats_asociativo['fallos']}")
    print(f"  Tasa de aciertos: {stats_asociativo['tasa_aciertos']:.2%}")
    print()
    
    # Reiniciar estadísticas
    cache_directo.reiniciar_estadisticas()
    cache_asociativo.reiniciar_estadisticas()
    
    # Ejemplo 3: Acceso aleatorio
    print("Ejemplo 3: Acceso aleatorio a 100 direcciones")
    for _ in range(100):
        direccion = random.randint(0, TAMANO_MEMORIA - 1)
        cache_directo.leer(direccion)
        cache_asociativo.leer(direccion)
    
    print("Resultados para mapeo directo:")
    stats_directo = cache_directo.obtener_estadisticas()
    print(f"  Accesos: {stats_directo['accesos']}")
    print(f"  Aciertos: {stats_directo['aciertos']}")
    print(f"  Fallos: {stats_directo['fallos']}")
    print(f"  Tasa de aciertos: {stats_directo['tasa_aciertos']:.2%}")
    
    print("Resultados para asociativo por conjuntos:")
    stats_asociativo = cache_asociativo.obtener_estadisticas()
    print(f"  Accesos: {stats_asociativo['accesos']}")
    print(f"  Aciertos: {stats_asociativo['aciertos']}")
    print(f"  Fallos: {stats_asociativo['fallos']}")
    print(f"  Tasa de aciertos: {stats_asociativo['tasa_aciertos']:.2%}")
