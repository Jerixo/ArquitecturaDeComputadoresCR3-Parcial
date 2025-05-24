"""
Pruebas para el simulador de pipeline de CPU.
Incluye pruebas básicas y casos de prueba para detección y resolución de hazards.
"""

from pipeline import PipelineCPU
from hazard_control import HazardControl
from isa import ISA

def test_basic_execution():
    """Prueba la ejecución básica del pipeline con operaciones aritméticas."""
    print("=== Test 1: Ejecución básica con operaciones aritméticas ===")
    
    # Programa de prueba con operaciones aritméticas simples
    program = [
        {"op": "ADD", "rd": 1, "rs1": 2, "rs2": 3},         # R1 = R2 + R3
        {"op": "SUB", "rd": 4, "rs1": 5, "rs2": 6},         # R4 = R5 - R6
        {"op": "MUL", "rd": 7, "rs1": 8, "rs2": 9},         # R7 = R8 * R9
    ]
    
    # Inicializar pipeline y registros
    cpu = PipelineCPU()
    cpu.load_instructions(program)
    
    # Valores iniciales para los registros
    cpu.registers[2] = 10
    cpu.registers[3] = 20
    cpu.registers[5] = 30
    cpu.registers[6] = 15
    cpu.registers[8] = 5
    cpu.registers[9] = 6
    
    print("Estado inicial:")
    print(f"R2 = {cpu.registers[2]}, R3 = {cpu.registers[3]}")
    print(f"R5 = {cpu.registers[5]}, R6 = {cpu.registers[6]}")
    print(f"R8 = {cpu.registers[8]}, R9 = {cpu.registers[9]}")
    
    # Ejecutar hasta completar todas las instrucciones
    print("\nEjecutando pipeline...")
    while any(cpu.pipeline.values()) or cpu.pc < len(cpu.instructions):
        cpu.print_state()
        cpu.step()
    
    # Verificar resultados y estadísticas
    print("\nResultados finales:")
    print(f"R1 = {cpu.registers[1]} (esperado: 30)")
    print(f"R4 = {cpu.registers[4]} (esperado: 15)")
    print(f"R7 = {cpu.registers[7]} (esperado: 30)")
    
    stats = {
        "cycles": cpu.cycles,
        "instructions_completed": cpu.instructions_completed,
        "stalls_inserted": cpu.stalls_inserted,
        "branches_taken": cpu.branches_taken
    }
    print(f"\nEstadísticas: {stats}")

def test_data_hazards():
    """Prueba la detección y resolución de hazards de datos."""
    print("\n=== Test 2: Hazards de datos con forwarding y stalling ===")
    
    # Programa con dependencias de datos que requieren forwarding y stalling
    program = [
        {"op": "ADD", "rd": 1, "rs1": 2, "rs2": 3},         # R1 = R2 + R3
        {"op": "ADD", "rd": 4, "rs1": 1, "rs2": 5},         # R4 = R1 + R5 (depende de ADD → requiere forwarding)
        {"op": "SUB", "rd": 6, "rs1": 4, "rs2": 7},         # R6 = R4 - R7 (depende de ADD → requiere forwarding)
        {"op": "LOAD", "rd": 8, "addr": 100},               # R8 = MEM[100]
        {"op": "ADD", "rd": 9, "rs1": 8, "rs2": 10},        # R9 = R8 + R10 (depende de LOAD → requiere stalling)
    ]
    
    # Inicializar pipeline, registros y memoria
    cpu = PipelineCPU()
    cpu.load_instructions(program)
    
    cpu.registers[2] = 10
    cpu.registers[3] = 20
    cpu.registers[5] = 5
    cpu.registers[7] = 8
    cpu.registers[10] = 15
    cpu.memory[100] = 25
    
    print("Estado inicial:")
    print(f"R2 = {cpu.registers[2]}, R3 = {cpu.registers[3]}")
    print(f"R5 = {cpu.registers[5]}, R7 = {cpu.registers[7]}")
    print(f"R10 = {cpu.registers[10]}, MEM[100] = {cpu.memory[100]}")
    
    # Ejecutar hasta completar todas las instrucciones
    print("\nEjecutando pipeline...")
    while any(cpu.pipeline.values()) or cpu.pc < len(cpu.instructions):
        cpu.print_state()
        cpu.step()
    
    # Verificar resultados y estadísticas
    print("\nResultados finales:")
    print(f"R1 = {cpu.registers[1]} (esperado: 30)")
    print(f"R4 = {cpu.registers[4]} (esperado: 35)")
    print(f"R6 = {cpu.registers[6]} (esperado: 27)")
    print(f"R8 = {cpu.registers[8]} (esperado: 25)")
    print(f"R9 = {cpu.registers[9]} (esperado: 40)")
    
    stats = {
        "cycles": cpu.cycles,
        "instructions_completed": cpu.instructions_completed,
        "stalls_inserted": cpu.stalls_inserted,
        "branches_taken": cpu.branches_taken
    }
    print(f"\nEstadísticas: {stats}")
    print(f"Stalls insertados: {cpu.stalls_inserted} (esperado: al menos 1)")

