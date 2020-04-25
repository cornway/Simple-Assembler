import os

class MifWriter:

    def __init__(self, byteArray=[], bitsWidth=16):
        width = bitsWidth >> 3
        wdeepth = len(byteArray) / width
        addr = 0
        self.rawText = ''
        self.rawText += 'WIDTH = ' + str(bitsWidth) + ';\n'
        self.rawText += 'DEPTH = ' + str(int(wdeepth)) + ';\n\n'
        self.rawText += 'ADDRESS_RADIX = HEX;\n'
        self.rawText += 'DATA_RADIX = HEX;\n\n'
        self.rawText += 'CONTENT BEGIN\n'

        while wdeepth >= 1:

            word = (byteArray[addr + 1] << 8) | byteArray[addr]
            if (width == 2):
                self.rawText += '\t' + hex(addr >> 1)[2:] + '\t:\t' + hex(word)[2:] + ';\n'
            addr = addr + width
            wdeepth = wdeepth - 1

        self.rawText += 'END;'

    def Write(self, path):
        if os.path.isfile(path):
            os.remove(path)
        f = open(path, 'a')
        f.write(self.rawText)
        f.close()

    def Print(self):
        print(self.rawText)
