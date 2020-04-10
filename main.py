
from jsonp import *
from asmp import *
from wmif import *

isaJson = IsaJson('fx.json')
asm = AsmParser('ex.asm')

asm.Phase_1(isaJson)
binArray = asm.Phase_2(isaJson)

mifWriter = MifWriter(binArray, 2)

mifWriter.Print()