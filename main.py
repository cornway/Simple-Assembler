
from jsonp import *
from asmp import *
from wmif import *
from pp import *

isaJson = IsaJson('fx.json')
pp = AsmAlias('ex.asm')
pp.RemoveComments()
asm = AsmParser(pp.lineBuffer)

asm.Phase_0(isaJson)

asm.PrintTokens()

asm.Phase_1(isaJson)

binArray = asm.Phase_2(isaJson)

mifWriter = MifWriter(binArray, 2)

mifWriter.Print()