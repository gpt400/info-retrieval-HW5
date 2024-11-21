from invertedFile import invertedFile

# print map
def printMapRecord(recordNum, invFile):
    record, success = invFile.readMapRecord(recordNum)
    if success:
        print(f"Map record {recordNum}: {record}")
    else:
        print(f"Map record {recordNum} does not exist.")

# print dict
def printDictRecord(recordNum, invFile):
    record, success = invFile.readDictRecord(recordNum)
    if success:
        print(f"Dict record {recordNum}: {record}")
    else:
        print(f"Dict record {recordNum} does not exist.")

# print post
def printPostRecord(recordNum, invFile):
    record, success = invFile.readPostRecord(recordNum)
    if success:
        print(f"Post record {recordNum}: {record}")
    else:
        print(f"Post record {recordNum} does not exist.")

def main():
    print("CREATING INVERTED FILE...")
    invFile = invertedFile("outfiles/dict", "outfiles/post", "outfiles/map", "outfiles/config.txt")

    print("\n\nTESTING READ OF MAP RECORDS")
    invFile.openForRead()

    printMapRecord(0, invFile)  # first record
    printMapRecord(2, invFile)  # some valid record
    printMapRecord(3, invFile)  # last record
    printMapRecord(-1, invFile) # too small
    printMapRecord(4, invFile)  # too big

    print("\n\nTESTING READ OF DICT RECORDS")
    printDictRecord(0, invFile)  # first record
    printDictRecord(2, invFile)  # some valid record
    printDictRecord(20, invFile) # last record
    printDictRecord(-1, invFile) # too small
    printDictRecord(21, invFile) # too big

    print("\n\nTESTING READ OF POST RECORDS")
    printPostRecord(0, invFile)  # first record
    printPostRecord(2, invFile)  # some valid record
    printPostRecord(10, invFile) # last record
    printPostRecord(-1, invFile) # too small
    printPostRecord(11, invFile) # too big

    invFile.closeAfterReading()

    print("\n\nTESTING READING FROM A CLOSED INVERTED FILE")
    printMapRecord(2, invFile)  # should fail
    printDictRecord(2, invFile)  # should fail
    printPostRecord(2, invFile)  # should fail

if __name__ == "__main__":
    main()
