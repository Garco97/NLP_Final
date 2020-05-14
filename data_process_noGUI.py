import math
import os
import string
import json
from nltk import *
from trie import *
from collections import defaultdict

def get_contractions():
    global contractions
    with open("contractions.json") as f:
        contractions = json.load(f)
        for c,v in contractions.items():
            contractions[c] = v.split("/")
            
def replace_contractions(sentence):
    for c,v in contractions.items():
        sentence = sentence.replace(c.lower(),v[0].lower(),100)
    return sentence
def get_document_tokenized(path):
    f = open(path)
    words = list()
    for line in f:
        pre_line = line.replace(".", " ")
        pre_line = pre_line.strip().split('" "')
        if pre_line == ['"character', 'dialogue"']: continue
        pre_line[2] = replace_contractions(pre_line[2].lower())
        aux = word_tokenize(pre_line[2])
        aux = [word.lower() for word in aux]
        words += aux
    return words

def clean_document(document):
    new_document = list()
    for word in document: 
        bad = False  
        for punct in string.punctuation:
            if word in string.punctuation or punct in word: 
                bad = True
                break
        if not bad: 
            new_document.append(word)
    return new_document

if __name__ == "__main__":
    #Nos situamos en el directorio del dataset
    print("Training")
    get_contractions()
    os.chdir("info")
    # Cogemos los ficheros del dataset
    documents = os.listdir(".")
    # Get all the data from all the characters
    tf = defaultdict(lambda:FreqDist()) 
    df = defaultdict(lambda:0) 
    idf = defaultdict(lambda:0.0)
    tf_idf = defaultdict(lambda:defaultdict(lambda:0.0))

    vocabulary = set()
    words = list()
    #! Gather all the words in the documents
    for d in documents:
        pre_document = get_document_tokenized(d)
        document = clean_document(pre_document) 
        #! Get tf for every word in the documents
        for word in document:
            tf[d][word] += 1  
            vocabulary.add(word)
            words.append(word)
    #! Get df for every word
    for d in documents:
        for word in vocabulary:
            if tf[d][word]:df[word] += 1
    #! Calculate the idf
    for word in vocabulary:
        idf[word] = math.log10(len(documents)/df[word])
    #! Calculate the tf-idf
    for d in documents:
        for word in vocabulary:
            if tf[d][word]: tf_idf[d][word] = (1+math.log10(tf[d][word])) * idf[word]

    #! Get bigrams in order of PMI
    bigram_finder = BigramCollocationFinder.from_words(words)
    bigram_measures = BigramAssocMeasures()
    best_bigrams = bigram_finder.nbest(bigram_measures.pmi, 1000000)

    #! Get trigrams in order of PMI
    trigram_finder = TrigramCollocationFinder.from_words(words)
    trigram_measures = TrigramAssocMeasures()
    best_trigrams = trigram_finder.nbest(trigram_measures.pmi, 1000000)

    trie = TrieSuggester()
    trie.index(vocabulary)
    print("Training finished")
    max_results = int(input("Enter how many results do you want:"))
    query = input("Enter a word:")
    while query != "":
        query_words = query.split()
        last_word = query_words[-1]
        aux = trie.search(last_word)
        if aux:
            unigram = list()
            for i in aux:
                unigram.append(i)
            #! Unigram
            unigram_sorted = list()
            for word in unigram:
                word_value = 0
                for d in documents:
                    if word_value < tf_idf[d][word]: word_value = tf_idf[d][word]
                unigram_sorted.append((word,word_value))   
            unigram_sorted.sort(key=lambda tup: tup[1], reverse=True)                 
            unigram_sorted = unigram_sorted[:max_results]
            print("\nUnigrams:")
            unigram = list()
            for word,value in unigram_sorted:
                print(word)
                unigram.append(word)
            print("\nBigrams:")
            #! Bigram
            results = 0
            for i,j in best_bigrams:  
                if i in unigram:
                    print(i + " " + j)
                    results += 1
                if results is max_results: break
            print("\nTrigrams:")

            #! Trigram 
            results = 0
            for i,j,t in best_trigrams:   
                if i in unigram:
                    print(i + " " + j + " " + t)
                    results += 1
                if results is max_results: break
        query = input("\nEnter a word:")
