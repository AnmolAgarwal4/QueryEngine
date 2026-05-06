#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <time.h>

#define MAX_TERMS    5000
#define MAX_DOCS     1000
#define MAX_WORD_LEN 64
#define HASH_SIZE    4096

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
    IndexEntry entries[MAX_TERMS];
    int        table[HASH_SIZE];
    int        term_count;
} InvertedIndex;

typedef struct {
    int    doc_ids[MAX_DOCS];
    int    frequencies[MAX_DOCS];
    int    count;
    double latency_ms;
} SearchResult;

static unsigned int hash_term(const char *term) {
    unsigned int h = 5381;
    while (*term)
        h = ((h << 5) + h) ^ (unsigned char)*term++;
    return h & (HASH_SIZE - 1);
}

static void to_lower(char *s) {
    for (; *s; s++) *s = (char)tolower((unsigned char)*s);
}

void init_index(InvertedIndex *idx) {
    idx->term_count = 0;
    memset(idx->table, -1, sizeof(idx->table));
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
            idx->entries[i].postings[pc].doc_id    = doc_id;
            idx->entries[i].postings[pc].frequency = 1;
            idx->entries[i].posting_count++;
            return;
        }
        i = idx->entries[i].next;
    }

    if (idx->term_count >= MAX_TERMS) {
        fprintf(stderr, "Index full\n");
        return;
    }

    int e = idx->term_count++;
    strncpy(idx->entries[e].term, term, MAX_WORD_LEN);
    idx->entries[e].postings[0].doc_id    = doc_id;
    idx->entries[e].postings[0].frequency = 1;
    idx->entries[e].posting_count         = 1;
    idx->entries[e].next                  = idx->table[slot];
    idx->table[slot]                      = e;
}

SearchResult search_term(InvertedIndex *idx, const char *raw_term) {
    SearchResult result;
    result.count      = 0;
    result.latency_ms = 0.0;

    char term[MAX_WORD_LEN];
    strncpy(term, raw_term, MAX_WORD_LEN - 1);
    term[MAX_WORD_LEN - 1] = '\0';
    to_lower(term);

    clock_t start        = clock();
    unsigned int slot    = hash_term(term);
    int i                = idx->table[slot];

    while (i != -1) {
        if (strcmp(idx->entries[i].term, term) == 0) {
            for (int j = 0; j < idx->entries[i].posting_count; j++) {
                result.doc_ids[j]     = idx->entries[i].postings[j].doc_id;
                result.frequencies[j] = idx->entries[i].postings[j].frequency;
                result.count++;
            }
            result.latency_ms = (double)(clock() - start) / CLOCKS_PER_SEC * 1000.0;
            return result;
        }
        i = idx->entries[i].next;
    }

    result.latency_ms = (double)(clock() - start) / CLOCKS_PER_SEC * 1000.0;
    return result;
}

int main(void) {
    InvertedIndex *idx = create_index();

    add_term(idx, "search", 1);
    add_term(idx, "engine", 1);
    add_term(idx, "search", 2);
    add_term(idx, "fast",   2);
    add_term(idx, "engine", 3);
    add_term(idx, "fast",   3);
    add_term(idx, "search", 3);

    SearchResult r = search_term(idx, "search");
    printf("Found %d results\n", r.count);
    for (int i = 0; i < r.count; i++) {
        printf("doc_id=%d freq=%d\n", r.doc_ids[i], r.frequencies[i]);
    }
    printf("Latency: %.4f ms\n", r.latency_ms);

    fflush(stdout);
    free_index(idx);
    return 0;
}