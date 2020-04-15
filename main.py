
from jsonp import *
from asmp import *
from wmif import *
from pp import *

isaJson = IsaJson('fx.json')
pp = AsmPreprocess('ex.asm')
pp.RemoveComments()
pp.ApplyAliases(isaJson)
asm = AsmParser(pp.postLineBuffer)

asm.Phase_1(isaJson)
binArray = asm.Phase_2(isaJson)

mifWriter = MifWriter(binArray, 2)

mifWriter.Print()