def test_control_hazards():
    """Prueba la detección y resolución de hazards de control."""
    print("\n=== Test 3: Hazards de control con saltos ===")
    
    # Programa con salto condicional para probar flush del pipeline
    program = [
        {"op": "ADD", "rd": 1, "rs1": 2, "rs2": 3},         # R1 = R2 + R3
        {"op": "ADD", "rd": 4, "rs1": 5, "rs2": 6},         # R4 = R5 + R6
        {"op": "BEQ", "rs1": 1, "rs2": 4, "target": 5},     # Si R1 == R4, saltar a instrucción 5
        {"op": "ADD", "rd": 7, "rs1": 8, "rs2": 9},         # R7 = R8 + R9 (no se ejecuta si el salto se toma)
        {"op": "SUB", "rd": 10, "rs1": 11, "rs2": 12},      # R10 = R11 - R12 (no se ejecuta si el salto se toma)
        {"op": "MUL", "rd": 13, "rs1": 14, "rs2": 15},      # R13 = R14 * R15 (destino del salto)
    ]
    
    # Inicializar pipeline y registros
    cpu = PipelineCPU()
    cpu.load_instructions(program)
    
    # Valores iniciales para los registros (R1 y R4 serán iguales para tomar el salto)
    cpu.registers[2] = 10
    cpu.registers[3] = 20
    cpu.registers[5] = 15
    cpu.registers[6] = 15
    cpu.registers[8] = 5
    cpu.registers[9] = 10
    cpu.registers[11] = 20
    cpu.registers[12] = 5
    cpu.registers[14] = 4
    cpu.registers[15] = 5
    
    print("Estado inicial:")
    print(f"R2 = {cpu.registers[2]}, R3 = {cpu.registers[3]}")
    print(f"R5 = {cpu.registers[5]}, R6 = {cpu.registers[6]}")
    
    # Ejecutar hasta completar todas las instrucciones
    print("\nEjecutando pipeline...")
    while any(cpu.pipeline.values()) or cpu.pc < len(cpu.instructions):
        cpu.print_state()
        cpu.step()
    
    # Verificar resultados y estadísticas
    print("\nResultados finales:")
    print(f"R1 = {cpu.registers[1]} (esperado: 30)")
    print(f"R4 = {cpu.registers[4]} (esperado: 30)")
    print(f"R7 = {cpu.registers[7]} (esperado: 0 si el salto se tomó)")
    print(f"R10 = {cpu.registers[10]} (esperado: 0 si el salto se tomó)")
    print(f"R13 = {cpu.registers[13]} (esperado: 20)")
    
    stats = {
        "cycles": cpu.cycles,
        "instructions_completed": cpu.instructions_completed,
        "stalls_inserted": cpu.stalls_inserted,
        "branches_taken": cpu.branches_taken
    }
    print(f"\nEstadísticas: {stats}")
    print(f"Saltos tomados: {cpu.branches_taken} (esperado: 1)")

def test_memory_operations():
    """Prueba las operaciones de memoria (LOAD/STORE)."""
    print("\n=== Test 4: Operaciones de memoria (LOAD/STORE) ===")
    
    # Programa con operaciones de carga y almacenamiento en memoria
    program = [
        {"op": "ADD", "rd": 1, "rs1": 2, "rs2": 3},         # R1 = R2 + R3
        {"op": "STORE", "rs": 1, "addr": 100},              # MEM[100] = R1
        {"op": "ADD", "rd": 4, "rs1": 5, "rs2": 6},         # R4 = R5 + R6
        {"op": "STORE", "rs": 4, "addr": 104},              # MEM[104] = R4
        {"op": "LOAD", "rd": 7, "addr": 100},               # R7 = MEM[100]
        {"op": "LOAD", "rd": 8, "addr": 104},               # R8 = MEM[104]
        {"op": "ADD", "rd": 9, "rs1": 7, "rs2": 8},         # R9 = R7 + R8
    ]
    
    # Inicializar pipeline y registros
    cpu = PipelineCPU()
    cpu.load_instructions(program)
    
    cpu.registers[2] = 10
    cpu.registers[3] = 20
    cpu.registers[5] = 15
    cpu.registers[6] = 25
    
    print("Estado inicial:")
    print(f"R2 = {cpu.registers[2]}, R3 = {cpu.registers[3]}")
    print(f"R5 = {cpu.registers[5]}, R6 = {cpu.registers[6]}")
    
    # Ejecutar hasta completar todas las instrucciones
    print("\nEjecutando pipeline...")
    while any(cpu.pipeline.values()) or cpu.pc < len(cpu.instructions):
        cpu.print_state()
        cpu.step()
    
    # Verificar resultados y estadísticas
    print("\nResultados finales:")
    print(f"R1 = {cpu.registers[1]} (esperado: 30)")
    print(f"R4 = {cpu.registers[4]} (esperado: 40)")
    print(f"R7 = {cpu.registers[7]} (esperado: 30)")
    print(f"R8 = {cpu.registers[8]} (esperado: 40)")
    print(f"R9 = {cpu.registers[9]} (esperado: 70)")
    print(f"MEM[100] = {cpu.memory[100]} (esperado: 30)")
    print(f"MEM[104] = {cpu.memory[104]} (esperado: 40)")
    
    stats = {
        "cycles": cpu.cycles,
        "instructions_completed": cpu.instructions_completed,
        "stalls_inserted": cpu.stalls_inserted,
        "branches_taken": cpu.branches_taken
    }
    print(f"\nEstadísticas: {stats}")

