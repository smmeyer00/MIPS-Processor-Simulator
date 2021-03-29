# MIPS Processor Simulator
## Author: Steven Meyer
## Description
Simulates a basic MIPS processor (not all instructions). Takes MIPS instructions as binary (32 bit words) disassembles them to produce 
mips assembly, and runs the instructions in a simulated processor. Shows processor state (clock cycle, program counter, current instruction, registers, 
and data in memory) after every clock cycle.
## Usage
python3 mipssim.py INPUTFILENAME OUTPUTFILENAME
### Example: python3 mipssim.py test1.bin mytest1
Above example will take binary file test1, simulate execution, and produce mytest1_sim.txt (simulation) and mytest1_dis.txt (disassembled code)
