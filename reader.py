#!/usr/bin/env python
'''
Read images and labels from db
De-Serialize to numpy array
'''

import numpy as np
import definition_pb2 as pb2
import cv2
# from PIL import Image
# import matplotlib.pyplot as plt

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
    '''read db with cursor '''
    env = lmdb.open(dbname)
    txn = env.begin()
    cur = txn.cursor()
    for index, value in cur:
        datum = pb2.Datum()
        datum.ParseFromString(value)
        display(index, datum)

def display(index, datum):
    ''' apply datum for own used'''
    # print datum
    if datum.HasField('label'):
        print datum.label
    # if datum.ListFields('float_data'):
    float_data = datum.float_data
    if datum.HasField('data'):
        dst = np.fromstring(datum.data, dtype=np.uint8)
        if datum.channels==1:
            dst = dst.reshape(datum.height,datum.width)                     
            # img = Image.fromarray(dst, 'P')
        else:
            dst = dst.reshape(datum.channels,datum.height,datum.width) 
            dst = dst.transpose(1,2,0) # CHW-->HWC
            # img = Image.fromarray(dst, 'RGB')
        # img.show()
        # fig = plt.figure()  
        # fig.imshow(img)
        # plt.show()
        cv2.imwrite('./images/'+str(index)+'.jpg', dst)

import argparse
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("dbpath", help="a folder keeping all data.")
    args = parser.parse_args()
    read_lmdb(args.dbpath)

if __name__ == '__main__':
    main()