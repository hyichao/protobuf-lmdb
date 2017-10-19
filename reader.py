#!/usr/bin/env python
'''
Read images and labels from db
De-Serialize to numpy array
'''

import numpy as np
import definition_pb2 as pb2
import cv2
from PIL import Image

def read_db(dbname):
    ''' read binary data from dbfile'''
    with open(dbname, 'rb') as dbfile:
        read_str = dbfile.read()
        datum = pb2.Datum()
        datum.ParseFromString(read_str)
        dbfile.close()
        return datum

import lmdb
def read_lmdb(dbname):
    
    env = lmdb.open(dbname)
    txn = env.begin()
    cur = txn.cursor()
    for _, value in cur:
        datum = pb2.Datum()
        datum.ParseFromString(value)
        display(datum)

def display(datum):
    ''' apply datum for own used'''
    # print datum
    if datum.HasField('label'):
        print datum.label
    if datum.HasField('data'):
        dst = np.fromstring(datum.data, dtype=np.uint8)
        if datum.channels==1:
            dst = dst.reshape(datum.height,datum.width)                        
            img = Image.fromarray(dst, 'P')
        else:
            dst = dst.reshape(datum.height,datum.width,datum.channels)            
            img = Image.fromarray(dst, 'RGB')
        img.show()

import argparse
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dbpath", help="a folder keeping all data.")
    args = parser.parse_args()
    read_lmdb(args.dbpath)

if __name__ == '__main__':
    main()