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
                else:
                    self.lineBuffer.append(tokens[0])

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


