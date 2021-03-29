import sys
import struct

r_type_opcodes = ["00000", "11100"]
i_type_opcodes = ["00100", "00001", "01000", "01011", "00011"]
j_type_opcodes = ["00010"]

memory = {}
r = [0] * 32 #registers 0-31
pc = 96 # program counter (address of current instruction), moves in increments of 4
break_index = -1 # disassemble method will set this to index of the break instruction in machine_code arr to be used by simulation later

opcode_dict = { # for i type instructions
    # "00010": "J", # J type
    # "00000": "JR", # R type
    "00100": "BEQ", # I type
    "00001": "BLTZ", # I type
    # "00000": "ADD", # R type
    "01000": "ADDI", # I type
    # "00000": "SUB", # R type
    "01011": "SW", # I type
    "00011": "LW" # I type
    # "00000": "SLL", # R type
    # "00000": "SRL", # R type
    # "11100": "MUL", # R type
    # "00000": "AND", # R type
    # "00000": "OR", # R type
    # "00000": "MOVZ", # R type
    # "00000": "NOP" # N/A
}

opcodefcode_dict = { # for rtype instructions, key,value as opcode+fcode, instruction
    "00000001000": "JR",
    "00000100000": "ADD", #
    "00000100010": "SUB", #
    "00000000000": "SLL",
    "00000000010": "SRL",
    "11100000010": "MUL", #
    "00000100100": "AND", #
    "00000100101": "OR", #
    "00000001010": "MOVZ", #
    "00000001101": "BREAK" #
}

machine_code = []

mips_instructions = [] # will store each mips instruction as an element in the arr to be used for printing during simulation

def beq(rs, rt, offset): # if rs == rt then pc = pc + 4 + offset else pc += 4
    global pc, r

    if r[rs] == r[rt]:
        pc = pc + offset
    else:
        # pc += 4
        pass

def bltz(rs, offset):
    global pc, r

    if r[rs] < 0:
        pc = pc + offset
    else:
        # pc += 4
        pass

def addi(rt, rs, immediate):
    global r, pc

    r[rt] = r[rs] + immediate
    # pc += 4

def sw(rt, offset, base):
    global r, pc, memory

    addr = r[base] + offset
    memory[addr] = r[rt]
    # pc += 4

def lw(rt, offset, base):
    global r, pc, memory

    addr = r[base] + offset
    r[rt] = memory[addr]
    # pc += 4

def jr(rs):
    global pc, r

    pc = r[rs]

def add(rd, rs, rt):
    global pc, r

    r[rd] = r[rs] + r[rt]
    # pc += 4

def sub(rd, rs, rt):
    global pc, r

    r[rd] = r[rs] - r[rt]
    # pc += 4

def sll(rd, rt, shamt):
    global pc, r

    r[rd] = r[rt] << shamt
    # pc += 4

def srl(rd, rt, shamt):
    global pc, r

    r[rd] = r[rt] >> shamt
    # pc += 4

def mul(rd, rs, rt):
    global pc, r

    r[rd] = r[rs] * r[rt]
    # pc += 4

def and_m(rd, rs, rt):
    global pc, r

    r[rd] = r[rs] & r[rt]
    # pc += 4

def or_m(rd, rs, rt):
    global pc, r

    r[rd] = r[rs] | r[rt]
    # pc += 4

def movz(rd, rs, rt):
    global pc, r

    if r[rt] == 0:
        r[rd] = r[rs]

    # pc += 4

def j(target):
    global pc

    pc_bitstring = format(pc, 'b')

    for i in range(32-len(pc_bitstring)):
        pc_bitstring = "0" + pc_bitstring

    high_4_bits = pc_bitstring[0:4]

    target = high_4_bits + target
    target = twos_comp(int(target, 2), len(target))

    pc = target

def break_m():
    pass



def twos_comp(val, bits): #given integer value and amount of bits, returns signed integer
    if(val & (1 << (bits - 1))) != 0:
        val = val - (1 << bits)
    return val


def pc_to_index(pc): # converts program counter to index of instruction in machine_code arr
    return int((pc-96) / 4)


