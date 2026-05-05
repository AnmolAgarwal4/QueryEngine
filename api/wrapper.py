import ctypes
import os
import time

lib_path = os.path.join(os.path.dirname(__file__), '..', 'Core', 'lurox_core.dll')
lib = ctypes.CDLL(lib_path)

lib.create_index.restype  = ctypes.c_void_p
lib.add_term.argtypes     = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
lib.search_term.argtypes  = [ctypes.c_void_p, ctypes.c_char_p]
lib.search_term.restype   = ctypes.c_int
lib.free_index.argtypes   = [ctypes.c_void_p]

def create_index():
    return lib.create_index()

def add(index, term, doc_id):
    lib.add_term(index, term.encode('utf-8'), doc_id)

def search(index, term):
    start = time.perf_counter()
    result = lib.search_term(index, term.encode('utf-8'))
    elapsed = (time.perf_counter() - start) * 1000
    return result, round(elapsed, 4)

def free(index):
    lib.free_index(index)

if __name__ == "__main__":
    idx = create_index()
    add(idx, "search", 1)
    add(idx, "engine", 1)
    add(idx, "search", 2)
    add(idx, "fast", 2)

    result, ms = search(idx, "search")
    print(f"Search result: {result} | Time: {ms}ms")

    result, ms = search(idx, "fast")
    print(f"Search result: {result} | Time: {ms}ms")

    free(idx)
    print("Done.")