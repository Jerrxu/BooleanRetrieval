#!/usr/bin/python
import getopt
import math
import os
import re
import sys
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize

# command:
# python index.py -i ".\training" -d dictionary.txt -p postings.txt

def usage():
    print("usage: " + sys.argv[0] + " -i directory-of-documents -d dictionary-file -p postings-file")

input_directory = output_file_dictionary = output_file_postings = None

try:
    opts, args = getopt.getopt(sys.argv[1:], 'i:d:p:')
except(getopt.GetoptError, err):
    usage()
    sys.exit(2)
    
for o, a in opts:
    if o == '-i': # input directory
        input_directory = a
    elif o == '-d': # dictionary file
        output_file_dictionary = a
    elif o == '-p': # postings file
        output_file_postings = a
    else:
        assert False, "unhandled option"
        
if input_directory == None or output_file_postings == None or output_file_dictionary == None:
    usage()
    sys.exit(2)



# control parameters
num_files_to_index = 100


files_list = os.listdir(input_directory)
files_list = [int(i) for i in files_list]
files_list.sort()
dictionary = {}
postings = []

stemmer = PorterStemmer()

files_indexed = []
for i in range(0, num_files_to_index):
    file_name = files_list[i]
    files_indexed.append(file_name)
    directory = "%s\\%s" % (input_directory, str(file_name))
    with open(directory, 'r') as read_file:
        data = read_file.read()
        tokens = [stemmer.stem(tok.lower()) for tok in word_tokenize(data)]
        for t in tokens:
            if t in dictionary:
                if file_name not in postings[dictionary[t]]:
                    postings[dictionary[t]].append(file_name)
            else:
                index = len(dictionary)
                dictionary[t] = index
                postings.append([file_name])

print("%s files indexed. Writing to dictionary.txt..." % num_files_to_index)

with open(output_file_dictionary, 'w') as out_dict:
    for entry in dictionary:
        out_dict.write("%s %s\n" % (entry, dictionary[entry]))

print("dictionary.txt written successfully. Writing to postings.txt...")

with open(output_file_postings, 'w') as out_postings:
    for i in files_indexed:
        out_postings.write("%s " % str(i))
    out_postings.write("\n");
    for line in postings:
        # len_postings = len(line)
        # num_skip_ps = math.sqrt(len_postings).round()
        for item in line:
            out_postings.write("%s " % str(item))
        out_postings.write("\n");

print("postings.txt written successfully. Done.")
