import re
import html
import os.path

#Strip HTML tags and special characters
def strip(text):

    #Unescape HTML
    cleanText = html.unescape(text)

    #Pattern to match 'alt' and 'content'  HTML attributes
    tagPattern = r'\b(?:alt|content)=["\']([^"\']+)(?=["\'])'
    tagMatches = re.findall(tagPattern, cleanText)

    #Removes HTML tags and extra whitespace, and converts to lowercase
    cleanText = re.sub(r'<.*?>', '', cleanText)
    cleanText = re.sub(r'\s+', ' ', cleanText).strip().lower()

    cleanText += ' ' + ' '.join(tagMatches)

    return cleanText

#Removes file extensions
def removeFileExtension(inputpathname):

    root, ext = os.path.splitext(inputpathname)
    return root

#Converts document into tokens separated by newline
def getTokens(doc):

    final = ""
    for token in doc:
        final += str(token) + "\n"  
    return final.strip()

#Reads content, strips it, and tokenizes it
def processFile(filename, nlp):

    with open(filename, 'r') as f:
        s = f.read()
        s = strip(s)
    return tokenize(s, nlp)

#Tokenizes using regex patterns
def tokenize(text, nlp):

    #removing unwanted elements
    urlPattern = re.compile(r'http[s]?://\S+')
    emailPattern = re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b')
    floatingPointPattern = re.compile(r'\b\d+\.\d+\b')
    punctuationPattern = re.compile(r'[^\w\s]')

    #detect urls and emails
    urls = urlPattern.findall(text)
    emails = emailPattern.findall(text)

    # remove unwanted elements
    text = urlPattern.sub('', text)
    text = emailPattern.sub('', text)
    text = floatingPointPattern.sub('', text)
    text = punctuationPattern.sub('', text)

    #tokenize the cleaned text
    doc = nlp(text)
    tokens = []

    for token in doc:
        if token.is_ascii and token.is_alpha and not token.is_stop and len(token)>1:
            tokens.append(token.text.lower())

    tokens.extend(urls)
    tokens.extend(emails)

    return tokens
