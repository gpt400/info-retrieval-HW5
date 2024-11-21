class fixedLengthFile:
    def __init__(self, filename, recordSize):
        self.filename = filename
        self.recordSize = recordSize
        self.numRecords = -1
        self.file = None

    def openForWrite(self):
        try:
            self.file = open(self.filename, 'w')
            self.numRecords = 0
            return True
        except IOError:
            return False

    def openForRead(self, numRecords):
        try:
            self.file = open(self.filename, 'r')
            self.numRecords = numRecords
            return True
        except IOError:
            return False

    def closeAfterWriting(self):
        if self.file:
            self.file.close()
        num = self.numRecords
        self.numRecords = -1
        return num

    def closeAfterReading(self):
        if self.file:
            self.file.close()
        self.numRecords = -1

    def writeRecord(self, *args):
        return

    def readRecord(self, recordNum):
        if self.file and 0 <= recordNum < self.numRecords:
            position = recordNum * self.recordSize
            self.file.seek(position)
            record = self.file.read(self.recordSize)
            return record, True
        return None, False


class mapFile(fixedLengthFile):
    RECORD_SIZE = 26

    def __init__(self, filename):
        super().__init__(filename, self.RECORD_SIZE)

    def writeRecord(self, docId, filename):
        if self.file:
            # truncate the fields and pad with spaces
            str_docId = str(docId)[:4].ljust(4)
            filename = filename[:20].rjust(20)
            record = f"{str_docId} {filename}" + "\n"
            if len(record) != self.RECORD_SIZE:
               print(f"map record not the correct length:{record}:")

            # write the map record
            self.file.write(record)
            self.numRecords += 1
            return True
        return False

    def readRecord(self, recordNum):
        if self.file and 0 <= recordNum < self.numRecords:
            position = recordNum * self.recordSize
            self.file.seek(position)
            record = self.file.read(self.recordSize)
            docId = record[:4].strip()
            filename = record[5:29].strip()
            return (docId, filename), True
        return None, False


class postFile(fixedLengthFile):
    RECORD_SIZE = 12

    def __init__(self, filename):
        super().__init__(filename, self.RECORD_SIZE)

    def writeRecord(self, docId, weight):
        if self.file:
            str_docId = str(docId)[:4].ljust(4)
            str_weight = str(weight)[:6].rjust(6)
            record = f"{str_docId} {str_weight}" + "\n"
            if len(record) != self.RECORD_SIZE:
               print(f"post record not the correct length:{record}:")

            # write the post record
            self.file.write(record)
            self.numRecords += 1
            return True
        return False

    def readRecord(self, recordNum):
        if self.file and 0 <= recordNum < self.numRecords:
            position = recordNum * self.RECORD_SIZE
            self.file.seek(position)
            record = self.file.read(self.RECORD_SIZE)
            docId = record[:4].strip()
            weight = record[5:].strip()
            return (docId, weight), True
        return None, False


class dictFile(fixedLengthFile):
    RECORD_SIZE = 34

    def __init__(self, filename):
        super().__init__(filename, self.RECORD_SIZE)

    def writeRecord(self, term, numDocs, start):
        if self.file:
            # truncate the strings to the correct lengths and pad with spaces
            term = term[:20].ljust(20)
            str_numdocs = str(numDocs)[:4].rjust(4)
            str_start = str(start)[:7].rjust(7)
            record = f"{term} {str_numdocs} {str_start}" + "\n"
            if len(record) != self.RECORD_SIZE:
               print(f"dict record not the correct length:{record}:")

            # write the dict record
            self.file.write(record)
            self.numRecords += 1
            return True
        return False

    def readRecord(self, recordNum):
        if self.file and 0 <= recordNum < self.numRecords:
            position = recordNum * self.recordSize
            self.file.seek(position)
            record = self.file.read(self.RECORD_SIZE)
            term = record[:20].strip()
            numDocs = record[21:25].strip()
            start = record[27:].strip()
            return (term, numDocs, start), True
        return None, False
