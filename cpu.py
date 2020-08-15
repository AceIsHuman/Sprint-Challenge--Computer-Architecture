HLT  = 0b00000001
LDI  = 0b10000010
PRN  = 0b01000111
ADD  = 0b10100000
MUL  = 0b10100010
PUSH = 0b01000101
POP  = 0b01000110
CALL = 0b01010000
RET  = 0b00010001
CMP  = 0b10100111
JMP  = 0b01010100
JEQ  = 0b01010101
JNE  = 0b01010110
AND  = 0b10101000

"""CPU functionality."""

import sys

class CPU:
    """Main CPU class."""

    def __init__(self):
        """Construct a new CPU."""
        self.ram = [0] * 256
        self.reg = [0] * 8
        # R5 is reserved as the interrupt mask (IM)
        # R6 is reserved as the interrupt status (IS)
        # R7 is reserved as the stack pointer (SP)
        self.reg[7] = 0xF4
        self.pc = 0
        self.running = False
        self.fl = 0

        self.instructions = {}
        self.instructions[HLT] = self.hlt
        self.instructions[LDI] = self.ldi
        self.instructions[PRN] = self.prn
        self.instructions[ADD] = self.add
        self.instructions[MUL] = self.mul
        self.instructions[PUSH] =self.push
        self.instructions[POP] = self.pop
        self.instructions[CALL] =self.call
        self.instructions[RET] = self.ret
        self.instructions[CMP] = self.cmp
        self.instructions[JMP] = self.jmp
        self.instructions[JEQ] = self.jeq
        self.instructions[JNE] = self.jne
        self.instructions[AND] = self.aluand

    def load(self, path):
        """Load a program into memory."""

        address = 0

        # For now, we've just hardcoded a program:

        try:
            with open(path) as file:
                for line in file:
                    comment_split = line.split('#')
                    possible_num = comment_split[0]

                    if possible_num == '':
                        continue

                    if possible_num[0] == '1' or possible_num[0] == '0':
                        num = possible_num[:8]
                        self.ram_write(int(num, 2), address)
                        address += 1
            file.close()
        except FileNotFoundError:
            print(f'{path} not found.')

    def alu(self, op, reg_a, reg_b):
        """ALU operations."""

        if op == "ADD":
            self.reg[reg_a] += self.reg[reg_b]
        # elif op == "SUB": etc
        elif op == "MUL":
            self.reg[reg_a] *= self.reg[reg_b]
        elif op == "CMP":
            if self.reg[reg_a] < self.reg[reg_b]:
                self.fl = 0b0100
            elif self.reg[reg_a] > self.reg[reg_b]:
                self.fl = 0b0010
            else: self.fl = 0b0001
        elif op == "AND":
            self.reg[reg_a] &= self.reg[reg_b]
        else:
            raise Exception("Unsupported ALU operation")

    def trace(self):
        """
        Handy function to print out the CPU state. You might want to call this
        from run() if you need help debugging.
        """

        print(f"TRACE: %02X | %02X %02X %02X |" % (
            self.pc,
            # self.fl,
            # self.ie,
            self.ram_read(self.pc),
            self.ram_read(self.pc + 1),
            self.ram_read(self.pc + 2)
        ), end='')

        for i in range(8):
            print(" %02X" % self.reg[i], end='')

        print()

    def run(self):
        """Run the CPU."""

        self.running = True
        # read memory address stored in PC
        # store in IR

        while self.running:
            ir = self.ram_read(self.pc)
            num_operands = ir >> 6
            op_a, op_b = self.ram_read(self.pc + 1), self.ram_read(self.pc + 2)

            self.instructions[ir](op_a, op_b)

            prevent_pc_update = (ir >> 4) & 1
            if prevent_pc_update:
                continue
            self.pc += num_operands + 1 

    def ram_read(self, mar):
        return self.ram[mar]

    def ram_write(self, mdr, mar):
        self.ram[mar] = mdr

    def hlt(self, *_):
        print('Shutting Down... Goodbye')
        self.running = False
        sys.exit(0)

    def ldi(self, reg, val):
        self.reg[reg] = val

    def prn(self, reg, _):
        print(self.reg[reg])

    def add(self, op_a, op_b):
        self.alu("ADD", op_a, op_b)

    def mul(self, op_a, op_b):
        self.alu("MUL", op_a, op_b)

    def cmp(self, op_a, op_b):
        self.alu("CMP", op_a, op_b)

    def aluand(self, reg_a, reg_b):
        self.alu("AND", reg_a, reg_b)

    def call(self, inst_address, _):
        # get the next instruction address
        next_address = self.pc + 2
        ## store in stack
        self.reg[7] -= 1
        self.ram_write(next_address, self.reg[7])

        # go to instruction
        self.pc = self.reg[inst_address]

    def ret(self, *_):
        ret_address = self.ram_read(self.reg[7])
        self.pc = ret_address
        self.reg[7] += 1

    def jmp(self, reg, _):
        self.pc = self.reg[reg]

    def jeq(self, reg, _):
        if self.fl == 0b0001:
            self.pc = self.reg[reg]
        else:
            self.pc = self.pc + 2

    def jne(self, reg, _):
        e = self.fl & 0b0001
        if not e:
            self.pc = self.reg[reg]
        else:
            self.pc = self.pc + 2

    def push(self, reg, _):
        # decrement stack pointer
        self.reg[7] -= 1
        # read register value
        val = self.reg[reg]
        # write to ram at stack pointer
        self.ram_write(val, self.reg[7])        

    def pop(self, reg, _):
        # get value at current stack pointer address
        val = self.ram_read(self.reg[7])
        # store value at given register
        self.reg[reg] = val
        # increment stack pointer
        self.reg[7] += 1

