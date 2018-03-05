#!/usr/bin/python
import getopt
import linecache
import nltk
import re
import sys
from nltk.stem.porter import *

# command:
# python search.py -d dictionary.txt -p postings.txt -q queries.txt -o output.txt

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






"""
Shunting-yard algorithm for parsing queries
Source and credit due: https://github.com/ekg/shuntingyard
thanks ekg
"""

operator_and = "AND"
operator_or = "OR"
operator_not = "NOT"
operator_left_paran = "("
operator_right_paran = ")"

operator_association = {
    operator_and: "left",
    operator_or: "left",
    operator_not: "right"
}

operator_precedence = {
    operator_not: 2,
    operator_and: 1,
    operator_or: 0,
    operator_left_paran: -1,
    operator_right_paran: -1
}

def precedence(op):
    return operator_precedence[op]

def associativity(op):
    return operator_association[op]

def is_op(c):
    return c in operator_precedence and not (is_left_paran(c) or is_right_paran(c))

def is_left_paran(c):
    return c == operator_left_paran

def is_right_paran(c):
    return c == operator_right_paran

def append_token(token, l):
    if token != "":
        l.append(token)
    return ""

def tokenize(expr):
    tokens = []
    last_token = ""
    in_token = False
    for c in expr:
        if c == " ":
            in_token = False
            last_token = append_token(last_token, tokens)
            continue
        elif is_op(c) or is_right_paran(c) or is_left_paran(c):
            in_token = False
            last_token = append_token(last_token, tokens)
            tokens.append(c)
        else:
            in_token = True
            last_token += c
        if not in_token and last_token != "":
            last_token = append_token(last_token, tokens)
    if in_token:
        append_token(last_token, tokens)
    return tokens

# notes are taken from http://en.wikipedia.org/wiki/Shunting_yard_algorithm
def infix_to_prefix(expr):
    """converts the infix expression to prefix using the shunting yard algorithm"""
    ops = []
    results = []
    for token in tokenize(expr):
        #print ops, results
        if is_op(token):
            #If the token is an operator, o1, then:
            #while there is an operator token, o2, at the top of the stack, and
            #either o1 is left-associative and its precedence is less than or equal to that of o2,
            #or o1 is right-associative and its precedence is less than that of o2,
            #pop o2 off the stack, onto the output queue;
            #push o1 onto the stack.
            while len(ops) > 0 and is_op(ops[-1]) and \
                    ( (associativity(token) == 'left' and precedence(token) <= precedence(ops[-1])) \
                 or   (associativity(token) == 'right' and precedence(token) < precedence(ops[-1])) ):
                results.append(ops.pop())
            ops.append(token)
        #If the token is a left parenthesis, then push it onto the stack.
        elif is_left_paran(token):
            ops.append(token)
        #If the token is a right parenthesis:
        elif is_right_paran(token):
            #Until the token at the top of the stack is a left parenthesis, pop operators off the stack onto the output queue.
            while len(ops) > 0 and not is_left_paran(ops[-1]):
                results.append(ops.pop())
            #Pop the left parenthesis from the stack, but not onto the output queue.
            #If the stack runs out without finding a left parenthesis, then there are mismatched parentheses.
            if len(ops) == 0:
                print("error: mismatched parentheses")
                exit()
            if is_left_paran(ops[-1]):
                ops.pop()
        else:
        #If the token is a number, then add it to the output queue.
            results.append(token)
    #When there are no more tokens to read:
    #While there are still operator tokens in the stack:
    while len(ops) > 0:
        #If the operator token on the top of the stack is a parenthesis, then there are mismatched parentheses.
        if is_right_paran(ops[-1]) or is_left_paran(ops[-1]):
            print("error: mismatched parentheses")
            exit()
        #Pop the operator onto the output queue.
        results.append(ops.pop())
    return results

if __name__ == '__main__':
    if len(sys.argv) == 1:
        print("usage", sys.argv[0], "\"infix boolean expression\"")
        print("e.g. \"( true & false | ( true & ! true ) )\"")
        exit()
    print(' '.join(infix_to_prefix(sys.argv[1])))