# reads binary file and stores bitstring of each mips instruction as element in machine_code global array
def read_binary(filename):
    in_file = open(filename, 'rb')

    while True:

        bitsInStrForm = in_file.read(4)
        if len(bitsInStrForm) == 0:
            break

        test = struct.unpack(">I", bitsInStrForm)[0]
        bitstring = bin(test)[2:]
        for i in range(32-len(bitstring)):
            bitstring = "0" + bitstring

        machine_code.append(bitstring)
        # print(bitstring)


def generate_mips_assembly(filename):

    global mips_instructions, break_index, machine_code

    in_file = open(filename, 'r')

    # for line in in_file:
    #     mips_instructions.append(line[42:len(line)])

    for i in range(break_index+1):
        mips_instructions.append(in_file.readline()[42:].strip())

    # count = mips_instructions.count("Invalid Instruction")
    #
    # for i in range(count):
    #     mips_instructions.remove("Invalid Instruction")

    # print(mips_instructions)
    # print(len(mips_instructions))

    machine_code = machine_code[0:break_index+1]
    # print(machine_code)
    # print(len(machine_code))




# disassemble machine_code global array and print results to output_file
def disassemble(output_file):

    global pc, r_type_opcodes, j_type_opcodes, i_type_opcodes, opcodefcode_dict, opcode_dict, break_index, memory

    out_file = open(output_file, 'w')

    break_hit = False #set to True once we hit BREAK instruc

    for instruction in machine_code:

        if break_hit: # parse as data
            out_file.write(instruction + " " + str(pc) + " " + str(twos_comp(int(instruction, 2), len(instruction))) + "\n")
            memory[pc] = twos_comp(int(instruction, 2), len(instruction))
            pc += 4
        else: # parse as instruction
            valid = instruction[0:1]
            opcode = instruction[1:6]
            rs = instruction[6:11]
            rt = instruction[11:16]
            rd = instruction[16:21]
            shamt = instruction[21:26]
            fcode = instruction[26:32]
            immediate = rd + shamt + fcode # for i type instructions
            address = rs + rt + immediate + "00" # for j type instructions (jump)

            if valid == "0":
                out_file.write(valid +" "+ opcode +" "+ rs +" "+ rt +" "+ rd +" "+ shamt +" "+ fcode +" "+ str(pc) +" "+ "Invalid Instruction\n")
            else: # valid instruction
                if opcode in r_type_opcodes:
                    opcode_txt = opcodefcode_dict[opcode+fcode]

                    if opcode_txt == "BREAK":
                        out_file.write(valid +" "+ opcode +" "+ rs +" "+ rt +" "+ rd +" "+ shamt +" "+ fcode +" "+ str(pc) +" "+ opcode_txt +"\n")
                        break_hit = True
                        break_index = int((pc - 96) / 4)
                        # print(break_index)

                    elif opcode_txt in ["ADD", "SUB", "MUL", "AND", "OR", "MOVZ"]: # std format instructions: opcode rd, rs, rt
                        out_file.write(valid +" "+ opcode +" "+ rs +" "+ rt +" "+ rd +" "+ shamt +" "+ fcode +" "+ str(pc) +" "+ opcode_txt +"\t")
                        out_file.write("R" + str(int(rd, 2)) + ", " + "R" + str(int(rs, 2)) + ", " + "R" + str(int(rt, 2)) + "\n")

                    elif opcode_txt in ["SLL", "SRL"]: # shift format instructions: opcode rd, rt, shamt
                        if int(rd, 2) == int(rt, 2) and int(shamt, 2) == 0: #NOP
                            out_file.write(valid +" "+ opcode +" "+ rs +" "+ rt +" "+ rd +" "+ shamt +" "+ fcode +" "+ str(pc) +" "+ "NOP" +"\n")
                        else:
                            out_file.write(valid +" "+ opcode +" "+ rs +" "+ rt +" "+ rd +" "+ shamt +" "+ fcode +" "+ str(pc) +" "+ opcode_txt +"\t")
                            out_file.write("R" + str(int(rd, 2)) + ", R" + str(int(rt, 2)) + ", #" + str(int(shamt, 2)) + "\n")

                    else: # JR format r type instruction: JR rs
                        out_file.write(valid +" "+ opcode +" "+ rs +" "+ rt +" "+ rd +" "+ shamt +" "+ fcode +" "+ str(pc) +" "+ opcode_txt +"\t")
                        out_file.write("R" + str(int(rs, 2)) + "\n")

                elif opcode in j_type_opcodes:
                    out_file.write(valid +" "+ opcode +" "+ rs +" "+ rt +" "+ rd +" "+ shamt +" "+ fcode +" "+ str(pc) +" "+ "J" +"\t")
                    out_file.write("#" + str(int(address, 2)) + "\n")
                elif opcode in i_type_opcodes:
                    opcode_txt = opcode_dict[opcode]
                    out_file.write(valid +" "+ opcode +" "+ rs +" "+ rt +" "+ rd +" "+ shamt +" "+ fcode +" "+ str(pc) +" "+ opcode_txt +"\t")

                    if opcode_txt == "BEQ":
                        immediate += "00"
                        out_file.write("R" + str(int(rs, 2)) + ", R" + str(int(rt, 2)) + ", #" + str(twos_comp(int(immediate, 2), len(immediate))) + "\n")
                    elif opcode_txt == "BLTZ":
                        immediate += "00"
                        out_file.write("R" + str(int(rs, 2)) + ", #" + str(twos_comp(int(immediate, 2), len(immediate))) + "\n")
                    elif opcode_txt == "ADDI":
                        out_file.write("R" + str(int(rt, 2)) + ", R" + str(int(rs, 2)) + ", #" + str(twos_comp(int(immediate, 2), len(immediate))) + "\n")
                    else: # SW or LW
                        out_file.write("R" + str(int(rt, 2)) + ", " + str(twos_comp(int(immediate, 2), len(immediate))) + "(R" + str(int(rs, 2)) + ")\n")

            pc += 4

        print(instruction[0:1], instruction[1:6], instruction[6:11], instruction[11:16], instruction[16:21], instruction[21:26], instruction[26:32])


