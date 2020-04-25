
from jsonp import *
from asmp import *
from wmif import *
from pp import *
from sim import *

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

sim = SimCpu('sim.json')
sim.Config(isaJson, 16, 100000)
sim.Startup(binArray)

sim.Execute(isaJson)
sim.DumpRegs()
sim.DumpMem(0x1000, 0x1010)