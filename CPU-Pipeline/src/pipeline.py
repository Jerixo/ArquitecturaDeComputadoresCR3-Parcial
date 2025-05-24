"""
Archivo principal del simulador de pipeline de CPU.
Implementa un pipeline de 5 etapas (IF, ID, EX, MEM, WB) con manejo de hazards.

Este módulo simula un procesador con arquitectura pipeline de 5 etapas,
incluyendo detección y resolución de hazards mediante técnicas de
forwarding y stalling, así como manejo de saltos condicionales.
"""

from hazard_control import HazardControl  # Importa el módulo para manejo de hazards
from isa import ISA  # Importa el módulo de definición del conjunto de instrucciones

class PipelineCPU:
    """
    Clase principal que implementa un procesador con pipeline de 5 etapas.
    
    Esta clase simula el funcionamiento completo de un procesador segmentado,
    incluyendo las etapas IF, ID, EX, MEM y WB, los registros intermedios,
    y los mecanismos para manejar hazards de datos y control.
    """
    
    def __init__(self):
        """
        Inicializa el procesador con pipeline y sus componentes.
        
        Configura los contadores, registros intermedios, memoria, banco de registros,
        y las unidades de control necesarias para la simulación.
        """
        # Contadores y estadísticas para análisis de rendimiento
        self.cycles = 0                # Contador de ciclos ejecutados
        self.instructions_completed = 0  # Contador de instrucciones completadas
        self.stalls_inserted = 0       # Contador de stalls insertados por hazards
        self.branches_taken = 0        # Contador de saltos tomados
        
        # Registros intermedios entre etapas del pipeline
        # Cada registro contiene un campo 'valid' que indica si contiene una instrucción válida
        self.if_id = {"valid": False, "instruction": None, "pc": 0}  # Registro entre IF y ID
        self.id_ex = {"valid": False, "instruction": None, "rs1_value": 0, "rs2_value": 0, "immediate": 0}  # Registro entre ID y EX
        self.ex_mem = {"valid": False, "instruction": None, "alu_result": 0, "rs2_value": 0}  # Registro entre EX y MEM
        self.mem_wb = {"valid": False, "instruction": None, "result": 0}  # Registro entre MEM y WB
        
        # Estado del pipeline para visualización y depuración
        self.pipeline = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}
        
        # Estado del procesador
        self.pc = 0                    # Program Counter (contador de programa)
        self.registers = [0] * 32      # Banco de 32 registros (R0 siempre es 0)
        self.memory = [0] * 1024       # Memoria de datos (1024 palabras)
        self.instructions = []         # Memoria de instrucciones
        
        # Unidades de control especializadas
        self.hazard_unit = HazardControl()  # Unidad para detección y resolución de hazards
        self.isa = ISA()               # Unidad para manejo del conjunto de instrucciones
        
        # Flags de control para el pipeline
        self.stall = False             # Indica si se debe detener el avance del pipeline
        self.flush = False             # Indica si se deben descartar instrucciones en el pipeline

    def load_instructions(self, instructions):
        """
        Carga un programa en la memoria de instrucciones.
        
        Args:
            instructions: Lista de instrucciones en formato de diccionario
        """
        self.instructions = instructions  # Almacena el programa en la memoria de instrucciones
        self.pc = 0                      # Reinicia el contador de programa
        self.reset_pipeline()            # Reinicia el estado del pipeline

    def reset_pipeline(self):
        """
        Reinicia el estado del pipeline.
        
        Vacía todos los registros intermedios y la visualización del pipeline.
        Útil al iniciar un nuevo programa o después de un reset.
        """
        # Reinicia todos los registros intermedios
        self.if_id = {"valid": False, "instruction": None, "pc": 0}
        self.id_ex = {"valid": False, "instruction": None, "rs1_value": 0, "rs2_value": 0, "immediate": 0}
        self.ex_mem = {"valid": False, "instruction": None, "alu_result": 0, "rs2_value": 0}
        self.mem_wb = {"valid": False, "instruction": None, "result": 0}
        
        # Reinicia la visualización del pipeline
        self.pipeline = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}

    def step(self):
        """
        Ejecuta un ciclo completo del pipeline.
        
        Avanza cada etapa del pipeline en orden inverso (de WB a IF) para evitar
        sobrescribir datos necesarios en etapas posteriores.
        """
        self.cycles += 1  # Incrementa el contador de ciclos
        
        # Ejecutar etapas en orden inverso para evitar sobrescribir datos
        # Esto es crucial ya que cada etapa depende del estado de la etapa anterior
        self.writeback_stage()  # Primero WB
        self.memory_stage()     # Luego MEM
        self.execute_stage()    # Luego EX
        self.decode_stage()     # Luego ID
        self.fetch_stage()      # Finalmente IF
        
        # Actualizar visualización del pipeline para depuración
        self.update_pipeline_view()
        
        # Resetear flags después de completar el ciclo
        if self.flush:
            self.flush = False  # El flush solo dura un ciclo

    def fetch_stage(self):
        """
        Etapa IF (Instruction Fetch): Busca la siguiente instrucción.
        
        Obtiene la instrucción apuntada por el PC y la coloca en el registro IF/ID.
        Si hay un stall, la etapa no avanza.
        """
        # Si hay un stall, no avanzar esta etapa
        if self.stall:
            return
            
        # Verificar si hay más instrucciones para ejecutar
        if self.pc < len(self.instructions):
            # Obtener la instrucción actual
            instruction = self.instructions[self.pc]
            
            # Actualizar el registro IF/ID
            self.if_id = {
                "valid": True,              # Marcar como válido
                "instruction": instruction,  # Guardar la instrucción
                "pc": self.pc               # Guardar el PC actual
            }
            
            # Incrementar el PC para la siguiente instrucción
            self.pc += 1
            
            # Actualizar visualización
            self.pipeline["IF"] = instruction
        else:
            # No hay más instrucciones, invalidar el registro IF/ID
            self.if_id = {"valid": False, "instruction": None, "pc": self.pc}
            self.pipeline["IF"] = None

    def decode_stage(self):
        """
        Etapa ID (Instruction Decode): Decodifica la instrucción y lee los registros.
        
        Decodifica la instrucción del registro IF/ID, lee los valores de los registros
        fuente y detecta hazards que puedan requerir stalling.
        """
        # Si hay un flush, invalidar la etapa y no avanzar
        if self.flush:
            # Invalidar IF/ID en caso de flush (por ejemplo, después de un salto)
            self.if_id = {"valid": False, "instruction": None, "pc": self.pc}
            self.pipeline["ID"] = None
            return
            
        # Si no hay instrucción válida en IF/ID, invalidar ID/EX
        if not self.if_id["valid"]:
            self.id_ex = {"valid": False, "instruction": None, "rs1_value": 0, "rs2_value": 0, "immediate": 0}
            self.pipeline["ID"] = None
            return
            
        # Obtener la instrucción del registro IF/ID
        instruction = self.if_id["instruction"]
        self.pipeline["ID"] = instruction
        
        # Detectar hazards que requieren stalling (por ejemplo, dependencias de datos)
        self.stall = self.hazard_unit.detect_hazards(self.if_id, self.id_ex, self.ex_mem)
        
        # Si se detectó un hazard, insertar un stall
        if self.stall:
            self.stalls_inserted += 1  # Incrementar contador de stalls
            # Invalidar ID/EX para insertar una burbuja en el pipeline
            self.id_ex = {"valid": False, "instruction": None, "rs1_value": 0, "rs2_value": 0, "immediate": 0}
            return
            
        # Leer valores de registros fuente
        rs1_value = 0
        rs2_value = 0
        immediate = 0
        
        # Obtener valores de registros según el tipo de instrucción
        if "rs1" in instruction:
            rs1_value = self.registers[instruction["rs1"]]
        if "rs2" in instruction:
            rs2_value = self.registers[instruction["rs2"]]
        if "immediate" in instruction:
            immediate = instruction["immediate"]
        elif "addr" in instruction:
            immediate = instruction["addr"]
            
        # Actualizar registro ID/EX con los valores leídos
        self.id_ex = {
            "valid": True,
            "instruction": instruction,
            "rs1_value": rs1_value,
            "rs2_value": rs2_value,
            "immediate": immediate
        }

    def execute_stage(self):
        """
        Etapa EX (Execute): Ejecuta la operación de la ALU.
        
        Realiza la operación aritmética o lógica correspondiente a la instrucción,
        aplica forwarding si es necesario, y maneja saltos condicionales.
        """
        # Si no hay instrucción válida en ID/EX, invalidar EX/MEM
        if not self.id_ex["valid"]:
            self.ex_mem = {"valid": False, "instruction": None, "alu_result": 0, "rs2_value": 0}
            self.pipeline["EX"] = None
            return
            
        # Obtener la instrucción del registro ID/EX
        instruction = self.id_ex["instruction"]
        self.pipeline["EX"] = instruction
        
        # Aplicar forwarding si es necesario para resolver hazards de datos
        # Esto permite usar resultados de instrucciones anteriores antes de que lleguen a WB
        rs1_value, rs2_value = self.hazard_unit.apply_forwarding(
            self.id_ex, self.ex_mem, self.mem_wb
        )
        
        # Ejecutar la operación ALU según el tipo de instrucción
        alu_result = 0
        op = instruction["op"]
        
        # Operaciones aritméticas
        if op == "ADD":
            alu_result = rs1_value + rs2_value
        elif op == "SUB":
            alu_result = rs1_value - rs2_value
        elif op == "MUL":
            alu_result = rs1_value * rs2_value
        # Operaciones de memoria
        elif op == "LOAD" or op == "STORE":
            alu_result = self.id_ex["immediate"]  # Calcular dirección de memoria
        # Operaciones de salto condicional
        elif op == "BEQ":
            # Comparar registros para determinar si se toma el salto
            alu_result = 1 if rs1_value == rs2_value else 0
            # Si se toma el salto, actualizar PC y hacer flush del pipeline
            if alu_result == 1:
                self.pc = instruction["target"]  # Actualizar PC al destino del salto
                self.flush = True                # Activar flush para limpiar instrucciones posteriores
                self.branches_taken += 1         # Incrementar contador de saltos tomados
                # Invalidar etapas anteriores para evitar ejecutar instrucciones incorrectas
                self.if_id = {"valid": False, "instruction": None, "pc": self.pc}
                self.pipeline["IF"] = None
                self.pipeline["ID"] = None
        # Operaciones de salto incondicional
        elif op == "JUMP":
            self.pc = instruction["target"]  # Actualizar PC al destino del salto
            self.flush = True                # Activar flush para limpiar instrucciones posteriores
            self.branches_taken += 1         # Incrementar contador de saltos tomados
            # Invalidar etapas anteriores para evitar ejecutar instrucciones incorrectas
            self.if_id = {"valid": False, "instruction": None, "pc": self.pc}
            self.pipeline["IF"] = None
            self.pipeline["ID"] = None
            
        # Actualizar registro EX/MEM con el resultado de la ALU
        self.ex_mem = {
            "valid": True,
            "instruction": instruction,
            "alu_result": alu_result,
            "rs2_value": rs2_value  # Necesario para instrucciones STORE
        }

    def memory_stage(self):
        """
        Etapa MEM (Memory Access): Accede a la memoria si es necesario.
        
        Realiza operaciones de lectura o escritura en memoria para instrucciones
        LOAD y STORE, respectivamente.
        """
        # Si no hay instrucción válida en EX/MEM, invalidar MEM/WB
        if not self.ex_mem["valid"]:
            self.mem_wb = {"valid": False, "instruction": None, "result": 0}
            self.pipeline["MEM"] = None
            return
            
        # Obtener la instrucción del registro EX/MEM
        instruction = self.ex_mem["instruction"]
        self.pipeline["MEM"] = instruction
        
        # Por defecto, el resultado es el valor calculado por la ALU
        result = self.ex_mem["alu_result"]
        op = instruction["op"]
        
        # Acceso a memoria según el tipo de instrucción
        if op == "LOAD":
            # Instrucción de carga: leer de memoria
            addr = self.ex_mem["alu_result"]
            if 0 <= addr < len(self.memory):
                result = self.memory[addr]  # Leer valor de memoria
        elif op == "STORE":
            # Instrucción de almacenamiento: escribir en memoria
            addr = self.ex_mem["alu_result"]
            if 0 <= addr < len(self.memory):
                # Usar el valor correcto para almacenar
                if "rs" in instruction:
                    # Si la instrucción especifica el registro fuente directamente
                    self.memory[addr] = self.registers[instruction["rs"]]
                else:
                    # Si no, usar el valor del registro rs2 propagado en el pipeline
                    self.memory[addr] = self.ex_mem["rs2_value"]
                
        # Actualizar registro MEM/WB con el resultado
        self.mem_wb = {
            "valid": True,
            "instruction": instruction,
            "result": result  # Resultado de la operación (ALU o memoria)
        }

    def writeback_stage(self):
        """
        Etapa WB (Write Back): Escribe el resultado en el registro destino si es necesario.
        
        Escribe el resultado de la operación en el registro destino para instrucciones
        que modifican registros (ADD, SUB, MUL, LOAD).
        """
        # Si no hay instrucción válida en MEM/WB, no hay nada que hacer
        if not self.mem_wb["valid"]:
            self.pipeline["WB"] = None
            return
            
        # Obtener la instrucción del registro MEM/WB
        instruction = self.mem_wb["instruction"]
        self.pipeline["WB"] = instruction
        
        op = instruction["op"]
        
        # Escribir en registro si es necesario
        if op in ["ADD", "SUB", "MUL", "LOAD"] and "rd" in instruction:
            rd = instruction["rd"]
            if rd != 0:  # R0 siempre es 0 en arquitecturas MIPS-like
                self.registers[rd] = self.mem_wb["result"]  # Escribir resultado en registro destino
                
        # Incrementar contador de instrucciones completadas
        self.instructions_completed += 1

    def update_pipeline_view(self):
        """
        Actualiza la vista del pipeline para visualización y depuración.
        
        Mantiene un diccionario con el estado actual de cada etapa para facilitar
        la visualización y depuración del pipeline.
        """
        # Actualizar el estado de cada etapa basado en los registros intermedios
        self.pipeline = {
            "IF": self.if_id["instruction"] if self.if_id["valid"] else None,
            "ID": self.id_ex["instruction"] if self.id_ex["valid"] else None,
            "EX": self.ex_mem["instruction"] if self.ex_mem["valid"] else None,
            "MEM": self.mem_wb["instruction"] if self.mem_wb["valid"] else None,
            "WB": self.pipeline["MEM"]  # WB muestra la instrucción que estaba en MEM
        }

    def run(self, cycles=None):
        """
        Ejecuta el pipeline por un número específico de ciclos o hasta completar el programa.
        
        Args:
            cycles: Número máximo de ciclos a ejecutar. Si es None, ejecuta hasta completar.
            
        Returns:
            Diccionario con estadísticas de ejecución (ciclos, instrucciones, stalls, etc.)
        """
        cycle_count = 0
        
        while (cycles is None or cycle_count < cycles) and (
            any(stage is not None for stage in self.pipeline.values()) or 
            self.pc < len(self.instructions)
        ):
            self.step()  # Ejecutar un ciclo del pipeline
            cycle_count += 1
            
        return {
            "cycles": self.cycles,                      # Total de ciclos ejecutados
            "instructions_completed": self.instructions_completed,  # Instrucciones completadas
            "stalls_inserted": self.stalls_inserted,    # Stalls insertados por hazards
            "branches_taken": self.branches_taken,      # Saltos tomados
            "cpi": self.cycles / self.instructions_completed if self.instructions_completed > 0 else 0  # Ciclos por instrucción
        }

    def print_state(self):
        """
        Imprime el estado actual del pipeline para depuración.
        
        Muestra el contenido de cada etapa y los primeros 10 registros.
        """
        print(f"Cycle {self.cycles}")  # Mostrar ciclo actual
        # Mostrar instrucción en cada etapa
        for stage in ["IF", "ID", "EX", "MEM", "WB"]:
            instr = self.pipeline[stage]
            print(f"{stage}: {instr}")
        # Mostrar primeros 10 registros
        print("Regs:", self.registers[:10])
        print("---")
