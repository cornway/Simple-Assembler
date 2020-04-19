from jsonp import *
from asmp import *

class AsmAlias:

    def __init__(self, filePath):
        self.rawLineBuffer = []
        self.lineBuffer = []
        with open(filePath, 'r') as asmFile:
            for line in asmFile:
                self.rawLineBuffer.append(line)

    def RemoveComments(self):
        multilineBegin = 0
        for raw in self.rawLineBuffer:
            #single line comment
            tokens = raw.split('//')
            if len(tokens) > 1:
                if len(tokens[0]) > 0:
                    self.lineBuffer.append(tokens[0])
            else:
                if '/*' not in raw and '*/' not in raw:
                    self.lineBuffer.append(raw)
                elif '/*' in raw:
                    tokens = raw.split('/*')
                    if len(tokens) > 1:
                        if len(tokens[0]) > 0:
                            self.lineBuffer.append(tokens[0])
                        multilineBegin = 1
                elif multilineBegin:
                    tokens = raw.split('*/')
                    if len(tokens) > 1:
                        if len(tokens[1]) > 0:
                            self.lineBuffer.append(tokens[0])
                        multilineBegin = 0

    def ApplyAlias(asmToken_in, isa):
        mnemonic = asmToken_in.tokens[0]
        alias = isa.containsAlias(mnemonic)
        if alias is None:
            return None
        else:
            i = 1
            asmToken = asmToken_in
            asmToken.tokens[0] = alias['alias']
            for arg in IsaInstruction.objNames[1:]:
                if len(alias[arg]) > 0 and alias[arg][0] in '%':
                    temp = int(alias[arg][1:])
                    if temp > 3:
                        print('Garbage')
                    asmToken.tokens[i] = asmToken_in.tokens[temp]
                elif len(alias[arg]):
                    asmToken.tokens[i] = alias[arg]
                i += 1
        return asmToken

    def subAlias(self, token, alias):
        return alias

    def PrintRaw(self):
        print("******** Raw :")
        for line in self.rawLineBuffer:
            print(line)

    def PrintPost(self):
        print("******** Post :")
        for line in self.lineBuffer:
            print(line)

class Parse:
    def ParseInt32Le (token):
        const = 0
        try:
            const = int(token)
        except ValueError:
            try:
                const = int(token, 16)
            except ValueError:
                raise ValueError('')
        return const

    def Tokenize(lineStr):
        odd = 0
        tokens = []
        for token in lineStr.split('"'):
            if not odd:
                for stoken in token.split():
                    rtoken = stoken.replace(' ', '')
                    if len(rtoken) > 0:
                        tokens.append(rtoken)
            else:
                tokens.append(token)
            odd = 1 - odd
        return tokens

    def appendConstLe (constArray, const, width):
        if width == 1:
            constArray.append(const & 0xff)
        if width == 2:
            constArray.append(const & 0xff)
            constArray.append((const >> 8) & 0xff)
        elif width == 4:
            constArray.append(const & 0xff)
            constArray.append((const >> 8) & 0xff)
            constArray.append((const >> 16) & 0xff)
            constArray.append((const >> 24) & 0xff)
        else:
            raise ValueError
        return width

    def appendBytes(constArray, byte, len):
        _len = len
        while len > 0:
            constArray.append(byte)
            len -= 1
        return _len

    def appendAsciiz(constArray, asciiz):
        width = 0
        for char in asciiz:
            if char != '"':
                constArray.append(ord(char) & 0xff)
                width += 1
        constArray.append(0)
        return width + 1
