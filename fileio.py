#!/bin/env/python
'''read in or write out file, standard utf16'''

import os

# charset
def read_utf16_charset(filename):
    '''unicode charset file'''
    print 'read charset file, should be encoded with utf16'
    with open(filename, 'r') as infile:
        charset = infile.read().decode('utf16')
        charset = sorted(charset)
        print str(len(charset))+' unicodes wanted'
        return charset

# file list
def read_utf16_file(filename):
    '''read utf16 encoded file'''
    print 'read utf16 file'
    with open(filename, 'r') as infile:
        lines = infile.read().decode('utf16').split('\n')
        print str(len(lines))+' lines read in. i.e.'
        print lines[:2]
        return lines

def write_utf16_file(filename, lines):
    '''write utf8 encoded file'''
    with open(filename, 'w') as outfile:
        for line in lines:
            line += '\n'
            outfile.write(line.encode('utf16'))


def translate_lines_by_charset(lines, charset):
    '''as name tells'''
    charset_mapping = {}
    for index,onechar in enumerate(charset):
        charset_mapping[onechar] = index


    samples = []
    for line in lines:
        words = line.split('\t')
        if len(words)!=2:
            print 'less than two elements: '+line
            continue
        path = words[0]
        label = words[1]

        sample = [path.encode('utf8')]
        for unic in label:
            sample.append(charset_mapping[unic])
        # print sample
        samples.append(sample)

    print 'translate from unicodes into int arrays, i.e. '
    print lines[:1]
    print samples[:1]
    return samples

if __name__ == "__main__":

    charsetpath = '/home/charlie/plate/charset.txt'
    if not os.path.exists(charsetpath):
        print 'error path: '+charsetpath
    charset = read_utf16_charset(charsetpath)
    print charset

    filepath = '/home/charlie/plate/test.txt'
    if not os.path.exists(filepath):
        print 'error path: '+filepath

    lines = read_utf16_file(filepath)
    samples = translate_lines_by_charset(lines,charset)