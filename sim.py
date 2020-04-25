import json
from pp import *

class SimAlu:
    debug = 1
    def __init__(self):
        self.neg = 0
        self.zero = 0
        self.ovf = 0
        self.carry = 0
        self.acc = 0x0

    def __Update(self):
        self.ovf = not (self.acc >> 32)
        self.neg = self.acc < 0
        self.zero = not self.acc
        self.carry = self.acc & 0x100000000
        self.acc = 0

    def Cmp(self, cpu, rn, rm):
        self.acc = cpu.rg[rn] - cpu.rg[rm]
        self.__Update()
        if (SimAlu.debug):
            print('Cmp : [', rn, ']=', hex(cpu.rg[rn]), '[', rm, ']=', hex(cpu.rg[rm]), self.zero)
    
    def Addi32(self, cpu, rn, imm):
        self.acc = cpu.rg[rn] + imm
        cpu.rg[rn] = self.acc
        self.__Update()

class SimCpu:

    def __InitMemory(self):
        for i in range(self.memorySize):
            self.memory[i] = 0xff
        for i in range(self.regSize):
            self.rg[i] = 0

    def __init__(self, simPath):
        self.alu = SimAlu()
        self.rg = []
        self.pc_next = 0x0
        self.halt = 0
        jsonc = ''
        with open(simPath, 'r') as simConf:
            jsonc = simConf.read()
        jsondict = json.loads(jsonc)
        isa = jsondict['isa']
        self.instructions = isa['instructions']

    def Config(self, isa, wordWidth, memSize, regSize=16):
        self.rg = regSize * [None]
        self.regSize = regSize
        self.memory = memSize * [None]
        self.memorySize = memSize
        self.width =int(wordWidth / 8)
        self.pc_rn = int(isa.regmap['pc'])

        self.__InitMemory()

    def Startup(self, binArray, address=0):
        for byte in binArray:
            self.memory[address] = byte
            address += 1

    def getSimFunc(self, name):
        for inst in self.instructions:
            if inst['name'] == name:
                return inst
        return None

    def Eval(self, isaInst, sim, pc):
        args = []
        for arg in sim['args'].split():
            args.append(isaInst.mapObj(arg, pc))

        if len(sim['func']):
            simFunc = eval(sim['func'])
            simFunc(self, args)

    def Decode(self, isa):
        self.pc_addr = self.rg[self.pc_rn]
        pc = self.LdmLe(self.pc_addr, self.width)

        isaInst = isa.getByOpcode(pc)
        if isaInst is None:
            raise ValueError

        self.rg[self.pc_rn] = self.pc_addr + isaInst.width

        print('\n* addr: ', hex(self.pc_addr), hex(pc), isaInst.mnemonic)

        sim = self.getSimFunc(isaInst.mnemonic)
        if sim is None:
            raise ValueError

        self.Eval(isaInst, sim, pc)

    def Execute(self, isa):
        while not self.halt:
            self.Decode(isa)

    def JnzCond(self, imm, cond):
        print('JnzCond : ', imm, cond)
        if cond:
            if imm & 0x80:
                imm = -(0x100 - imm)
            self.rg[self.pc_rn] = self.pc_addr + imm

    def Addi(self, rn, imm):
        print('Addi : ', rn, imm, hex(self.rg[rn]))
        self.rg[rn] += imm
        return self.rg[rn]

    def Addia(self, rn, imm):
        print('Addia : ', rn, imm,  hex(self.rg[rn]))
        tmp = self.rg[rn]
        self.rg[rn] += imm
        return tmp

    def Movw(self, rn, word):
        print('Movw', rn, hex(word))
        self.rg[rn] = word

    def Movr(self, rn, rm):
        print('Movr', rn, rm)
        self.rg[rn] = self.rg[rm]

    def StmLe (self, dst, src, width):
        print('StmLe : ', hex(dst), hex(src), width)
        if width not in [1, 2, 4]:
            raise ValueError
        i = 0
        shift = 0
        while i != width:
            self.memory[dst + i] = (src >> shift) & 0xff
            shift += 8
            i += 1
        return 0

    def LdmLe (self, src, width):
        if width not in [1, 2, 4]:
            raise ValueError
        shift = 0
        val = 0x0
        for m in self.memory[src:src+width]:
            val |= (m & 0xff) << shift
            shift += 8
        print('LdmeLe : ', hex(val), hex(src), width)
        return val
    
    def Halt(self):
        self.halt = True

    def DumpRegs(self):
        print('Registers dump :')
        i = 0
        for r in self.rg:
            print('r[', i, ']=', hex(r))
            i += 1
    def DumpMem(self, start, stop):
        print('DumpMem ', hex(start), hex(stop))
        for m in self.memory[start:stop+1]:
            print(hex(m))
