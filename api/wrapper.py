import ctypes
import os
import platform

ext = '.dll' if platform.system() == 'Windows' else '.so'
lib_path = os.path.join(os.path.dirname(__file__), '..', 'Core', f'lurox_core{ext}')
lib = ctypes.CDLL(lib_path)

MAX_DOCS = 1000

class SearchResult(ctypes.Structure):
    _fields_ = [
        ("doc_ids",     ctypes.c_int * MAX_DOCS),
        ("frequencies", ctypes.c_int * MAX_DOCS),
        ("count",       ctypes.c_int),
        ("latency_ms",  ctypes.c_double),
    ]

lib.create_index.restype  = ctypes.c_void_p
lib.add_term.argtypes     = [ctypes.c_void_p, ctypes.c_char_p, ctypes.c_int]
lib.search_term.argtypes  = [ctypes.c_void_p, ctypes.c_char_p]
lib.search_term.restype   = SearchResult
lib.free_index.argtypes   = [ctypes.c_void_p]

def create_index():
    return lib.create_index()

def add(index, term, doc_id):
    lib.add_term(index, term.encode('utf-8'), doc_id)

def search(index, term):
    result = lib.search_term(index, term.encode('utf-8'))
    docs = [
        {"doc_id": result.doc_ids[i], "freq": result.frequencies[i]}
        for i in range(result.count)
    ]
    return docs, round(result.latency_ms, 4)

def free(index):
    lib.free_index(index)