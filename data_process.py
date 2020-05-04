import math
import os
import string
import json
from nltk import *
from trie import *
from collections import defaultdict
from io import StringIO
from nanomsg import Socket, PAIR, PUB

def connection():
    global s1
    s1 = Socket(PAIR)
    s1.connect('ipc://127.0.0.1:54272')

def get_contractions():
    global contractions
    with open("contractions.json") as f:
        contractions = json.load(f)
        for c,v in contractions.items():
            contractions[c] = v.split("/")
            
def replace_abreviations(sentence):
    for c,v in contractions.items():
        sentence = sentence.replace(c.lower(),v[0].lower(),100)
    return sentence
def get_document_tokenize(path):
    f = open(path)
    words = list()
    for line in f:
        pre_line = line.strip().split('" "')
        if pre_line == ['"character', 'dialogue"']: continue
        pre_line[2] = replace_abreviations(pre_line[2].lower())
        aux = word_tokenize(pre_line[2])
        aux = [word.lower() for word in aux]
        words += aux
    return words

def clean_document(document):
    new_document = list()
    for word in document: 
        bad = False  
        for punct in string.punctuation:
            if punct in word or word in string.punctuation: 
                bad = True
                break
        if not bad: 
            new_document.append(word)
    return new_document

def idf(word,stats):
    return math.log(stats.N() / stats[word])

def predict_from_dataset(dataset, terms):
    return [1 if term in dataset else 0 for term in terms]

def baseline_unigram_predict(terms):
    return predict_from_dataset(baseline_unigrams, terms)

def pos_unigram_predict(terms):
    return predict_from_dataset(pos_filtered_freqdist, terms)
if __name__ == "__main__":
    connection()
    #Nos situamos en el directorio del dataset
    s1.send("Training")
    get_contractions()
    os.chdir("info")
    # Cogemos los ficheros del dataset
    documents = os.listdir(".")
    # Get all the data from all the characters
    unigram_freq = FreqDist()
    bigram_freq = FreqDist()
    trigram_freq = FreqDist()
    vocabulary = list()
    for d in documents:
        pre_document = get_document_tokenize(d)
        document = clean_document(pre_document) 
        for word in document:
            unigram_freq[word] += 1  
            vocabulary.append(word)
        for bigram in ngrams(document,2):
            bigram_freq[bigram] += 1
        for trigram in ngrams(document,3):
            trigram_freq[trigram] += 1 

    trie = TrieSuggester()
    trie.index(vocabulary)
    s1.send("Training finished")
    query = s1.recv().decode("UTF-8")
    while True:
        if query != "":
            last_word = query.split()[-1]
            aux = trie.search(last_word)
            if aux:
                unigram = list()
                for i in aux:
                    unigram.append(i)
                #! Unigram
                max_results = 7
                tfs = FreqDist(unigram)
                unigram.sort(key=lambda w: -(tfs[w] * idf(w, unigram_freq)) ,reverse=True)
                unigram = unigram[:max_results]
                s1.send("unigram")
                for uni in unigram:
                    if uni != last_word:
                        s1.send(uni)

                #! Bigram
                bigram_finder = BigramCollocationFinder.from_words(vocabulary)
                bigram_measures = BigramAssocMeasures()
                results = 0
                for i,j in bigram_finder.nbest(bigram_measures.pmi, 1000000):   
                    if i in unigram:
                        s1.send(i + " " + j)
                        results += 1
                    if results is max_results: break
                
                #! Trigram 
                trigram_finder = TrigramCollocationFinder.from_words(vocabulary)
                trigram_measures = TrigramAssocMeasures()
                results = 0
                for i,j,t in trigram_finder.nbest(trigram_measures.pmi, 1000000):   
                    if i in unigram:
                        s1.send(i + " " + j + " " + t)
                        results += 1
                    if results is max_results: break
                s1.send("THE END")
        query = s1.recv().decode("UTF-8")
