import math
import resource
import sys
import spacy
import os
import time
from invertedFile import invertedFile
from fixedLengthFile import fixedLengthFile, mapFile, dictFile, postFile
from hashtable import HashTable, Posting
from tokenizer import processFile, removeFileExtension

MAX_LENGTH = 45

#Main, processes files from inputDirectory to outputDirectory
def main(inputDirectory, outputDirectory):

   #statistics about the collection
    numPostings = 0
    numTokens = 0
    numDocuments = 0
    dfTracker = {}
    docTokenCounters = {}

    #nlp = spacy.load("en_core_web_sm")
    nlp = spacy.blank("en")
    nlp.max_length = 2000000 #increase memory allocation, necessary for VS Code and maybe Turing

    #if outputDirectory of given name doesn't exist, make it
    if not os.path.exists(outputDirectory):
        os.makedirs(outputDirectory)

    globalHT = HashTable(300000)
    docID = 0

    # open the inverted File
    MapFilename = outputDirectory + "/map"
    DictFilename = outputDirectory + "/dict"
    PostFilename = outputDirectory + "/post"
    ConfigFilename = outputDirectory + "/config.txt"
    invFile = invertedFile(DictFilename, PostFilename, MapFilename, ConfigFilename)
    invFile.openForWrite()
    
    #Process files in inputDirectory
    for filename in os.listdir(inputDirectory):
        fullPath = os.path.join(inputDirectory, filename)
        invFile.writeMapRecord(docID, filename)

        if os.path.isfile(fullPath):
            tokens = processFile(fullPath, nlp)
            numTokensInDocument = len(tokens)
            docTokenCounters[docID] = numTokensInDocument
            numTermsInDocument = 0
  
            #initialize document hash table
            docht = HashTable(numTokensInDocument)

            for token in tokens:
                    if len(token) < MAX_LENGTH:
                        data = docht.getPostings(token)
                        if not data:
                            numTermsInDocument += 1
                            # Insert and update numDocs
                            docht.insert(token, Posting(docID=docID, freq=1))
                            dfTracker[token] = dfTracker.get(token, 0) + 1
                        else:
                            index = docht.__find__(token)
                            for i, posting in enumerate(docht.hashtable[index].postings):
                                if posting.docID == docID:
                                    updatedFreq = posting.freq + 1
                                    docht.hashtable[index].postings[i] = Posting(docID=posting.docID, freq=updatedFreq)
                                    break

            for idx in docht:
                term = docht.hashtable[idx].key
                if term != '':
                    postings = docht.hashtable[idx].postings
                    if postings:
                        freq = postings[0].freq
                        # Create a posting for globalHT
                        posting = Posting(docID=docID, freq=freq)
                        globalHT.insert(term, posting)

            print(f"Filename: {filename}")
            print(f"Unique terms in document: {numTermsInDocument}")
            print(f"Total tokens in document: {numTokensInDocument}")
            numPostings += numTermsInDocument
            numTokens += numTokensInDocument
            numDocuments += 1
            docID += 1

    # After processing all documents
    writeIndexFiles(globalHT, dfTracker, numDocuments, docTokenCounters, invFile)
    invFile.closeAfterWriting()

    print(f"Total unique terms in the collection: {globalHT.used}")
    print(f"Total number of postings in the document collection: {numPostings}")
    print(f"Total number of tokens in the document collection: {numTokens}")

def writeIndexFiles(globalHT, dfTracker, numDocuments, docTokenCounters, invFile):

    start = 0  # Start position in postings file

    for idx in range(globalHT.size):
        pair = globalHT.hashtable[idx]
        if pair.key != '':
            term = pair.key
            postings = pair.postings
            numDocsContainingTerm = dfTracker.get(term, 1)

            idf = math.log10(numDocuments / numDocsContainingTerm) + 1

            invFile.writeDictRecord(term, len(postings), start)

            for posting in postings:
                tf = posting.freq
                numTokensInDocument = docTokenCounters[posting.docID]
                rtf = tf / numTokensInDocument
                tf_idf = rtf * idf
                invFile.writePostRecord(posting.docID, tf_idf)

            start += len(postings)
        else:
            # Empty slot
            invFile.writeDictRecord('empty', -1, -1)


if __name__ == '__main__':
    if len(sys.argv) != 3: #only 2 arguments allowed
        print("Program needs input directory and output directory")
        sys.exit(1)

    startRealTime = time.time()  # Real time
    startUserTime = resource.getrusage(resource.RUSAGE_SELF).ru_utime  # User time

    # Call main with given arguments
    main(sys.argv[1], sys.argv[2])

    # End time measurement
    endRealTime = time.time()
    endUserTime = resource.getrusage(resource.RUSAGE_SELF).ru_utime

    elapsedRealTime = endRealTime - startRealTime
    elapsedUserTime = endUserTime - startUserTime

    print(f"Real time: {elapsedRealTime:.2f} seconds")
    print(f"User time (CPU): {elapsedUserTime:.2f} seconds")
