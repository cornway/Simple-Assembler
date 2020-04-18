from jsonp import *
from pp import *

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
        self.allign = 0

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
                const = int(token, 16)
                iwidth = self.__appendConstLe(const, iwidth)
                if iwidth == 0:
                    print("Garbage at ", lineNum, ' Line')
            elif itype == 'label':
                self.label = token
                self.labelLsb = ilsb
                self.labelMask = imask
            elif itype == 'label_far':
                self.label = token
                self.labelFar = 1
            elif itype == 'asciz':
                token = asmTok.tokens[i + 1]
                width = self.__appendAsciiz(token)
                break
            elif itype == 'allign':
                self.allign = int(asmTok.tokens[i + 1])
                break
            elif itype != 'word':
                print("Garbage at ", lineNum, ' Line')
            i = i + 1

        self.opcode = opcode
        self.opcodeWidth = instruction.objs['mnemonic'].width
        self.width = width

    def appendBytes(self, byte, len):
        _len = len
        while len > 0:
            self.constArray.append(byte)
            len -= 1
        return _len

    def __appendConstLe (self, const, width):
        twidth = width
        if width == 1:
            self.constArray.append(const & 0xff)
        if width == 2:
            self.constArray.append(const & 0xff)
            self.constArray.append((const >> 8) & 0xff)
        elif width == 4:
            self.constArray.append(const & 0xff)
            self.constArray.append((const >> 8) & 0xff)
            self.constArray.append((const >> 16) & 0xff)
            self.constArray.append((const >> 24) & 0xff)
        else:
            twidth = 0
        return twidth

    def __appendAsciiz(self, asciiz):
        width = 0
        for char in asciiz:
            if char != '"':
                self.constArray.append(ord(char) & 0xff)
                width += 1
        self.constArray.append(0)
        return width + 1


    def Resolve(self, curAddr=0x0, labelAddr=0x0):

        opcode = self.opcode
        if len(self.label) > 0:
            if (self.labelFar):
                self.__appendConstLe(labelAddr, 4)
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

    def ParseAlias(self, isa):
        addr = 0
        lineNum = 0
        tokens = self.tokens
        self.tokens = []
        for token in tokens:
            if len(token.tokens) > 0:
                alias = AsmAlias.ApplyAlias(token, isa)
                if alias is not None:
                    self.tokens.append(alias)
                else:
                    self.tokens.append(token)

    def ParseTokens(self, isa):
        addr = 0
        lineNum = 0
        for token in self.tokens:
            if len(token.tokens) > 0:
                instruction = isa.get(token.tokens[0])

                unresolved = AsmUnresolved()
                unresolved.Parse(lineNum, instruction, token)
                if AsmParser.debug:
                    instruction.Print()
                    unresolved.Print()

                self.unresolved.append(unresolved)
                lineNum = lineNum + 1

    def __ParseSection(self, u, curAddr):
        if u.allign > 0:
            rem = curAddr % u.allign
            rem = u.allign - rem
            u.appendBytes(0, rem)
            u.width += rem
            return 1
        return 0

    def ParseSections(self, isa):
        lineNum = 0
        tlen = 0
        addr = 0
        unresolved = self.unresolved
        self.unresolved = []
        for u in unresolved:

            self.__ParseSection(u, addr)
            print(hex(addr), tlen)
            self.labelsResolved[lineNum] = addr
            self.unresolved.append(u)
            lineNum += 1
            addr += u.width

    def Resolve(self, isa):
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

    def PrintTokens (self):
        print('Tokens ********')
        for token in self.tokens:
            token.Print()

    def Print(self):
        print('Tokens ********')
        for token in self.tokens:
            token.Print()
        print('Labels ********')
        for label, num in self.labels.items():
            print(label, num)