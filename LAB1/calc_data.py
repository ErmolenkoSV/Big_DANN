import os
import struct
import time
import argparse
import mmap
import multiprocessing

def read_sequential(filename):
    file_size = os.path.getsize(filename)
    if file_size % 4 != 0:
        raise ValueError("File size must be divisible by 4")
    
    min_num = None
    max_num = None
    total = 0
    with open(filename, 'rb') as f:
        while True:
            chunk = f.read(1024 * 1024)  # Чтение по 1 МБ
            if not chunk:
                break
            for i in range(0, len(chunk), 4):
                num = struct.unpack_from('>I', chunk, i)[0]
                total += num
                if min_num is None or num < min_num:
                    min_num = num
                if max_num is None or num > max_num:
                    max_num = num
    return total, min_num, max_num

def process_chunk(data):
    min_num = None
    max_num = None
    total = 0
    for i in range(0, len(data), 4):
        num = struct.unpack_from('>I', data, i)[0]
        total += num
        if min_num is None or num < min_num:
            min_num = num
        if max_num is None or num > max_num:
            max_num = num
    return (total, min_num, max_num)

def worker(start, end, filename, queue):
    with open(filename, 'rb') as f:
        mm = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
        chunk = mm[start:end]
        result = process_chunk(chunk)
        queue.put(result)
        mm.close()

def read_parallel(filename):
    file_size = os.path.getsize(filename)
    if file_size % 4 != 0:
        raise ValueError("File size must be divisible by 4")
    
    num_processes = multiprocessing.cpu_count()
    chunk_size = file_size // num_processes
    chunk_size = (chunk_size + 3) // 4 * 4  # Выравнивание по 4 байтам
    
    chunks = []
    for i in range(num_processes):
        start = i * chunk_size
        end = start + chunk_size
        if i == num_processes - 1:
            end = file_size
        chunks.append((start, end))
    
    queue = multiprocessing.Queue()
    processes = []
    
    for start, end in chunks:
        p = multiprocessing.Process(target=worker, args=(start, end, filename, queue))
        processes.append(p)
        p.start()
    
    total = 0
    min_num = None
    max_num = None
    
    for _ in range(len(chunks)):
        chunk_total, chunk_min, chunk_max = queue.get()
        total += chunk_total
        if min_num is None or (chunk_min is not None and chunk_min < min_num):
            min_num = chunk_min
        if max_num is None or (chunk_max is not None and chunk_max > max_num):
            max_num = chunk_max
    
    for p in processes:
        p.join()
    
    return total, min_num, max_num

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Calculate sum, min, and max of a binary file.')
    parser.add_argument('filename', type=str, help='The binary file to process')
    parser.add_argument('--multiprocessing', action='store_true', help='Use multiprocessing version')
    args = parser.parse_args()

    start_time = time.time()
    if args.multiprocessing:
        total, min_num, max_num = read_parallel(args.filename)
    else:
        total, min_num, max_num = read_sequential(args.filename)
    end_time = time.time()

    print(f"Sum: {total}")
    print(f"Min: {min_num}")
    print(f"Max: {max_num}")
    print(f"Time taken: {end_time - start_time:.2f} seconds")
