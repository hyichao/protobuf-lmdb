## Play Around with Protobuf+LMDB
Try to use protobuf python wrapper to enhance daily working efficiency.

### Installation

* option 1. using pre-build

```
# Ubuntu
sudo apt-get install protobuf-compiler
# Mac
brew install protobuf
```
After Installation, check the protobuffer compiler

```
protoc --version
```

Then install its python library with pip

```
pip install protobuf
```

* Option 2. Using source code.. which is not recommanded

```
git clone https://github.com/google/protobuf.git
# follow its README
```

### Prepare .proto file

ProtoBuffer required a definition file of your own data structure. i.e. the `definition.proto` file in our example. FYI. this proto file contains a message named `Datum`, which is copied from [CAFFE](https://github.com/BVLC/caffe/blob/master/src/caffe/proto/caffe.proto).

```
protoc --python_out=. definition.proto
```

with the 'compile' command, a file will be generated named with `**_pb2.py`, which will be used in your actual py script

### Read & Write

As two scripts shows, `reader.py` and `writer.py`
In order to apply the tech into daily working with CAFFE, lmdb support is added.

```
pip install lmdb
```

using lmdb in python is pretty easy, please ref to these two py scripts.

with all prerequest, all three steps to play around is as follows.

```
git clone https://github.com/hyichao/protobuf-lmdb.git
cd protobuf-lmdb
protoc --python_out=. definition.proto
python writer.py
python reader.py
```