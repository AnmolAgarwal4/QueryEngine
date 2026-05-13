#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <math.h>
#include <time.h>

#define MAX_TERMS    50000
#define MAX_DOCS     10000
#define MAX_WORD_LEN 64
#define HASH_SIZE    16384
#define DOC_HASH     32768
#define BM25_K1      1.5f
#define BM25_B       0.75f

typedef struct {
    int doc_id;
    int frequency;
} Posting;

typedef struct {
    char    term[MAX_WORD_LEN];
    Posting postings[MAX_DOCS];
    int     posting_count;
    int     next;
} IndexEntry;

typedef struct {
    int doc_id;
    int internal_idx;
    int next;
} DocMap;

typedef struct {
    IndexEntry entries[MAX_TERMS];
    int        table[HASH_SIZE];
    int        term_count;

    DocMap     docs[MAX_DOCS];
    int        doc_table[DOC_HASH];
    int        doc_lengths[MAX_DOCS];
    int        total_docs;
    float      avg_doc_length;
} InvertedIndex;

typedef struct {
    int    doc_ids[MAX_DOCS];
    float  scores[MAX_DOCS];
    int    count;
    double latency_ms;
} SearchResult;

static unsigned int hash_term(const char *term) {
    unsigned int h = 5381;
    while (*term)
        h = ((h << 5) + h) ^ (unsigned char)*term++;
    return h & (HASH_SIZE - 1);
}

static unsigned int hash_doc(int doc_id) {
    unsigned int h = (unsigned int)doc_id;
    h = ((h >> 16) ^ h) * 0x45d9f3b;
    h = ((h >> 16) ^ h) * 0x45d9f3b;
    h = (h >> 16) ^ h;
    return h & (DOC_HASH - 1);
}

static void to_lower(char *s) {
    for (; *s; s++) *s = (char)tolower((unsigned char)*s);
}

static int get_or_create_internal(InvertedIndex *idx, int doc_id) {
    unsigned int slot = hash_doc(doc_id);
    int i = idx->doc_table[slot];
    while (i != -1) {
        if (idx->docs[i].doc_id == doc_id) return idx->docs[i].internal_idx;
        i = idx->docs[i].next;
    }
    if (idx->total_docs >= MAX_DOCS) return -1;

    int new_idx = idx->total_docs++;
    idx->docs[new_idx].doc_id       = doc_id;
    idx->docs[new_idx].internal_idx = new_idx;
    idx->docs[new_idx].next         = idx->doc_table[slot];
    idx->doc_table[slot]            = new_idx;
    idx->doc_lengths[new_idx]       = 0;
    return new_idx;
}

void init_index(InvertedIndex *idx) {
    idx->term_count     = 0;
    idx->total_docs     = 0;
    idx->avg_doc_length = 0.0f;
    memset(idx->table, -1, sizeof(idx->table));
    memset(idx->doc_table, -1, sizeof(idx->doc_table));
    memset(idx->doc_lengths, 0, sizeof(idx->doc_lengths));
}

InvertedIndex *create_index(void) {
    InvertedIndex *idx = malloc(sizeof(InvertedIndex));
    init_index(idx);
    return idx;
}

void free_index(InvertedIndex *idx) {
    free(idx);
}

void add_term(InvertedIndex *idx, const char *raw_term, int doc_id) {
    char term[MAX_WORD_LEN];
    strncpy(term, raw_term, MAX_WORD_LEN - 1);
    term[MAX_WORD_LEN - 1] = '\0';
    to_lower(term);

    int internal = get_or_create_internal(idx, doc_id);
    if (internal < 0) return;
    idx->doc_lengths[internal]++;

    unsigned int slot = hash_term(term);
    int i = idx->table[slot];

    while (i != -1) {
        if (strcmp(idx->entries[i].term, term) == 0) {
            for (int j = 0; j < idx->entries[i].posting_count; j++) {
                if (idx->entries[i].postings[j].doc_id == doc_id) {
                    idx->entries[i].postings[j].frequency++;
                    return;
                }
            }
            int pc = idx->entries[i].posting_count;
            if (pc >= MAX_DOCS) return;
            idx->entries[i].postings[pc].doc_id    = doc_id;
            idx->entries[i].postings[pc].frequency = 1;
            idx->entries[i].posting_count++;
            return;
        }
        i = idx->entries[i].next;
    }

    if (idx->term_count >= MAX_TERMS) return;

    int e = idx->term_count++;
    strncpy(idx->entries[e].term, term, MAX_WORD_LEN);
    idx->entries[e].postings[0].doc_id    = doc_id;
    idx->entries[e].postings[0].frequency = 1;
    idx->entries[e].posting_count         = 1;
    idx->entries[e].next                  = idx->table[slot];
    idx->table[slot]                      = e;
}

void finalize_index(InvertedIndex *idx) {
    if (idx->total_docs == 0) {
        idx->avg_doc_length = 0.0f;
        return;
    }
    long total = 0;
    for (int i = 0; i < idx->total_docs; i++)
        total += idx->doc_lengths[i];
    idx->avg_doc_length = (float)total / idx->total_docs;
}

static int find_internal(InvertedIndex *idx, int doc_id) {
    unsigned int slot = hash_doc(doc_id);
    int i = idx->doc_table[slot];
    while (i != -1) {
        if (idx->docs[i].doc_id == doc_id) return idx->docs[i].internal_idx;
        i = idx->docs[i].next;
    }
    return -1;
}

static float compute_bm25(int tf, int df, int total_docs, int doc_len, float avg_doc_len) {
    float idf = logf(((float)(total_docs - df) + 0.5f) / ((float)df + 0.5f) + 1.0f);
    float norm = (float)tf * (BM25_K1 + 1.0f);
    float denom = (float)tf + BM25_K1 * (1.0f - BM25_B + BM25_B * ((float)doc_len / avg_doc_len));
    return idf * (norm / denom);
}

SearchResult search_term(InvertedIndex *idx, const char *raw_term) {
    SearchResult result;
    result.count      = 0;
    result.latency_ms = 0.0;

    char term[MAX_WORD_LEN];
    strncpy(term, raw_term, MAX_WORD_LEN - 1);
    term[MAX_WORD_LEN - 1] = '\0';
    to_lower(term);

    clock_t start     = clock();
    unsigned int slot = hash_term(term);
    int i             = idx->table[slot];

    if (idx->avg_doc_length == 0.0f) finalize_index(idx);

    while (i != -1) {
        if (strcmp(idx->entries[i].term, term) == 0) {
            int df = idx->entries[i].posting_count;
            int written = 0;
            int cap = MAX_DOCS < df ? MAX_DOCS : df;
            for (int j = 0; j < cap; j++) {
                int doc_id   = idx->entries[i].postings[j].doc_id;
                int tf       = idx->entries[i].postings[j].frequency;
                int internal = find_internal(idx, doc_id);
                int doc_len  = (internal >= 0) ? idx->doc_lengths[internal] : 1;
                float score  = compute_bm25(tf, df, idx->total_docs, doc_len, idx->avg_doc_length);

                result.doc_ids[written] = doc_id;
                result.scores[written]  = score;
                written++;
            }
            result.count = written;
            result.latency_ms = (double)(clock() - start) / CLOCKS_PER_SEC * 1000.0;
            return result;
        }
        i = idx->entries[i].next;
    }

    result.latency_ms = (double)(clock() - start) / CLOCKS_PER_SEC * 1000.0;
    return result;
}

int main(void) {
    return 0;
}