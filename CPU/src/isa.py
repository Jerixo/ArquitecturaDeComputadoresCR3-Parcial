"""
Módulo para la definición del conjunto de instrucciones (ISA).
Implementa la codificación y decodificación de instrucciones.
"""

class ISA:
    # Códigos de operación
    OPCODES = {
        "ADD": 0x00,
        "SUB": 0x01,
        "MUL": 0x02,
        "LOAD": 0x03,
        "STORE": 0x04,
        "BEQ": 0x05,
        "JUMP": 0x06
    }
    
    # Formatos de instrucción
    FORMATS = {
        "ADD": "R",   # Formato R: opcode (6 bits), rs1 (5 bits), rs2 (5 bits), rd (5 bits), funct (11 bits)
        "SUB": "R",
        "MUL": "R",
        "LOAD": "I",  # Formato I: opcode (6 bits), rs1 (5 bits), rd (5 bits), immediate (16 bits)
        "STORE": "S", # Formato S: opcode (6 bits), rs (5 bits), immediate (21 bits)
        "BEQ": "B",   # Formato B: opcode (6 bits), rs1 (5 bits), rs2 (5 bits), target (16 bits)
        "JUMP": "J"   # Formato J: opcode (6 bits), target (26 bits)
    }
    
    def __init__(self):
        """Inicializa el conjunto de instrucciones."""
        pass
    
    def execute(self, instr, registers, memory):
        """
        Ejecuta una instrucción.
        
        Args:
            instr: Instrucción a ejecutar
            registers: Banco de registros
            memory: Memoria de datos
            
        Returns:
            Dirección de salto si es una instrucción de salto, None en caso contrario
        """
        op = instr["op"]
        
        if op == "ADD":
            registers[instr["rd"]] = registers[instr["rs1"]] + registers[instr["rs2"]]
        elif op == "SUB":
            registers[instr["rd"]] = registers[instr["rs1"]] - registers[instr["rs2"]]
        elif op == "MUL":
            registers[instr["rd"]] = registers[instr["rs1"]] * registers[instr["rs2"]]
        elif op == "LOAD":
            registers[instr["rd"]] = memory[instr["addr"]]
        elif op == "STORE":
            memory[instr["addr"]] = registers[instr["rs"]]
        elif op == "BEQ":
            if registers[instr["rs1"]] == registers[instr["rs2"]]:
                return instr["target"]
        elif op == "JUMP":
            return instr["target"]
        
        return None
    
    def encode_instruction(self, instr):
        """
        Codifica una instrucción en formato binario.
        
        Args:
            instr: Instrucción en formato de diccionario
            
        Returns:
            Instrucción codificada (entero de 32 bits)
        """
        if not instr or "op" not in instr:
            return 0
            
        op = instr["op"]
        if op not in self.OPCODES:
            return 0
            
        opcode = self.OPCODES[op]
        format_type = self.FORMATS[op]
        
        # Codificar según el formato
        if format_type == "R":  # ADD, SUB, MUL
            rs1 = instr.get("rs1", 0)
            rs2 = instr.get("rs2", 0)
            rd = instr.get("rd", 0)
            funct = 0  # No usado en esta implementación simplificada
            
            return (opcode << 26) | (rs1 << 21) | (rs2 << 16) | (rd << 11) | funct
            
        elif format_type == "I":  # LOAD
            rs1 = instr.get("rs1", 0)
            rd = instr.get("rd", 0)
            immediate = instr.get("addr", 0) & 0xFFFF  # Limitar a 16 bits
            
            return (opcode << 26) | (rs1 << 21) | (rd << 16) | immediate
            
        elif format_type == "S":  # STORE
            rs = instr.get("rs", 0)
            immediate = instr.get("addr", 0) & 0x1FFFFF  # Limitar a 21 bits
            
            return (opcode << 26) | (rs << 21) | immediate
            
        elif format_type == "B":  # BEQ
            rs1 = instr.get("rs1", 0)
            rs2 = instr.get("rs2", 0)
            target = instr.get("target", 0) & 0xFFFF  # Limitar a 16 bits
            
            return (opcode << 26) | (rs1 << 21) | (rs2 << 16) | target
            
        elif format_type == "J":  # JUMP
            target = instr.get("target", 0) & 0x3FFFFFF  # Limitar a 26 bits
            
            return (opcode << 26) | target
            
        return 0
    
    def decode_instruction(self, binary):
        """
        Decodifica una instrucción binaria.
        
        Args:
            binary: Instrucción en formato binario (entero de 32 bits)
            
        Returns:
            Instrucción en formato de diccionario
        """
        opcode = (binary >> 26) & 0x3F
        
        # Buscar operación por opcode
        op = None
        for key, value in self.OPCODES.items():
            if value == opcode:
                op = key
                break
                
        if op is None:
            return {"op": "NOP"}
            
        format_type = self.FORMATS[op]
        
        # Decodificar según el formato
        if format_type == "R":  # ADD, SUB, MUL
            rs1 = (binary >> 21) & 0x1F
            rs2 = (binary >> 16) & 0x1F
            rd = (binary >> 11) & 0x1F
            
            return {"op": op, "rs1": rs1, "rs2": rs2, "rd": rd}
            
        elif format_type == "I":  # LOAD
            rs1 = (binary >> 21) & 0x1F
            rd = (binary >> 16) & 0x1F
            immediate = binary & 0xFFFF
            
            # Extender signo si es necesario
            if immediate & 0x8000:
                immediate |= 0xFFFF0000
                
            return {"op": op, "rs1": rs1, "rd": rd, "addr": immediate}
            
        elif format_type == "S":  # STORE
            rs = (binary >> 21) & 0x1F
            immediate = binary & 0x1FFFFF
            
            # Extender signo si es necesario
            if immediate & 0x100000:
                immediate |= 0xFFE00000
                
            return {"op": op, "rs": rs, "addr": immediate}
            
        elif format_type == "B":  # BEQ
            rs1 = (binary >> 21) & 0x1F
            rs2 = (binary >> 16) & 0x1F
            target = binary & 0xFFFF
            
            # Extender signo si es necesario
            if target & 0x8000:
                target |= 0xFFFF0000
                
            return {"op": op, "rs1": rs1, "rs2": rs2, "target": target}
            
        elif format_type == "J":  # JUMP
            target = binary & 0x3FFFFFF
            
            # Extender signo si es necesario
            if target & 0x2000000:
                target |= 0xFC000000
                
            return {"op": op, "target": target}
            
        return {"op": "NOP"}
    
    def assemble_program(self, program_text):
        """
        Ensambla un programa en texto a instrucciones.
        
        Args:
            program_text: Programa en formato de texto (una instrucción por línea)
            
        Returns:
            Lista de instrucciones en formato de diccionario
        """
        instructions = []
        
        for line in program_text.strip().split('\n'):
            line = line.strip()
            if not line or line.startswith('#'):
                continue
                
            parts = line.split()
            op = parts[0].upper()
            
            if op == "ADD" or op == "SUB" or op == "MUL":
                # Formato: ADD rd, rs1, rs2
                regs = parts[1].split(',')
                rd = int(regs[0][1:])  # Quitar 'R' y convertir a entero
                rs1 = int(regs[1][1:])
                rs2 = int(regs[2][1:])
                instructions.append({"op": op, "rd": rd, "rs1": rs1, "rs2": rs2})
                
            elif op == "LOAD":
                # Formato: LOAD rd, addr
                regs = parts[1].split(',')
                rd = int(regs[0][1:])
                addr = int(regs[1])
                instructions.append({"op": op, "rd": rd, "addr": addr})
                
            elif op == "STORE":
                # Formato: STORE rs, addr
                regs = parts[1].split(',')
                rs = int(regs[0][1:])
                addr = int(regs[1])
                instructions.append({"op": op, "rs": rs, "addr": addr})
                
            elif op == "BEQ":
                # Formato: BEQ rs1, rs2, target
                regs = parts[1].split(',')
                rs1 = int(regs[0][1:])
                rs2 = int(regs[1][1:])
                target = int(regs[2])
                instructions.append({"op": op, "rs1": rs1, "rs2": rs2, "target": target})
                
            elif op == "JUMP":
                # Formato: JUMP target
                target = int(parts[1])
                instructions.append({"op": op, "target": target})
                
        return instructions
    
    def disassemble_instruction(self, instr):
        """
        Convierte una instrucción a formato de texto.
        
        Args:
            instr: Instrucción en formato de diccionario
            
        Returns:
            Instrucción en formato de texto
        """
        if not instr or "op" not in instr:
            return "NOP"
            
        op = instr["op"]
        
        if op == "ADD" or op == "SUB" or op == "MUL":
            return f"{op} R{instr['rd']}, R{instr['rs1']}, R{instr['rs2']}"
            
        elif op == "LOAD":
            return f"{op} R{instr['rd']}, {instr['addr']}"
            
        elif op == "STORE":
            return f"{op} R{instr['rs']}, {instr['addr']}"
            
        elif op == "BEQ":
            return f"{op} R{instr['rs1']}, R{instr['rs2']}, {instr['target']}"
            
        elif op == "JUMP":
            return f"{op} {instr['target']}"
            
        return "NOP"
