import sys



class TextfileWrapper(object):

    def __init__(self, inputFilename, outputFilename):
        self.inputFilename = inputFilename
        self.outputFilename = outputFilename
        self.outputLines = []
    
    def determineIndentation(self, input):
        self.indent = 0
        self.enumerationMode = False
        for c in input:
            if c == ' ':
                self.indent += 1
            elif c in ['-', '*']:
                self.enumerationMode = True
                return
            else:
                return

    def readFile(self):
        file = open(self.inputFilename, "r")
        inputLines = file.readlines()
        file.close()
        return(inputLines)
            
    def writeFile(self):
        file = open(self.outputFilename, "w")
        file.writelines(self.outputLines)
        file.close()
    
    def addLine(self, line):
        self.outputLines.append((' ' * self.indent) + line.strip() + '\n')
        if(self.enumerationMode):
            self.indent += 2
        self.enumerationMode = False
    
    def run(self):
        inputLines = self.readFile()
        
        lineCounter = 1
        for line in inputLines:
            currentLine = line
            self.determineIndentation(currentLine)
            while(len(currentLine.strip())+self.indent >= 80):
                strippedLine = currentLine.strip()
                wrappingColumn = strippedLine[:80-self.indent+1].rfind(' ')
                if(wrappingColumn == -1):
                    print "Error: Couldn't wrap line %i." % (lineCounter)
                    sys.exit(2)
                self.addLine(strippedLine[:wrappingColumn])
                currentLine = strippedLine[wrappingColumn+1:]
            self.addLine(currentLine)
            lineCounter += 1
    
        self.writeFile()
        print "Successfully wrapped %i lines of input to %i lines of output." % (lineCounter, len(self.outputLines))





if(__name__ == "__main__"):
    if(len(sys.argv) != 3):
        print "Syntax: TextfileWrapper.py <input_file/> <output_file/>"
        sys.exit(1)
    else:
        TextfileWrapper(sys.argv[1], sys.argv[2]).run()
