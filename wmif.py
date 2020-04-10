
class MifWriter:

    def __init__(self, byteArray=[], width=1):
        wdeepth = len(byteArray) / width
        addr = 0
        self.rawText = ''
        self.rawText += 'DEPTH = ' + hex(int(wdeepth)) + ';\n'
        self.rawText += 'WIDTH = ' + hex(width) + ';\n'
        self.rawText += 'ADDRESS_RADIX = HEX;\n'
        self.rawText += 'DATA_RADIX = HEX;\n'
        self.rawText += 'CONTENT\n'
        self.rawText += 'BERGIN\n'

        while wdeepth >= 1:

            word = (byteArray[addr + 1] << 8) | byteArray[addr]
            if (width == 2):
                self.rawText += "{0:#0{1}x}".format(addr,6) + '    :    ' + "{0:#0{1}x}".format(word, 6) + ';\n'
            addr = addr + width
            wdeepth = wdeepth - 1

        self.rawText += 'END;'

    def Print(self):
        print(self.rawText)
