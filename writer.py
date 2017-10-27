#!/usr/bin/env python
'''
Read images and labels
Serialize to string
Store to Database
'''

import sys
import os
import argparse

import numpy as np
import cv2
from multiprocessing import Pool

import lmdb
import definition_pb2 as pb2
import fileio

RESIZE_HEIGHT=30
RESIZE_WIDTH=360

def generate_datum(sample):
    '''
    Arg: a line, seperated by space [imagepath label]
    Read image and store the values into pb blob
    '''
    assert len(sample)>=2
    
    ### read image ###
    imagepath = sample[0]
    src = cv2.imread(imagepath)
    if src is None:
        print 'Empty Image. '
        return None

    # image pre-processing
    is_color = (len(src.shape)==3) 
    if is_color:
        height, width, channel = src.shape
    else:
        height, width = src.shape
        channel = 1
    nheight = int(RESIZE_HEIGHT)
    nwidth = int( (1.0*RESIZE_HEIGHT/height)*width)
    src = cv2.resize(src,(nwidth,nheight))

    extend = (RESIZE_WIDTH-nwidth)/2
    boarder_value = (128,128,128) if is_color else 128
    if (RESIZE_WIDTH-nwidth)%2==0:
        src = cv2.copyMakeBorder(src,0,0,extend,extend,cv2.BORDER_CONSTANT,value=boarder_value)
    else:
        src = cv2.copyMakeBorder(src,0,0,extend,extend+1,cv2.BORDER_CONSTANT,value=boarder_value)
        
    # image structue
    if is_color:
        height, width, channel = src.shape
    else:
        height, width = src.shape
        channel = 1
    # HWC --> CHW
    src = src.transpose(2,0,1)

    ### generating pbdatum ###
    pbdatum = pb2.Datum()
    pbdatum.channels = channel
    pbdatum.height = height
    pbdatum.width = width
    # image data store in bytes
    pbdatum.data = src.tobytes()

    # labels = sample[1:]
    # if len(labels)==1: # one label only, typical classification
    #     label = int(labels[0])
    #     pbdatum.label = label
    # else:
    labels = sample[1:]
    for ele in labels:
        pbdatum.float_data.append(int(ele))

    return pbdatum


def generate_datums_multi(samples):
    ''' using Pool to parallel '''
    pool = Pool()
    datums = pool.map(generate_datum, samples)
    pool.close()
    pool.join()

    # for sample in samples:
    #     generate_datum(sample)

    datums = [sample for sample in datums if sample is not None]
    print str(len(datums))+' datums created.'
    return datums

def write_lmdb(filepath, charsetpath, dbpath):
    ''' commit transaction '''

    charset = fileio.read_utf16_charset(charsetpath)
    lines = fileio.read_utf16_file(filepath)

    env = lmdb.open(dbpath, map_size=30*300*3*10*3033)
    batch_size = 3000
    batches = len(lines)/batch_size
    counter = 0
    for index in xrange(batches):
        print '----------- batch: '+str(index)+' -----------------'
        sub_lines = lines[index*batch_size:(index+1)*batch_size]    
        samples = fileio.translate_lines_by_charset(sub_lines, charset)
        datums = generate_datums_multi(samples)
        txn = env.begin(write = True)
        for datum_id in xrange(len(datums)):
            txn.put(str(index*batch_size+datum_id), datums[datum_id].SerializeToString())
        txn.commit()
        counter+=len(datums)

    print '----------- the rest -----------------'    
    sub_lines = lines[batches*batch_size:]
    samples = fileio.translate_lines_by_charset(sub_lines, charset)
    datums = generate_datums_multi(samples)
    txn = env.begin(write = True)
    for datum_id in xrange(len(datums)):
        txn.put(str(batches*batch_size+datum_id), datums[datum_id].SerializeToString())
    txn.commit()
    counter+=len(datums)

    print 'total datum size: '+str(counter)
    env.close()

def main():
    ''' parse arguments in main function '''
    parser = argparse.ArgumentParser()
    parser.add_argument('filepath', help='the list file recording all images and labels.')
    parser.add_argument('charset', help='charset file.')
    parser.add_argument('dbpath', help='a folder keeping all data.')
    # parser.add_argument('height', type=int, help='resize to height.')
    # parser.add_argument('width', type=int, help='resize to width.')
    args = parser.parse_args()

    if not os.path.exists(args.filepath):
        print 'error path: '+args.filepath
    if not os.path.exists(args.charset):
        print 'error path: '+args.charset

    write_lmdb(args.filepath, args.charset, args.dbpath)

if __name__ == '__main__':
    main()


