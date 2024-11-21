from typing import NamedTuple, List
import atexit

class Posting(NamedTuple):
    docID: int
    freq: int

class StringIntPair(NamedTuple):
    key: str
    postings: List[Posting]

class HashTable:
    def __init__(self, NumKeys):
        self.size = NumKeys * 3 # we want the hash table to be 2/3 empty
        self.used = 0
        self.collisions = 0
        self.lookups = 0

        # Initialize the hashtable with unique StringIntPair instances
        self.hashtable = [StringIntPair('', []) for _ in range(self.size)]


        # register cleanup when exit
        atexit.register(self.cleanup)

    def __iter__(self):
        return iter(range(self.size))

    # Similar to destructor in cpp to clean up resources
    def cleanup(self):
        self.hashtable.clear()

    # ------------------------------ Accessors ------------------------------
    
    # print the contents of the hash table currently, only prints non-null entries
    def print(self, filename):
        with open(filename, 'w') as fpout:
            for i in range(self.size):
                if self.hashtable[i].key != "":
                    postingsStr = ', '.join([f'({p.doc_id}, {p.freq})' for p in self.hashtable[i].postings])
                    fpout.write(self.hashtable[i].key + " " + [{postingsStr}] + "\n")
                else:
                    fpout.write("empty\n")
        print("Collisions: ", self.collisions, ", Used: ", self.used, ", Lookups: ", self.lookups)


    # insert or add a word with its frequency count in hashtable
    def insert(self, key, posting: Posting):
        index = -1
        if self.used >= self.size:
            print("The hashtable is full; cannot insert.")
        else:
            index = self.__find__(key)

            # If not already in the table, insert it
            if self.hashtable[index].key == "":
                self.hashtable[index] = StringIntPair(key, [posting])
                self.used += 1
            else:
                # Update the frequency
                self.hashtable[index].postings.append(posting)

    def getPostings(self, key):
        self.lookups += 1
        index = self.__find__(key)
        if self.hashtable[index].key == "":
            return []
        else:
            return self.hashtable[index].postings
        
    # return the data or -1 if Key is not found
    def getData(self, key):
        self.lookups += 1
        index = self.__find__(key)
        if self.hashtable[index].key == "":
            return -1
        else:
            return self.hashtable[index].data

    # return the number of collisions
    def getUsage(self):
        return (self.used, self.collisions, self.lookups)
    
    # -------------------------- Private Functions ----------------------------

    # return the index of the word in the table, or the index of the free space in which to store the word
    def __find__(self, key):
        sum = 0
        index = -1

        # add all the characters of the key together
        for i in range(len(key)):
            sum = (sum * 19) + ord(key[i])   # Mult sum by 19, add byte value of char
   
        index = sum % self.size
        
        # Check to see if word is in that location
        # If not there, do linear probing until word found
        # or empty location found.
        while self.hashtable[index].key != key and self.hashtable[index].key != "":
            index = (index + 1) % self.size
            self.collisions += 1
       
        return index