def execute(instruction): # instruction is bitstring of instruction, return -1 for invalid instructions and 0 for succesfully completed instructions

    global pc, memory, machine_code, mips_instructions, r, r_type_opcodes, i_type_opcodes, j_type_opcodes, opcodefcode_dict, opcode_dict

    valid = instruction[0:1]
    opcode = instruction[1:6]
    rs = instruction[6:11]
    rt = instruction[11:16]
    rd = instruction[16:21]
    shamt = instruction[21:26]
    fcode = instruction[26:32]
    immediate = rd + shamt + fcode # for i type instructions
    address = rs + rt + immediate + "00" # for j type instructions (jump)

    # print("Executing:", instruction)

    if valid == "0": #instruction invalid
        pc += 4
        return -1 # -1 signals invalid instruction to simulate()
    pc += 4
    if opcode in r_type_opcodes:
        opcode_txt = opcodefcode_dict[opcode+fcode]
        print(opcode_txt)

        if opcode_txt == "JR":
            jr(int(rs, 2)) #jumps to address in rs register
            return 0
        elif opcode_txt == "ADD":
            add(int(rd, 2), int(rs, 2), int(rt, 2))
            return 0
        elif opcode_txt == "SUB":
            sub(int(rd, 2), int(rs, 2), int(rt, 2))
            return 0
        elif opcode_txt == "SLL":
            sll(int(rd, 2), int(rt, 2), int(shamt, 2))
            return 0
        elif opcode_txt == "SRL":
            srl(int(rd, 2), int(rt, 2), int(shamt, 2))
            return 0
        elif opcode_txt == "MUL":
            mul(int(rd, 2), int(rs, 2), int(rt, 2))
            return 0
        elif opcode_txt == "AND":
            and_m(int(rd, 2), int(rs, 2), int(rt, 2))
            return 0
        elif opcode_txt == "OR":
            or_m(int(rd, 2), int(rs, 2), int(rt, 2))
            return 0
        elif opcode_txt == "MOVZ":
            movz(int(rd, 2), int(rs, 2), int(rt, 2))
            return 0
        elif opcode_txt == "BREAK":
            return -2 # -2 return value signals break has been hit, will be used in simulate()


    elif opcode in i_type_opcodes:
        opcode_txt = opcode_dict[opcode]
        print(opcode_txt)

        if opcode_txt == "BEQ":
            offset = immediate + "00"
            offset = twos_comp(int(offset, 2), len(offset))
            beq(int(rs, 2), int(rt, 2), offset)
            return 0
        elif opcode_txt == "BLTZ":
            offset = immediate + "00"
            offset = twos_comp(int(offset, 2), len(offset))
            bltz(int(rs, 2), offset)
            return 0
        elif opcode_txt == "ADDI":
            immediate = twos_comp(int(immediate, 2), len(immediate))
            addi(int(rt, 2), int(rs, 2), immediate)
            return 0
        elif opcode_txt == "SW":
            base = int(rs, 2)
            offset = twos_comp(int(immediate, 2), len(immediate))
            sw(int(rt, 2), offset, base)
            return 0
        elif opcode_txt == "LW":
            base = int(rs, 2)
            offset = twos_comp(int(immediate, 2), len(immediate))
            lw(int(rt, 2), offset, base)
            return 0

    elif opcode in j_type_opcodes:
        print("J")
        j(address)
        return -3




