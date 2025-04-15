import os
import struct

def main():
    filename = 'data.bin'
    size_gb = 2
    num_bytes = size_gb * 1024 ** 3  # 2 ГБ в байтах
    chunk_size = 1024 * 1024  # 1 МБ для каждого блока записи

    with open(filename, 'wb') as f:
        bytes_written = 0
        while bytes_written < num_bytes:
            remaining = num_bytes - bytes_written
            current_chunk = min(chunk_size, remaining)
            data = os.urandom(current_chunk)  # Генерация случайных байтов
            f.write(data)
            bytes_written += current_chunk

if __name__ == '__main__':
    main()
