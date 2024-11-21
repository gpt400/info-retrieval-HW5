from fixedLengthFile import dictFile, postFile, mapFile

class invertedFile:
    def __init__(self, dictFilename, postFilename, mapFilename, configFilename):
        self.dictFile = dictFile(dictFilename)
        self.postFile = postFile(postFilename)
        self.mapFile = mapFile(mapFilename)
        self.configFile = configFilename

    def openForWrite(self):
        return (self.dictFile.openForWrite() and
                self.postFile.openForWrite() and
                self.mapFile.openForWrite()) 

    def openForRead(self):
        try:
            with open(self.configFile, 'r') as config:
                dictRecords, postRecords, mapRecords = map(int, config.read().split())
            return (self.dictFile.openForRead(dictRecords) and
                    self.postFile.openForRead(postRecords) and
                    self.mapFile.openForRead(mapRecords))
        except IOError:
            return False

    def closeAfterWriting(self):
        dictNum = self.dictFile.closeAfterWriting()
        postNum = self.postFile.closeAfterWriting()
        mapNum = self.mapFile.closeAfterWriting()
        with open(self.configFile, 'w') as config:
            config.write(f"{dictNum} {postNum} {mapNum}\n")
        return True

    def closeAfterReading(self):
        self.dictFile.closeAfterReading()
        self.postFile.closeAfterReading()
        self.mapFile.closeAfterReading()

    def writeMapRecord(self, docId, filename):
        return self.mapFile.writeRecord(docId, filename)

    def writeDictRecord(self, term, numDocs, start):
        return self.dictFile.writeRecord(term, numDocs, start)

    def writePostRecord(self, docId, weight):
        return self.postFile.writeRecord(docId, weight)

    def readMapRecord(self, recordNum):
        return self.mapFile.readRecord(recordNum)

    def readDictRecord(self, recordNum):
        return self.dictFile.readRecord(recordNum)

    def readPostRecord(self, recordNum):
        return self.postFile.readRecord(recordNum)
