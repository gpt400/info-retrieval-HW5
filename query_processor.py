import spacy
import argparse
import os
from typing import Dict, List, Tuple
from fixedLengthFile import dictFile, postFile, mapFile
from tokenizer import tokenize, processFile

class QueryProcessor:
    def __init__(self, dict_path: str, post_path: str, map_path: str):
        self.dict_file = dictFile(dict_path)
        self.post_file = postFile(post_path)
        self.map_file = mapFile(map_path)
        self.nlp = spacy.blank("en")
        
        # Get number of lines in files
        self.dict_records = sum(1 for line in open(dict_path))
        self.post_records = sum(1 for line in open(post_path))
        self.map_records = sum(1 for line in open(map_path))

    def find_term(self, term: str) -> Tuple[int, int]:
        """Find a term in the dictionary file"""
        self.dict_file.openForRead(self.dict_records)
        
        # Read through all records sequentially
        for i in range(self.dict_records):
            record, success = self.dict_file.readRecord(i)
            if success and record[0].strip() == term:
                num_docs = int(record[1])
                start_pos = int(record[2])
                self.dict_file.closeAfterReading()
                return num_docs, start_pos
                
        self.dict_file.closeAfterReading()
        return -1, -1

    # def get_postings(self, start_pos: int, num_docs: int) -> List[Tuple[str, float]]:
    #     """Get postings for a term"""
    #     postings = []
    #     self.post_file.openForRead(self.post_records)
        
    #     for i in range(num_docs):
    #         record, success = self.post_file.readRecord(start_pos + i)
    #         if success:
    #             doc_id = record[0].strip()
    #             weight = float(record[1].strip())
    #             postings.append((doc_id, weight))
                
    #     self.post_file.closeAfterReading()
    #     return postings

    def get_postings(self, start_pos: int, num_docs: int) -> List[Tuple[str, float]]:
        """Get postings for a term"""
        postings = []
        self.post_file.openForRead(self.post_records)
    
        for i in range(num_docs):
            record, success = self.post_file.readRecord(start_pos + i)
            if success:
                try:
                    doc_id = record[0].strip()
                    weight = float(record[1].strip())
                    if doc_id and 0 <= float(doc_id) < self.map_records:  # Validate doc_id
                        postings.append((doc_id, weight))
                    else:
                        print(f"Warning: Invalid document ID {doc_id} in posting")
                except (ValueError, IndexError) as e:
                    print(f"Warning: Could not parse posting record: {e}")
                    continue
                
        self.post_file.closeAfterReading()
        return postings

    def process_query(self, query: str) -> List[Tuple[str, float]]:
        """Process a query and return top 10 results"""
        # Preprocess query using the same tokenization as indexing
        query_tokens = tokenize(query, self.nlp)
        
        if not query_tokens:
            return []

        # Process each term and accumulate scores
        accumulator = {}
        term_matches = {}
        
        print("\nProcessing query terms:", ", ".join(query_tokens))
        
        for term in query_tokens:
            print(f"\nLooking for term: {term}")
            num_docs, start_pos = self.find_term(term)
            
            if num_docs > 0:
                print(f"Found '{term}' with {num_docs} documents starting at position {start_pos}")
                postings = self.get_postings(start_pos, num_docs)
                for doc_id, weight in postings:
                    accumulator[doc_id] = accumulator.get(doc_id, 0) + weight
                    if doc_id not in term_matches:
                        term_matches[doc_id] = []
                    term_matches[doc_id].append(term)
            else:
                print(f"Term '{term}' not found in dictionary")

        # Get document names and prepare results
        results = []
        
        if accumulator:
            self.map_file.openForRead(self.map_records)
            for doc_id, score in accumulator.items():
                map_record, success = self.map_file.readRecord(int(doc_id))
                if success:
                    doc_name = map_record[1].strip()
                    matching_terms = term_matches.get(doc_id, [])
                    results.append((doc_name, score, matching_terms))
            self.map_file.closeAfterReading()

        # Sort by score
        results.sort(key=lambda x: x[1], reverse=True)
        
        # Display results
        if results:
            print(f"\nFound {len(results)} matching documents:")
            print("-" * 60)
            for i, (doc_name, score, terms) in enumerate(results[:10], 1):
                print(f"{i}. Document: {doc_name:<20} Score: {score:.4f}")
                print(f"   Matching terms: {', '.join(terms)}")
            print("-" * 60)
        else:
            print("\nNo matching documents found.")

        return results[:10]

def main():
    parser = argparse.ArgumentParser(description='Search engine query processor')
    parser.add_argument('query', nargs='+', help='Search terms')
    parser.add_argument('-d', '--directory', default='.', help='Directory containing index files')
    args = parser.parse_args()
    
    dict_path = os.path.join(args.directory, "dict")
    post_path = os.path.join(args.directory, "post")
    map_path = os.path.join(args.directory, "map")
    
    processor = QueryProcessor(dict_path, post_path, map_path)
    query = ' '.join(args.query)
    processor.process_query(query)

if __name__ == "__main__":
    main()