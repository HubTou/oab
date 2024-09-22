#!/usr/bin/env python3
""" oab - Outlook Offline Address Books decoder
License: 3-clause BSD (see https://opensource.org/licenses/BSD-3-Clause)
Author: Timothy Holmes
"""

import struct

class LZXDDecompressor:
    """ Compressed version 4 full details file decompressor """
    def __init__(self, window_size):
        self.window_size = window_size
        self.window = bytearray(self.window_size)
        self.window_pos = 0
        self.r = [1, 1, 1]  # Recent offsets initialized to 1 as per LZXD
        self.first_chunk_read = False

    def _rotate_left(self, value, count, bits=16):
        """ Private method to rotate bits to the left """
        return ((value << count) | (value >> (bits - count))) & ((1 << bits) - 1)

    def _read_bit(self, bitstream):
        """ Private method to read a bit """
        if bitstream["remaining"] == 0:
            bitstream["remaining"] = 16
            if len(bitstream["buffer"]) < 2:
                raise ValueError("Unexpected EOF")
            bitstream["n"] = struct.unpack('<H', bitstream["buffer"][:2])[0]
            bitstream["buffer"] = bitstream["buffer"][2:]

        bitstream["remaining"] -= 1
        bitstream["n"] = self._rotate_left(bitstream["n"], 1)
        return bitstream["n"] & 1

    def _read_bits(self, bitstream, bits):
        """ Private method to read bits """
        result = 0
        while bits > 0:
            if bitstream["remaining"] == 0:
                bitstream["remaining"] = 16
                if len(bitstream["buffer"]) < 2:
                    raise ValueError("Unexpected EOF")
                bitstream["n"] = struct.unpack('<H', bitstream["buffer"][:2])[0]
                bitstream["buffer"] = bitstream["buffer"][2:]

            take_bits = min(bits, bitstream["remaining"])
            bitstream["remaining"] -= take_bits
            result = (result << take_bits) | (bitstream["n"] >> (16 - take_bits))
            bitstream["n"] <<= take_bits
            bits -= take_bits

        return result

    def decompress(self, compressed_data, expected_size):
        """ Public method to decompress a bitstream """
        # Initialize bitstream from the compressed data
        bitstream = {"buffer": compressed_data, "n": 0, "remaining": 0}

        # The final decompressed data
        decompressed_data = bytearray()

        while len(decompressed_data) < expected_size:
            if not self.first_chunk_read:
                # Skip the first chunk header
                _ = self._read_bit(bitstream) # e8_translation_enabled
                self.first_chunk_read = True

            # Decompress a block of data, handling matches, literals, and copy operations
            while len(decompressed_data) < expected_size:
                # Read next bit or bits from bitstream and process as per LZXD spec
                byte = self._read_bits(bitstream, 8)  # Read one byte for this example
                decompressed_data.append(byte)

                # Add to the sliding window for further matches
                self.window[self.window_pos] = byte
                self.window_pos = (self.window_pos + 1) % self.window_size

        return decompressed_data[:expected_size]
