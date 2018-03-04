#!/usr/bin/python
import getopt
import linecache
import nltk
import re
import sys
from nltk.stem.porter import *

def usage():
    print("usage: " + sys.argv[0] + " -d dictionary-file -p postings-file -q queries-file -o output-file")

dictionary_file = postings_file = queries_file = output_file = None
	
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
        queries_file = a
    elif o == '-o':
        output_file = a
    else:
        assert False, "unhandled option"

if dictionary_file == None or postings_file == None or queries_file == None or output_file == None:
    usage()
    sys.exit(2)

print("hello pizza")
print(output_file)

stemmer = PorterStemmer()

def _and(token1, token2):
    stem1 = stemmer.stem(token1.lower())
    line1 = linecache.getline(postings_file, int(dictionary[stem1]) + 2)
    list1 = line1.strip().split(' ')
    stem2 = stemmer.stem(token2.lower())
    line2 = linecache.getline(postings_file, int(dictionary[stem2]) + 2)
    list2 = line2.strip().split(' ')
    merged = []
    count1 = 0
    count2 = 0
    while count1 != len(list1) and count2 != len(list2):
        int1 = int(list1[count1])
        int2 = int(list2[count2])
        if int1 == int2:
            merged.append(int1)
            count1 += 1
            count2 += 1
        elif int1 < int2:
            count1 += 1
        else:
            count2 += 1
    return merged

def _or(token1, token2):
    stem1 = stemmer.stem(token1.lower())
    line1 = linecache.getline(postings_file, int(dictionary[stem1]) + 2)
    list1 = line1.strip().split(' ')
    stem2 = stemmer.stem(token2.lower())
    line2 = linecache.getline(postings_file, int(dictionary[stem2]) + 2)
    list2 = line2.strip().split(' ')
    merged = [int(i) for i in list1] + [int(i) for i in list2 if i not in list1]
    merged.sort()
    return merged


def _not(token):
    stem = stemmer.stem(token.lower())
    line = linecache.getline(postings_file, int(dictionary[stem]) + 2)
    listt = line.strip().split(' ')
    merged = [int(i) for i in all_postings if i not in listt]
    return merged

dictionary = {}
with open(dictionary_file, 'r') as dict_file:
    for line in dict_file:
        line = line.replace('\n', '').split(' ')
        dictionary[line[0]] = line[1]

all_postings = linecache.getline(postings_file, 1)
all_postings = [i for i in all_postings.strip().split(' ')]


# writing to output file

queries_file = open(queries_file, 'r')
output_writer = open(output_file, 'w')
for line in queries_file:
    line = line.strip().split(' ')
    result = None
    if line[1] == 'AND':
        result = _and(line[0], line[2])
    elif line[1] == 'OR':
        result = _or(line[0], line[2])
    elif line[0] == 'NOT':
        result = _not(line[1])

    output = ''
    for i in result:
        output = "%s%s " % (output, str(i))
    output_writer.write('%s\n' % output)

queries_file.close()
output_writer.close()
