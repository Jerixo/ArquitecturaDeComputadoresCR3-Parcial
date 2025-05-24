"""
Módulo para la detección y resolución de hazards en el pipeline.
Implementa unidades de forwarding y detección de hazards.
"""

class HazardControl:
    def __init__(self):
        """Inicializa las unidades de control de hazards."""
        pass
    
    def detect_hazards(self, if_id, id_ex, ex_mem):
        """
        Detecta hazards de datos que requieren stalling.
        
        Args:
            if_id: Registro IF/ID
            id_ex: Registro ID/EX
            ex_mem: Registro EX/MEM
            
        Returns:
            True si se detecta un hazard que requiere stall, False en caso contrario
        """
        if not if_id["valid"] or not if_id["instruction"]:
            return False
            
        # Obtener registros fuente de la instrucción en IF/ID
        instruction = if_id["instruction"]
        rs1 = instruction.get("rs1", -1)
        rs2 = instruction.get("rs2", -1)
        
        # Si no hay registros fuente, no hay hazard
        if rs1 == -1 and rs2 == -1:
            return False
            
        # Hazard de carga-uso (Load-Use Hazard)
        # Si una instrucción de carga es seguida inmediatamente por una instrucción
        # que usa el registro cargado, necesitamos hacer stall
        if id_ex["valid"] and id_ex["instruction"]:
            id_ex_instr = id_ex["instruction"]
            
            # Si es una instrucción LOAD y el registro destino es usado por la siguiente instrucción
            if id_ex_instr["op"] == "LOAD" and "rd" in id_ex_instr:
                rd = id_ex_instr["rd"]
                if rd != 0 and (rd == rs1 or rd == rs2):
                    return True
                    
        # Hazards de control (Branch Hazards)
        # Ya manejados en la etapa EX del pipeline
        
        return False
    
    def get_forwarding_signals(self, id_ex, ex_mem, mem_wb):
        """
        Determina las señales de forwarding para los operandos.
        
        Args:
            id_ex: Registro ID/EX
            ex_mem: Registro EX/MEM
            mem_wb: Registro MEM/WB
            
        Returns:
            Tupla (forward_rs1, forward_rs2) con las señales de forwarding para cada operando
        """
        forward_rs1 = "none"  # No forwarding
        forward_rs2 = "none"  # No forwarding
        
        if not id_ex["valid"] or not id_ex["instruction"]:
            return forward_rs1, forward_rs2
            
        # Obtener registros fuente de la instrucción en ID/EX
        instruction = id_ex["instruction"]
        rs1 = instruction.get("rs1", -1)
        rs2 = instruction.get("rs2", -1)
        
        # Forwarding desde EX/MEM
        if ex_mem["valid"] and ex_mem["instruction"]:
            ex_mem_instr = ex_mem["instruction"]
            
            # Solo instrucciones que escriben en registros pueden ser fuente de forwarding
            if ex_mem_instr["op"] in ["ADD", "SUB", "MUL", "LOAD"] and "rd" in ex_mem_instr:
                rd = ex_mem_instr["rd"]
                
                # No forwarding desde R0
                if rd != 0:
                    if rd == rs1:
                        forward_rs1 = "ex_mem"
                    if rd == rs2:
                        forward_rs2 = "ex_mem"
        
        # Forwarding desde MEM/WB
        if mem_wb["valid"] and mem_wb["instruction"]:
            mem_wb_instr = mem_wb["instruction"]
            
            # Solo instrucciones que escriben en registros pueden ser fuente de forwarding
            if mem_wb_instr["op"] in ["ADD", "SUB", "MUL", "LOAD"] and "rd" in mem_wb_instr:
                rd = mem_wb_instr["rd"]
                
                # No forwarding desde R0
                if rd != 0:
                    # Solo forward desde MEM/WB si no hay ya un forward desde EX/MEM
                    if rd == rs1 and forward_rs1 == "none":
                        forward_rs1 = "mem_wb"
                    if rd == rs2 and forward_rs2 == "none":
                        forward_rs2 = "mem_wb"
        
        return forward_rs1, forward_rs2
    
    def apply_forwarding(self, id_ex, ex_mem, mem_wb):
        """
        Aplica forwarding a los operandos.
        
        Args:
            id_ex: Registro ID/EX
            ex_mem: Registro EX/MEM
            mem_wb: Registro MEM/WB
            
        Returns:
            Tupla (rs1_value, rs2_value) con los valores correctos
        """
        # Valores originales
        rs1_value = id_ex["rs1_value"]
        rs2_value = id_ex["rs2_value"]
        
        # Obtener señales de forwarding
        forward_rs1, forward_rs2 = self.get_forwarding_signals(id_ex, ex_mem, mem_wb)
        
        # Aplicar forwarding para rs1
        if forward_rs1 == "ex_mem":
            # Para LOAD, el resultado no está disponible hasta después de MEM
            if ex_mem["instruction"]["op"] != "LOAD":
                rs1_value = ex_mem["alu_result"]
        elif forward_rs1 == "mem_wb":
            rs1_value = mem_wb["result"]
        
        # Aplicar forwarding para rs2
        if forward_rs2 == "ex_mem":
            # Para LOAD, el resultado no está disponible hasta después de MEM
            if ex_mem["instruction"]["op"] != "LOAD":
                rs2_value = ex_mem["alu_result"]
        elif forward_rs2 == "mem_wb":
            rs2_value = mem_wb["result"]
        
        return rs1_value, rs2_value
    
    def resolve(self, pipeline, registers):
        """
        Método de compatibilidad con la implementación original.
        Detecta hazards y determina la acción a tomar.
        
        Args:
            pipeline: Estado del pipeline
            registers: Banco de registros
            
        Returns:
            String indicando la acción a tomar: "stall", "forward", o None
        """
        id_instr = pipeline.get("ID")
        ex_instr = pipeline.get("EX")
        mem_instr = pipeline.get("MEM")
        wb_instr = pipeline.get("WB")

        if not id_instr:
            return None

        rs1 = id_instr.get("rs1")
        rs2 = id_instr.get("rs2")

        # Dependencia con EX (valor no disponible aún)
        if ex_instr and ex_instr.get("op") == "LOAD" and ex_instr.get("rd") in (rs1, rs2):
            return "stall"

        # Forwarding desde MEM
        if mem_instr and mem_instr.get("rd") in (rs1, rs2):
            return "forward"

        # Forwarding desde WB
        if wb_instr and wb_instr.get("rd") in (rs1, rs2):
            return "forward"

        return None
