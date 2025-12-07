import math
import numpy as np
from collections import Counter
from PIL import Image

# =======================
# RUN-LENGTH ENCODING (RLE)
# =======================
def rle_compress(text):
    compressed = []
    i = 0
    while i < len(text):
        count = 1
        while i + 1 < len(text) and text[i] == text[i + 1]:
            i += 1
            count += 1
        compressed.append(f"{text[i]}{count}")
        i += 1
    return ''.join(compressed)

def rle_decompress(compressed):
    decompressed = ""
    i = 0
    while i < len(compressed):
        char = compressed[i]
        i += 1
        count = ""
        while i < len(compressed) and compressed[i].isdigit():
            count += compressed[i]
            i += 1
        decompressed += char * int(count)
    return decompressed

# =======================
# HUFFMAN CODING
# =======================
class Node:
    def __init__(self, char, freq):
        self.char = char
        self.freq = freq
        self.left = None
        self.right = None

    def __lt__(self, other):
        return self.freq < other.freq

def huffman_compress(text):
    freq = Counter(text)
    heap = [Node(char, freq[char]) for char in freq]

    while len(heap) > 1:
        heap.sort(key=lambda x: x.freq)
        left = heap.pop(0)
        right = heap.pop(0)
        merged = Node(None, left.freq + right.freq)
        merged.left = left
        merged.right = right
        heap.append(merged)

    root = heap[0]
    codes = {}

    def generate_codes(node, current_code=""):
        if node is None:
            return
        if node.char is not None:
            codes[node.char] = current_code
        generate_codes(node.left, current_code + "0")
        generate_codes(node.right, current_code + "1")

    generate_codes(root)
    encoded_text = ''.join(codes[ch] for ch in text)
    return encoded_text, codes

def huffman_decompress(encoded_text, codes):
    reverse_codes = {v: k for k, v in codes.items()}
    decoded_text = ""
    temp = ""
    for bit in encoded_text:
        temp += bit
        if temp in reverse_codes:
            decoded_text += reverse_codes[temp]
            temp = ""
    return decoded_text

# =======================
# GOLOMB CODING
# =======================
def unary_encode(q: int) -> str:
    return "1" * q + "0"

def golomb_encode(n: int, m: int) -> str:
    q = n // m
    r = n % m
    quotient_code = unary_encode(q)

    if (m & (m - 1)) == 0:  # power of 2
        k = int(math.log2(m))
        remainder_code = format(r, f'0{k}b')
    else:  # truncated binary
        b = math.ceil(math.log2(m))
        T = 2**b - m
        if r < T:
            remainder_code = format(r, f'0{b-1}b')
        else:
            remainder_code = format(r + T, f'0{b}b')
    return quotient_code + remainder_code

def unary_decode(code: str) -> (int, str): # type: ignore
    q = 0
    while code and code[0] == '1':
        q += 1
        code = code[1:]
    if code and code[0] == '0':
        code = code[1:]
    return q, code

def golomb_decode(code: str, m: int) -> int:
    q, remaining_bits = unary_decode(code)
    if (m & (m - 1)) == 0:
        k = int(math.log2(m))
        r_bits = remaining_bits[:k]
        r = int(r_bits, 2)
    else:
        b = math.ceil(math.log2(m))
        T = 2**b - m
        r_bits = remaining_bits[:b-1]
        r = int(r_bits, 2)
        if r >= T:
            r_bits = remaining_bits[:b]
            r = int(r_bits, 2) - T
    n = q * m + r
    return n

# =======================
# LZW CODING
# =======================
def lzw_compress(text):
    dictionary = {chr(i): i for i in range(256)}  # map character to ASCII
    next_code = 256
    current_c = ""
    result = []

    for next_n in text:
        combined = current_c + next_n
        if combined in dictionary:
            current_c = combined
        else:
            if current_c != "":
                result.append(dictionary[current_c])
            dictionary[combined] = next_code
            next_code += 1
            current_c = next_n

    if current_c != "":
        result.append(dictionary[current_c])

    return result

def lzw_decompress(compressed_codes):
    dictionary = {i: chr(i) for i in range(256)}
    next_code = 256

    prev_code = compressed_codes[0]
    decoded = dictionary[prev_code]
    result = [decoded]

    for code in compressed_codes[1:]:
        if code in dictionary:
            entry = dictionary[code]
        elif code == next_code:
            entry = decoded + decoded[0]
        else:
            raise ValueError(f"Invalid LZW code: {code}")

        result.append(entry)
        dictionary[next_code] = decoded + entry[0]
        next_code += 1
        decoded = entry

    return "".join(result)

# =======================
# LOSSY IMAGE COMPRESSION (QUANTIZATION)
# =======================
def quantize_image(image: Image.Image, levels: int = 16) -> Image.Image:
    image = image.convert("L")  # Convert to grayscale
    arr = np.array(image)
    arr = (arr // (256 // levels)) * (256 // levels)
    return Image.fromarray(arr.astype(np.uint8))
