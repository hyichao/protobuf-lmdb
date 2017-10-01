#!/usr/bin/env python
'''
Read images and labels
Serialize to string
Store to Database
'''

import sys
import definition_pb2 as pb2
import cv2
import numpy as np
from multiprocessing import Pool

def generate_datum(sample):
    '''
    Arg: a tuple (imagepath, label)
    Read image and store the values into pb blob
    '''
    assert type(sample) is tuple
    
    imagepath = sample[0]
    label = sample[1]

    # read image
    src = cv2.imread(imagepath)
    if src is None:
        print 'Empty Image. '
        return None
    # image structue
    channel, height, width = src.shape

    pbdatum = pb2.Datum()
    pbdatum.channels = channel
    pbdatum.height = height
    pbdatum.width = width
    # image data store in bytes
    pbdatum.data = src.tobytes()
    # labels 
    pbdatum.label = label

    return pbdatum

# def generate_datums():
#     samples = []
#     for item in xrange(0,10):
#         sample = ('lena.jpg', 0)
#         samples.append(sample)

#     for sample in samples:        
#         generate_datum(sample)

#     return datum

def generate_datums_multi():
    samples = []
    for item in xrange(0,1):
        sample = ('lena.jpg', 0)
        samples.append(sample)

    pool = Pool()
    datums = pool.map(generate_datum, samples)
    pool.close()
    pool.join()

    return datums

# def write_db():
#     datums = generate_datums()
    
#     filepath = 'images.db'
#     # write to file
#     with open(filepath, 'wb') as dbfile:
#         dbfile.write(datum.SerializeToString())
#         dbfile.close()

import lmdb
def write_lmdb():
    datums = generate_datums_multi()
    env = lmdb.open("imagedb",map_size=750000*sys.getsizeof(datums[0])*len(datums))
    txn = env.begin(write = True)
    for index in xrange(len(datums)):
        txn.put(str(index), datums[index].SerializeToString())
    txn.commit()
    env.close()

def main():
    write_lmdb()

if __name__ == '__main__':
    main()


