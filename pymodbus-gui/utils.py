import struct
import binascii

class BytesConversion:
    """
    Class to manipulate  list of words (unsigned 16) to convert to different formats
    """
    def swapBytes(input: list) -> list:
        """
        Swap bytes in a list of 16-bit values.

        :param input: A list of 16-bit values
        :return: A list of 16-bit values with swapped bytes
        """
        newList = []
        for i in input:
            newList.append(struct.unpack('>H', struct.pack('<H', i))[0]) 
        return newList
    
    def swapWords(input: list) -> list:
        """
        Swap words in a list of 16-bit values.

        :param input: A list of 16-bit values
        :return: A list of 16-bit values with swapped words
        """
        newList = []
        for i in range(0, len(input), 2):
            try:
                newList.append(input[i + 1])
            except IndexError:
                print("Index Error at input list")
            finally:
                newList.append(input[i]) 
        return newList
    
    def swapDwords(input: list) -> list:
        """
        Swap double words in a list of 16-bit values.

        :param input: A list of 16-bit values
        :return: A list of 16-bit values with swapped words
        """
        newList = []
        for i in range(0, len(input), 4):
            try:
                newList.append(input[i + 2])
                newList.append(input[i + 3]) 
            except IndexError:
                print("Index Error at input list")
            finally:
                newList.append(input[i + 0])
                try:
                    newList.append(input[i + 1])
                except IndexError:
                    print("Index Error at input list")
        return newList
    
    def toInt16(input: int) -> int:
        """
        Convert a 16-bit unsigned int to a 16-bit signed int.

        :param input: A list of one unsigned 16-bit int
        :return: A signed 16-bit int
        """
        
        return struct.unpack('@h', struct.pack('@H', input))[0]
        
    def toInt32(input: list) -> int:
        """
        Convert two 16-bit values to a 32-bit signed int.

        :param input: A list of two unsigned 16-bit uint
        :return: A signed 32-bit int
        """
        return struct.unpack('@i', struct.pack('@HH', input[0], input[1]))[0]

    def toUInt32(input: list) -> int:
        """
        Convert two 16-bit values to a 32-bit unsigned  int.

        :param input: A list of two unsigned 16-bit uint
        :return: An unsigned 32-bit int
        """
        return struct.unpack('@I', struct.pack('@HH', input[0], input[1]))[0]
    
    def toInt64(input: list) -> int:
        """
        Convert four 16-bit values to a 64-bit signed int.

        :param input: A list of four unsigned 16-bit uint
        :return: A signed 64-bit int
        """
        return struct.unpack('@q', struct.pack('@HHHH', input[0], input[1], input[2], input[3]))[0]

    def toUInt64(input: list) -> int:
        """
        Convert four 16-bit values to a 64-bit unsigned int.

        :param input: A list of four unsigned 16-bit uint
        :return: An unsigned 64-bit int
        """
        return struct.unpack('@Q', struct.pack('@HHHH', input[0], input[1], input[2], input[3]))[0]
    
    def toFloat32(input: list) -> float:
        """
        Convert two 16-bit values to a 32-bit floating point.

        :param input: A list of two unsigned 16-bit uint
        :return: A floatting point
        """
        return struct.unpack('@f', struct.pack('@HH', input[0], input[1]))[0]
    
    def toDouble(input: list) -> int:
        """
        Convert four 16-bit values to a 64-bit double precision floating point.

        :param input: A list of four unsigned 16-bit uint
        :return: A double precision floating point
        """
        return struct.unpack('@d', struct.pack('@HHHH', input[0], input[1], input[2], input[3]))[0]


print(BytesConversion.swapBytes(BytesConversion.swapWords([1,2])))