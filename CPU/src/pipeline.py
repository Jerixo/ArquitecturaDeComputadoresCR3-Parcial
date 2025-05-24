"""
Archivo principal del simulador de pipeline de CPU.
Implementa un pipeline de 5 etapas (IF, ID, EX, MEM, WB) con manejo de hazards.
"""

from hazard_control import HazardControl
from isa import ISA

class PipelineCPU:
    def __init__(self):
        # Contadores y estadísticas
        self.cycles = 0
        self.instructions_completed = 0
        self.stalls_inserted = 0
        self.branches_taken = 0
        
        # Registros del pipeline
        self.if_id = {"valid": False, "instruction": None, "pc": 0}
        self.id_ex = {"valid": False, "instruction": None, "rs1_value": 0, "rs2_value": 0, "immediate": 0}
        self.ex_mem = {"valid": False, "instruction": None, "alu_result": 0, "rs2_value": 0}
        self.mem_wb = {"valid": False, "instruction": None, "result": 0}
        
        # Estado del pipeline para visualización
        self.pipeline = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}
        
        # Estado del procesador
        self.pc = 0
        self.registers = [0] * 32
        self.memory = [0] * 1024
        self.instructions = []
        
        # Unidades de control
        self.hazard_unit = HazardControl()
        self.isa = ISA()
        
        # Flags de control
        self.stall = False
        self.flush = False

    def load_instructions(self, instructions):
        """Carga un programa en la memoria de instrucciones."""
        self.instructions = instructions
        self.pc = 0
        self.reset_pipeline()

    def reset_pipeline(self):
        """Reinicia el estado del pipeline."""
        self.if_id = {"valid": False, "instruction": None, "pc": 0}
        self.id_ex = {"valid": False, "instruction": None, "rs1_value": 0, "rs2_value": 0, "immediate": 0}
        self.ex_mem = {"valid": False, "instruction": None, "alu_result": 0, "rs2_value": 0}
        self.mem_wb = {"valid": False, "instruction": None, "result": 0}
        self.pipeline = {"IF": None, "ID": None, "EX": None, "MEM": None, "WB": None}

    def step(self):
        """Ejecuta un ciclo del pipeline."""
        self.cycles += 1

        # Ejecutar etapas en orden inverso
        self.writeback_stage()
        self.memory_stage()
        self.execute_stage()

        if self.flush:
            self.if_id = {"valid": False, "instruction": None, "pc": self.pc}
            self.pipeline["IF"] = None
            self.flush = False  # <- resetea el flag después de limpiar

        self.decode_stage()
        self.fetch_stage()

        # Actualizar visualización del pipeline
        self.update_pipeline_view()


    def fetch_stage(self):
        """Etapa IF: Busca la siguiente instrucción."""
        if self.stall:
            self.pipeline["IF"] = None  #evita mostrar una instrucción cuando se hace stall
            return

        if self.pc < len(self.instructions):
            instruction = self.instructions[self.pc]
            self.if_id = {
                "valid": True,
                "instruction": instruction,
                "pc": self.pc
            }
            self.pc += 1
            self.pipeline["IF"] = instruction
        else:
            self.if_id = {"valid": False, "instruction": None, "pc": self.pc}
            self.pipeline["IF"] = None


    def decode_stage(self):
        """Etapa ID: Decodifica la instrucción y lee los registros."""
        if self.flush:
            # Invalidar IF/ID en caso de flush
            self.if_id = {"valid": False, "instruction": None, "pc": self.pc}
            self.pipeline["ID"] = None
            return
            
        if not self.if_id["valid"]:
            self.id_ex = {"valid": False, "instruction": None, "rs1_value": 0, "rs2_value": 0, "immediate": 0}
            self.pipeline["ID"] = None
            return
            
        instruction = self.if_id["instruction"]
        self.pipeline["ID"] = instruction
        
        # Detectar hazards que requieren stalling
        self.stall = self.hazard_unit.detect_hazards(self.if_id, self.id_ex, self.ex_mem)
        
        if self.stall:
            self.stalls_inserted += 1
            self.id_ex = {"valid": False, "instruction": None, "rs1_value": 0, "rs2_value": 0, "immediate": 0}
            return
            
        # Leer valores de registros
        rs1_value = 0
        rs2_value = 0
        immediate = 0
        
        if "rs1" in instruction:
            rs1_value = self.registers[instruction["rs1"]]
        if "rs2" in instruction:
            rs2_value = self.registers[instruction["rs2"]]
        if "immediate" in instruction:
            immediate = instruction["immediate"]
        elif "addr" in instruction:
            immediate = instruction["addr"]
            
        # Actualizar registro ID/EX
        self.id_ex = {
            "valid": True,
            "instruction": instruction,
            "rs1_value": rs1_value,
            "rs2_value": rs2_value,
            "immediate": immediate
        }

    def execute_stage(self):
        """Etapa EX: Ejecuta la operación de la ALU."""
        if not self.id_ex["valid"]:
            self.ex_mem = {"valid": False, "instruction": None, "alu_result": 0, "rs2_value": 0}
            self.pipeline["EX"] = None
            return
            
        instruction = self.id_ex["instruction"]
        self.pipeline["EX"] = instruction
        
        # Aplicar forwarding si es necesario
        rs1_value, rs2_value = self.hazard_unit.apply_forwarding(
            self.id_ex, self.ex_mem, self.mem_wb
        )
        
        # Ejecutar operación ALU
        alu_result = 0
        op = instruction["op"]
        
        if op == "ADD":
            alu_result = rs1_value + rs2_value
        elif op == "SUB":
            alu_result = rs1_value - rs2_value
        elif op == "MUL":
            alu_result = rs1_value * rs2_value
        elif op == "LOAD" or op == "STORE":
            alu_result = self.id_ex["immediate"]  # Dirección de memoria
        elif op == "BEQ":
            alu_result = 1 if rs1_value == rs2_value else 0
            # CORRECCIÓN: Manejo de saltos
            if alu_result == 1:
                self.pc = instruction["target"]
                self.flush = True
                self.branches_taken += 1
        elif op == "JUMP":
            self.pc = instruction["target"]
            self.flush = True
            self.branches_taken += 1
            
        # Actualizar registro EX/MEM
        self.ex_mem = {
            "valid": True,
            "instruction": instruction,
            "alu_result": alu_result,
            "rs2_value": rs2_value
        }

    def memory_stage(self):
        """Etapa MEM: Accede a la memoria si es necesario."""
        if not self.ex_mem["valid"]:
            self.mem_wb = {"valid": False, "instruction": None, "result": 0}
            self.pipeline["MEM"] = None
            return
            
        instruction = self.ex_mem["instruction"]
        self.pipeline["MEM"] = instruction
        
        result = self.ex_mem["alu_result"]
        op = instruction["op"]
        
        if op == "LOAD":
            addr = self.ex_mem["alu_result"]
            if 0 <= addr < len(self.memory):
                result = self.memory[addr]
        elif op == "STORE":
            addr = self.ex_mem["alu_result"]
            if 0 <= addr < len(self.memory):
                if "rs" in instruction:
                    self.memory[addr] = self.registers[instruction["rs"]]
                else:
                    self.memory[addr] = self.ex_mem["rs2_value"]
                
        # Actualizar registro MEM/WB
        self.mem_wb = {
            "valid": True,
            "instruction": instruction,
            "result": result
        }

    def writeback_stage(self):
        """Etapa WB: Escribe el resultado en el registro destino si es necesario."""
        if not self.mem_wb["valid"]:
            self.pipeline["WB"] = None
            return
            
        instruction = self.mem_wb["instruction"]
        self.pipeline["WB"] = instruction
        
        op = instruction["op"]
        
        # Escribir en registro si es necesario
        if op in ["ADD", "SUB", "MUL", "LOAD"] and "rd" in instruction:
            rd = instruction["rd"]
            if rd != 0:  # R0 siempre es 0
                self.registers[rd] = self.mem_wb["result"]
                
        self.instructions_completed += 1

    def update_pipeline_view(self):
        """Actualiza la vista del pipeline para visualización."""
        self.pipeline = {
            "IF": self.if_id["instruction"] if self.if_id["valid"] else None,
            "ID": self.id_ex["instruction"] if self.id_ex["valid"] else None,
            "EX": self.ex_mem["instruction"] if self.ex_mem["valid"] else None,
            "MEM": self.mem_wb["instruction"] if self.mem_wb["valid"] else None,
            "WB": self.pipeline["MEM"]
        }

    def run(self, cycles=None):
        """Ejecuta el pipeline por un número específico de ciclos o hasta completar."""
        cycle_count = 0
        
        while (cycles is None or cycle_count < cycles) and (
            any(stage is not None for stage in self.pipeline.values()) or 
            self.pc < len(self.instructions)
        ):
            self.step()
            cycle_count += 1
            
        return {
            "cycles": self.cycles,
            "instructions_completed": self.instructions_completed,
            "stalls_inserted": self.stalls_inserted,
            "branches_taken": self.branches_taken,
            "cpi": self.cycles / self.instructions_completed if self.instructions_completed > 0 else 0
        }

    def print_state(self):
        """Imprime el estado actual del pipeline."""
        print(f"Cycle {self.cycles}")
        for stage in ["IF", "ID", "EX", "MEM", "WB"]:
            instr = self.pipeline[stage]
            print(f"{stage}: {instr}")
        print("Regs:", self.registers[:10])
        print("---")
