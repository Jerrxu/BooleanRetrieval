#!/usr/bin/python
import getopt
import linecache
import nltk
import re
import sys
from nltk.stem.porter import *

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q file-of-queries -o output-file-of-results")

dictionary_file = postings_file = file_of_queries = output_file_of_results = None
	
try:
    opts, args = getopt.getopt(sys.argv[1:], 'd:p:q:o:')
except(getopt.GetoptError, err):
    usage()
    sys.exit(2)

for o, a in opts:
    if o == '-d':
        dictionary_file  = a
    elif o == '-p':
        postings_file = a
    elif o == '-q':
        file_of_queries = a
    elif o == '-o':
        file_of_output = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or file_of_queries == None or file_of_output == None :
    usage()
    sys.exit(2)



stemmer = PorterStemmer()

def _and(token1, token2):
    stem1 = stemmer.stem(token1.lower())
    line1 = linecache.getline(postings_file, int(dictionary[stem1]) + 1)
    list1 = line1.strip().split(' ')
    stem2 = stemmer.stem(token2.lower())
    line2 = linecache.getline(postings_file, int(dictionary[stem2]) + 1)
    list2 = line2.strip().split(' ')
    merged = []
    count1 = 0
    count2 = 0
    while count1 != len(list1) and count2 != len(list2):
        int1 = int(list1[count1])
        int2 = int(list2[count2])
        if int1 == int2:
            merged.append(int1)
            print(int1)
            count1 += 1
            count2 += 1
        elif int1 < int2:
            count1 += 1
        else:
            count2 += 1
    return '\n\n'


def _or(token1, token2):
    stem1 = stemmer.stem(token1.lower())
    line1 = linecache.getline(postings_file, int(dictionary[stem1]) + 1)
    list1 = line1.strip().split(' ')
    stem2 = stemmer.stem(token2.lower())
    line2 = linecache.getline(postings_file, int(dictionary[stem2]) + 1)
    list2 = line2.strip().split(' ')
    merged = list1 + [i for i in list2 if i not in list1]
    merged = [int(i) for i in merged]
    merged.sort()
    return merged


dictionary = {}
with open(dictionary_file, 'r') as dict_file:
    for line in dict_file:
        line = line.replace('\n', '').split(' ')
        dictionary[line[0]] = line[1]


with open(file_of_queries, 'r') as queries_file:
    for line in queries_file:
        line = line.strip().split(' ')
        if line[1] == 'AND':
            print(_and(line[0], line[2]))
        elif line[1] == 'OR':
            print(_or(line[0], line[2]))