def test_isa_encoding_decoding():
    """Prueba la codificación y decodificación de instrucciones."""
    print("\n=== Test 5: Codificación y decodificación de instrucciones ===")
    
    isa = ISA()
    
    # Instrucciones de prueba para todos los formatos
    instructions = [
        {"op": "ADD", "rd": 1, "rs1": 2, "rs2": 3},
        {"op": "SUB", "rd": 4, "rs1": 5, "rs2": 6},
        {"op": "MUL", "rd": 7, "rs1": 8, "rs2": 9},
        {"op": "LOAD", "rd": 10, "addr": 100},
        {"op": "STORE", "rs": 11, "addr": 200},
        {"op": "BEQ", "rs1": 12, "rs2": 13, "target": 5},
        {"op": "JUMP", "target": 10}
    ]
    
    print("Instrucciones originales:")
    for i, instr in enumerate(instructions):
        print(f"{i}: {isa.disassemble_instruction(instr)}")
    
    # Codificar instrucciones a formato binario
    binary_instructions = []
    for instr in instructions:
        binary = isa.encode_instruction(instr)
        binary_instructions.append(binary)
        print(f"\nInstrucción: {isa.disassemble_instruction(instr)}")
        print(f"Codificada: 0x{binary:08x}")
    
    # Decodificar instrucciones y verificar resultados
    print("\nInstrucciones decodificadas:")
    for i, binary in enumerate(binary_instructions):
        decoded = isa.decode_instruction(binary)
        print(f"{i}: {isa.disassemble_instruction(decoded)}")
        
        # Verificar que la decodificación es correcta
        original = instructions[i]
        if decoded["op"] != original["op"]:
            print(f"  ERROR: Operación incorrecta. Esperado: {original['op']}, Obtenido: {decoded['op']}")
        
        # Verificar campos según el tipo de instrucción
        if decoded["op"] in ["ADD", "SUB", "MUL"]:
            if decoded["rd"] != original["rd"] or decoded["rs1"] != original["rs1"] or decoded["rs2"] != original["rs2"]:
                print(f"  ERROR: Campos incorrectos. Esperado: rd={original['rd']}, rs1={original['rs1']}, rs2={original['rs2']}")
                print(f"  Obtenido: rd={decoded['rd']}, rs1={decoded['rs1']}, rs2={decoded['rs2']}")
        elif decoded["op"] == "LOAD":
            if decoded["rd"] != original["rd"] or decoded["addr"] != original["addr"]:
                print(f"  ERROR: Campos incorrectos. Esperado: rd={original['rd']}, addr={original['addr']}")
                print(f"  Obtenido: rd={decoded['rd']}, addr={decoded['addr']}")
        elif decoded["op"] == "STORE":
            if decoded["rs"] != original["rs"] or decoded["addr"] != original["addr"]:
                print(f"  ERROR: Campos incorrectos. Esperado: rs={original['rs']}, addr={original['addr']}")
                print(f"  Obtenido: rs={decoded['rs']}, addr={decoded['addr']}")
        elif decoded["op"] == "BEQ":
            if decoded["rs1"] != original["rs1"] or decoded["rs2"] != original["rs2"] or decoded["target"] != original["target"]:
                print(f"  ERROR: Campos incorrectos. Esperado: rs1={original['rs1']}, rs2={original['rs2']}, target={original['target']}")
                print(f"  Obtenido: rs1={decoded['rs1']}, rs2={decoded['rs2']}, target={decoded['target']}")
        elif decoded["op"] == "JUMP":
            if decoded["target"] != original["target"]:
                print(f"  ERROR: Campos incorrectos. Esperado: target={original['target']}")
                print(f"  Obtenido: target={decoded['target']}")

def run_all_tests():
    """Ejecuta todas las pruebas en secuencia."""
    test_basic_execution()
    test_data_hazards()
    test_control_hazards()
    test_memory_operations()
    test_isa_encoding_decoding()

if __name__ == "__main__":
    run_all_tests()