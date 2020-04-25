
from jsonp import *
from asmp import *
from wmif import *
from pp import *

isaJson = IsaJson('fx.json')
pp = AsmAlias('ex.asm')
pp.RemoveComments()
asm = AsmParser(pp.lineBuffer)

asm.ParseAlias(isaJson)

asm.ParseTokens(isaJson)
asm.ParseSections(isaJson)
binArray = asm.Resolve(isaJson)

mifWriter = MifWriter(binArray, 16)

mifWriter.Write('out.mif')

mifWriter.Print()
