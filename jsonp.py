import json

class IsaInstObj:

    def __init__(self, name, map, mask, type, width):
        lsb_msb = map.split(':')
        self.lsb = -1
        self.msb = -1
        self.name = name
        if len(lsb_msb) == 2:
            self.lsb = int(lsb_msb[1])
            self.msb = int(lsb_msb[0])

        if len(mask) > 0:
            self.mask = int(mask, 16)
        else:
            self.mask = 0x00

        if len(type):
            self.type = type
        else:
            self.type = ''
        self.width = int(width, 16)

class IsaInstruction:
    objTypes = ['opcode', 'const', 'imm', 'reg', 'label']
    objNames = ['mnemonic', 'p1', 'p2', 'p3']

    def __init__(self):
        self.opcode = 0x00
        self.opname = ''

    def __init__(self, jsonDict):

        isaObjsMap = jsonDict['map']
        isaObjMask = jsonDict['mask']
        isaObjType = jsonDict['type']
        isaObjWidth = jsonDict['width']
        isaMnemonic = jsonDict['mnemonic']

        self.objs = {}
        for name in IsaInstruction.objNames:
            objMap = isaObjsMap[name]
            objMask = isaObjMask[name]
            objType = isaObjType[name]
            objWidth = isaObjWidth[name]
            isaInstObj = IsaInstObj(isaMnemonic, objMap, objMask, objType, objWidth)
            self.objs[name] = isaInstObj

        self.opcode = int(jsonDict['opcode'], 16)
        self.mnemonic = isaMnemonic

    def Print(self):
        print('========', self.mnemonic, hex(self.opcode))
        for obj in self.objs.values():
            if len(obj.type):
                print('<', obj.type, '[', obj.msb, ':', obj.lsb, ']', obj.mask, obj.width, '>')

class IsaJson:

    def __init__(self, jsonPath):
        jsonc = ''
        with open(jsonPath, 'r') as jsonf:
            jsonc = jsonf.read()
        jsondict = json.loads(jsonc)

        isa = jsondict['isa']
        opcodes = isa['opcodes']
        self.alias = isa['alias']

        self.instructions = []
        for opcode in opcodes:
            self.instructions.append(IsaInstruction(opcode))

    def get(self, name):
        for inst in self.instructions:
            if name == inst.mnemonic:
                return inst
        print('Can\'t find <', name, '> instruction!')

    def getAlias(self, name):
        for alias in self.alias:
            if alias['name'] == name:
                return alias
        print('Can\'t find <', name, '> Alias!')
        return None

    def containsAlias(self, token):
        for alias in self.alias:
            if alias['name'] in token:
                return alias
        return None

    def Print():
        for i in self.instructions:
            i.Print()
