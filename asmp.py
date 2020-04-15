from jsonp import *

class AsmToken:
    def __init__(self, lineStr='', lineNum=0):
        rtokens = lineStr.split()
        self.tokens = []
        self.lineNum = lineNum
        for rtoken in rtokens:
            token = rtoken.replace(' ', '')
            if len(token) > 0:
                self.tokens.append(token)
                self.lineNum = lineNum

    def Print(self):
        if (self.lineNum >= 0):
            print('========', self.lineNum)
            for token in self.tokens:
                print(token)

class AsmUnresolved:

    def __init__(self):
        self.label = ''
        self.labelLsb = -1
        self.labelMask = 0x0
        self.constArray = []
        self.labelFar = 0

    def Parse(self, lineNum, instruction, asmTok=[]):
        byteArray = []
        constArray = []
        opcode = 0x00000000
        temp = 0x00000000
        width = 0
        i = 0

        for token in asmTok.tokens:

            iname = IsaInstruction.objNames[i]
            itype = instruction.objs[iname].type
            imask = instruction.objs[iname].mask
            iwidth = instruction.objs[iname].width
            ilsb = instruction.objs[iname].lsb

            width += iwidth

            if itype == 'opcode':
                temp = imask & instruction.opcode
                opcode = temp << ilsb
            elif itype == 'reg':
                temp = int(token[1:])
                if temp <= imask:
                    temp = temp << ilsb
                    opcode = opcode | temp
                else:
                    print("Garbage at ", lineNum, ' Line')
            elif itype == 'imm':
                temp = int(token)
                if temp <= imask:
                    temp = temp << ilsb
                    opcode = opcode | temp
                else:
                    print("Garbage at ", lineNum, ' Line')
            elif itype == 'const':
                temp = int(token, 16)
                if (iwidth == 2):
                    self.constArray.append(temp & 0xff)
                    self.constArray.append((temp >> 8) & 0xff)
                elif (iwidth == 4):
                    self.constArray.append(temp & 0xff)
                    self.constArray.append((temp >> 8) & 0xff)
                    self.constArray.append((temp >> 16) & 0xff)
                    self.constArray.append((temp >> 24) & 0xff)
                else:
                    print("Garbage at ", lineNum, ' Line')
            elif itype == 'label':
                self.label = token
                self.labelLsb = ilsb
                self.labelMask = imask
            elif itype == 'label_far':
                self.label = token
                self.labelFar = 1
            else:
                print("Garbage at ", lineNum, ' Line')
            i = i + 1

        i = 0
        self.opcode = opcode
        self.opcodeWidth = instruction.objs['mnemonic'].width

        return width

    def Resolve(self, curAddr=0x0, labelAddr=0x0):

        opcode = self.opcode
        if len(self.label) > 0:
            if (self.labelFar):
                self.constArray.append(labelAddr & 0xff)
                self.constArray.append((labelAddr >> 8) & 0xff)
                self.constArray.append((labelAddr >> 16) & 0xff)
                self.constArray.append((labelAddr >> 24) & 0xff)
            else:
                offset = (labelAddr - curAddr) & self.labelMask
                offset = offset << self.labelLsb
                opcode |= offset

        byteArray = []
        i = 0
        while i < self.opcodeWidth:
            byteArray.append(opcode & 0xff)
            opcode = opcode >> 8
            i = i + 1
        for const in self.constArray:
            byteArray.append(const)

        return byteArray

    def Print(self):
        print('Unresolved: ', hex(self.opcode), self.label)

class AsmParser:
    debug = 0

    def __init__(self, lineBuffer):
        
        lineNum = 0
        self.labels = {}
        self.tokens = []
        self.labelsResolved = {}
        self.unresolved = []
        for line in lineBuffer:
            #Skip empty lines
            if line[0] == '\n':
                continue
            tokens = line.split(':')
            asmTok = tokens[0]
            if len(tokens) > 1:
                #label present
                token = tokens[0].replace(' ', '')
                if len(token) > 0:
                    self.labels[token] = lineNum
                else:
                    print('Error #0')
                asmTok = tokens[1]

            if AsmParser.debug:
                print(lineNum, ': Token', asmTok)

            self.tokens.append(AsmToken(asmTok, lineNum))
            lineNum = lineNum + 1

    def Phase_1(self, isa):
        addr = 0
        lineNum = 0
        for token in self.tokens:
            if len(token.tokens) > 0:
                instruction = isa.get(token.tokens[0])

                unresolved = AsmUnresolved()
                unresLen = unresolved.Parse(lineNum, instruction, token)
                if AsmParser.debug:
                    instruction.Print()
                    unresolved.Print()

                self.unresolved.append(unresolved)
                self.labelsResolved[lineNum] = addr

                addr = addr + unresLen
                lineNum = lineNum + 1


    def Phase_2(self, isa):
        lineNum = 0
        addr = 0
        binaryArray = []
        for u in self.unresolved:
            labelAddr = 0
            if len(u.label):
                labelLineNum = self.labels[u.label]
                labelAddr = self.labelsResolved[labelLineNum]
                addr = self.labelsResolved[lineNum]

            byteArray = u.Resolve(addr, labelAddr)

            if AsmParser.debug:
                print('Bytes: ', byteArray)

            for b in byteArray:
                binaryArray.append(b)

            lineNum = lineNum + 1

        return binaryArray

    def Print(self):
        print('Tokens ********')
        for token in self.tokens:
            token.Print()
        print('Labels ********')
        for label, num in self.labels.items():
            print(label, num)