"""
Shunting-yard algorithm end
"""






"""
Main script start
All code and all comments below are written by me, Huang Shan Xu
"""

stemmer = PorterStemmer()

dictionary = {}
with open(dictionary_file, 'r') as dict_file:
    for line in dict_file:
        line = line.replace('\n', '').split(' ')
        dictionary[line[0]] = line[1]

all_postings = linecache.getline(postings_file, 1)
all_postings = [int(i) for i in all_postings.strip().split(' ')]

def get_postings_list(token):
    """
    Argument:
        token: a lowercased, stemmed word
    Returns:
        list of int corresponding to the postings list of token
    """
    stem = stemmer.stem(token.lower())
    if stem in dictionary:
        line = linecache.getline(postings_file, int(dictionary[stem]) + 2)
        line = line.strip().split(' ')
        return [int(i) for i in line]
    return []

def convert_to_list(thing):
    """
    Argument:
        thing: either a list of int or str token
    Returns:
        if thing is a token then returns list of int containing postings list of token
        if thing is list then returns thing
    """
    if type(thing) is str:
        return get_postings_list(thing)
    elif type(thing) is list:
        return thing

def _and(list1, list2):
    """
    Arguments:
        list1: list of int
        list2: list of int
    Returns:
        list of int containing set intersection of elements of list1 and list2
    """
    merged = []
    count1 = 0
    count2 = 0
    while count1 != len(list1) and count2 != len(list2):
        int1 = list1[count1]
        int2 = list2[count2]
        if int1 == int2:
            merged.append(int1)
            count1 += 1
            count2 += 1
        elif int1 < int2:
            count1 += 1
        else:
            count2 += 1
    return merged

def _or(list1, list2):
    """
    Arguments:
        list1: list of int
        list2: list of int
    Returns:
        list of int containing set union of elements of list1 and list2
    """
    merged = list1 + [i for i in list2 if i not in list1]
    merged.sort()
    return merged

def _not(listt):
    """
    Argument:
        listt: list of int
    Returns:
        list of int containing set difference of elements of all_postings minus listt
    """
    merged = [i for i in all_postings if i not in listt]
    return merged


# read and execute queries
output_writer = open(output_file, 'w')
with open(queries_file, 'r') as queries_reader:
    for line in queries_reader:
        line = line.strip()
        postfix_list = infix_to_prefix(line)
        result_list = None
        # special case of single token query
        if len(postfix_list) == 1:
            result_list = convert_to_list(postfix_list[0])
        else:
            # postfix_list initially contains only str tokens and operators.
            # the list is traversed front-to-back and operations are executed.
            # after each operation, the operand(s) and operators are removed from the list,
            # and the result of the operation is inserted back to the list at that location
            # the index is updated accordingly to read every item once
            index = 0
            while len(postfix_list) > 1:
                item = postfix_list[index]
                if item == "NOT":
                    listt = convert_to_list(postfix_list[index-1])
                    result = _not(listt)
                    del postfix_list[index-1]
                    del postfix_list[index-1]
                    postfix_list.insert(index-1, result)
                elif item == "AND":
                    list1 = convert_to_list(postfix_list[index-1])
                    list2 = convert_to_list(postfix_list[index-2])
                    result = _and(list1, list2)
                    del postfix_list[index-2]
                    del postfix_list[index-2]
                    del postfix_list[index-2]
                    postfix_list.insert(index-2, result)
                    index -= 1
                elif item == "OR":
                    list1 = convert_to_list(postfix_list[index-1])
                    list2 = convert_to_list(postfix_list[index-2])
                    result = _or(list1, list2)
                    del postfix_list[index-2]
                    del postfix_list[index-2]
                    del postfix_list[index-2]
                    postfix_list.insert(index-2, result)
                    index -= 1
                else:   # a str token or list, advance by 1
                    index += 1
            result_list = postfix_list[0]
        # write to output file
        output = ''
        for i in result_list:
            output = "%s%s " % (output, str(i))
        output = output.rstrip()
        output_writer.write('%s\n' % output)
output_writer.close()