def simulate(filename):
    # at the start of this method machine_code will contain binary of all instructions up to and including the break
    # mips_instructions will contain assembly code that relates to same index of machine_code binary instruction
    # this method will deal with the printing and formatting while execute() will actually simulate the execution of the instructions
    global memory, r, pc, machine_code, mips_instructions

    pc = 96

    cc = 1 # clock cycle

    done = False
    out_file = open(filename, 'w')

    while not done:
        instruc_index = pc_to_index(pc)
        error_code = execute(machine_code[instruc_index])
        print(pc)
                                                    # -3 for jump
        if error_code == 0 or error_code == -2 or error_code == -3: # succesfull instruction, print processor state and update cc
            out_file.write("====================\n")
            # if error_code == -3:
            #     pc -= 4
            out_file.write("cycle:" + str(cc) + "\t" + str((instruc_index*4)+96) + "\t" + mips_instructions[instruc_index] + "\n\n")
            # if error_code == -3:
            #     pc += 4
            out_file.write("registers:\n")
            out_file.write("r00:\t" + str(r[0]) + "\t" + str(r[1]) + "\t" + str(r[2]) + "\t" + str(r[3]) + "\t" + str(r[4]) + "\t" + str(r[5]) + "\t" + str(r[6]) + "\t" + str(r[7]) + "\n")
            out_file.write("r08:\t" + str(r[8]) + "\t" + str(r[9]) + "\t" + str(r[10]) + "\t" + str(r[11]) + "\t" + str(r[12]) + "\t" + str(r[13]) + "\t" + str(r[14]) + "\t" + str(r[15]) + "\n")
            out_file.write("r16:\t" + str(r[16]) + "\t" + str(r[17]) + "\t" + str(r[18]) + "\t" + str(r[19]) + "\t" + str(r[20]) + "\t" + str(r[21]) + "\t" + str(r[22]) + "\t" + str(r[23]) + "\n")
            out_file.write("r24:\t" + str(r[24]) + "\t" + str(r[25]) + "\t" + str(r[26]) + "\t" + str(r[27]) + "\t" + str(r[28]) + "\t" + str(r[29]) + "\t" + str(r[30]) + "\t" + str(r[31]) + "\n\n")
            out_file.write("data:\n")

            data_start_addr = list(memory)[0]
            data_addresses = list(memory)
            data_points = len(list(memory))

            count = 0
            new_line_done = False

            for addr in data_addresses:
                if count == 0:
                    out_file.write(str(addr) + ":\t")

                out_file.write(str(memory[addr]))
                count+=1

                if count == 8:
                    out_file.write("\n")
                    count = 0
                    new_line_done = True
                else:
                    out_file.write("\t")
                    new_line_done = False

            if new_line_done:
                out_file.write("\n")
            else:
                out_file.write("\n\n")

            cc += 1

            if error_code == -2: #break hit, set done to true to stop simulation
                done = True

        elif error_code == -1: # invalid instruction, do nothing
            pass

        # pc += 4





    print(memory)



if __name__ == "__main__":
    read_binary(sys.argv[1]) # command line arg -> input file name
    disassemble(sys.argv[2] + "_dis.txt") # command line arg -> output file name
    generate_mips_assembly(sys.argv[2] + "_dis.txt") # generates mips assembly for printing and removes data from machine_code arr since it is now stored in memory dict
    simulate(sys.argv[2] + "_sim.txt")
    # print(machine_code)
