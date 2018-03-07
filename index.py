#!/usr/bin/python
# Matric. #: A0178639J
import getopt
import math
import os
import re
import sys
from nltk.stem.porter import *
from nltk.tokenize import word_tokenize

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


# main
files_list = os.listdir(input_directory)
files_list = [int(i) for i in files_list]
files_list.sort()
dictionary = {}
postings = []

stemmer = PorterStemmer()

print("Generating dictionary and postings lists...")

files_indexed = []
for i in range(0, len(files_list)):
    file_name = files_list[i]
    files_indexed.append(file_name)
    directory = "%s\\%s" % (input_directory, str(file_name))
    data = None
    with open(directory, 'r') as read_file:
        data = read_file.read()
    tokens = [stemmer.stem(tok.lower()) for tok in word_tokenize(data)]
    for t in tokens:
        if t in dictionary:
            if file_name not in dictionary[t]['l']:
                dictionary[t]['l'].append(file_name)
                dictionary[t]['c'] += 1
        else:
            index = len(dictionary)
            dictionary[t] = {'c': 1, 'i': index, 'l': [file_name]}
            # postings.append([file_name])

print("Files indexed. Generating skip pointers...")

for key, value in dictionary.items():
    len_postings = value['c']
    # don't add skip pointers if list is too short, since it won't help speed up by that much
    if len_postings < 5:
        continue
    num_skip_ps = int(round(math.sqrt(len_postings), 0))
    skip_length = math.ceil(len_postings/num_skip_ps) - 1
    for j in range(0, num_skip_ps):
        dictionary[key]['l'][j*skip_length] = "%s@%s" % (value['l'][j*skip_length],\
            str(value['l'][skip_length*(j+1)]))

print("Skip pointers generated. Writing to dictionary.txt and postings.txt...")

out_postings = open(output_file_postings, 'w')
for i in files_indexed:
    out_postings.write("%s " % str(i))
out_postings.write("\n");
out_dict = open(output_file_dictionary, 'w')
for key, value in dictionary.items():
    out_dict.write("%s %s\n" % (key, value['c']))
    postings_list = ''
    for item in value['l']:
        postings_list = "%s %s" % (postings_list, str(item))
    postings_list = postings_list.strip()
    out_postings.write("%s\n" % postings_list);

out_dict.close()
out_postings.close()

print("dictionary.txt and postings.txt written. Indexing done!")
