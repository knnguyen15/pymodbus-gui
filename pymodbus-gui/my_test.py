import sys
import struct
import binascii

a =[0, 2, 4, 8]
print(binascii.hexlify(struct.pack('@HH', 0, 16656)))
print(struct.unpack('f', struct.pack('f', 9.0))[0])
print(struct.unpack('f', struct.pack('@HH', 0, 16656))[0])

print(binascii.hexlify(struct.pack('>HH', 0, 65534)))