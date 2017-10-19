#!/usr/bin/env python
'''
Read images and labels
Serialize to string
Store to Database
'''

import sys
import definition_pb2 as pb2
import numpy as np
from PIL import Image
from multiprocessing import Pool

def generate_datum(sample):
    '''
    Arg: a line, seperated by space [imagepath label]
    Read image and store the values into pb blob
    '''

    words = sample.replace('\n','').split(' ')
    assert len(words)>=2

    ### read image ###
    imagepath = words[0]
    image = Image.open(imagepath)
    src = np.array(image)
    if src is None:
        print 'Empty Image. '
        return None
    # image structue
    if len(src.shape)==3:
        height, width, channel = src.shape
    else:
        height, width = src.shape
        channel = 1
    
    pbdatum = pb2.Datum()
    pbdatum.channels = channel
    pbdatum.height = height
    pbdatum.width = width
    # image data store in bytes
    pbdatum.data = src.tobytes()

    ### labels ###
    labels = words[1:]
    if len(labels)==1: # one label only, typical classification
        label = int(labels[0])
        pbdatum.label = label
    else:
        labels = words[1:]
        for ele in labels:
            pbdatum.float_data.append(int(ele))

    return pbdatum


def generate_datums_multi(samples):
    ''' using Pool to parallel '''
    pool = Pool()
    datums = pool.map(generate_datum, samples)
    pool.close()
    pool.join()

    return datums

import lmdb
def write_lmdb(filepath, dbpath):
    ''' commit transaction '''
    infile = open(filepath, 'r')
    lines = infile.readlines()
    datums = generate_datums_multi(lines)
    env = lmdb.open(dbpath, map_size=750000*sys.getsizeof(datums[0])*len(datums))
    txn = env.begin(write = True)
    for index in xrange(len(datums)):
        txn.put(str(index), datums[index].SerializeToString())
    txn.commit()
    env.close()

import argparse
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='the list file recording all images and labels.')
    parser.add_argument('dbpath', help='a folder keeping all data.')
    args = parser.parse_args()

    write_lmdb(args.filepath, args.dbpath)

if __name__ == '__main__':
    main()


