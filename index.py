#!/usr/bin/python
import getopt
import math
import os
import re
import sys
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.stem.porter import *

# command:
# python index.py -i "..\nltk_data\corpora\reuters\training\" -d dictionary.txt -p postings.txt

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


files_list = os.listdir(input_directory)
files_list = [int(i) for i in files_list]
files_list.sort()
dictionary = {}
postings = []

stemmer = PorterStemmer()

# for i in range(0, len(files_list)):
for i in range(0, 100):
    file_name = files_list[i]
    directory = "%s%s" % (input_directory, str(file_name))
    with open(directory, 'r') as read_file:
        data = read_file.read().replace('\n', '')
        tokens = [stemmer.stem(tok.lower()) for tok in word_tokenize(data)]
        for t in tokens:
            if t not in dictionary:
                index = len(dictionary)
                dictionary[t] = index
                postings.append([file_name])
            else:
                if file_name not in postings[dictionary[t]]:
                    postings[dictionary[t]].append(file_name)


with open(output_file_dictionary, 'w') as out_dict:
    for entry in dictionary:
        out_dict.write("%s %s\n" % (entry, dictionary[entry]))

with open(output_file_postings, 'w') as out_postings:
    for line in postings:
        # len_postings = len(line)
        # num_skip_ps = math.sqrt(len_postings).round()
        for item in line:
            out_postings.write("%s " % str(item))
        out_postings.write("\n");
