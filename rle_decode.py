import os
import sys
import subprocess
from Bio import SeqIO
from concurrent.futures import ThreadPoolExecutor, as_completed

def rle_decode_file(input_file, output_file, chunk_size=1024*1024*100):  # 1MB 청크
    with open(input_file, 'rb') as infile, open(output_file, 'wb') as outfile:
        buffer = bytearray()
        
        while True:
            chunk = infile.read(chunk_size)
            if not chunk:
                break
            
            buffer.extend(chunk)
            
            while len(buffer) >= 2:
                count = (buffer[0] & 0x7F) + 1
                char = buffer[1]
                outfile.write(bytes([char] * count))
                buffer = buffer[2:]
    os.remove(input_file)


def decompress_with_zpaq(id_file, qual_file):
    # 각각 id.zpaq, qual.zpaq 파일 복원
    zpaq_cmd_id = f"zpaq x {id_file}"
    zpaq_cmd_qual = f"zpaq x {qual_file}"
    
    try:
        subprocess.run(zpaq_cmd_id, shell=True, check=True)
        subprocess.run(zpaq_cmd_qual, shell=True, check=True)
        print(f"복원된 파일: {id_file}.zpaq, {qual_file}.zpaq")
    except subprocess.CalledProcessError as e:
        print(f"복원 중 오류 발생: {e}")

    os.remove(f"{id_file}")
    os.remove(f"{qual_file}")
    
    

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python3 split_id_qual.py <id_file> <qual_file>")
        sys.exit(1)
    
    id_file = sys.argv[1]
    qual_file = sys.argv[2]

    qual_basename = os.path.basename(qual_file)
    
    # id.zpaq와 qual.zpaq 압축 해제
    decompress_with_zpaq(id_file, qual_file)
    
    # qual 파일 RLE 디코딩
    qual_decompressed_file = f"{qual_basename}_decompess.txt"
    rle_decode_file(f"{qual_basename}.txt", qual_decompressed_file)

