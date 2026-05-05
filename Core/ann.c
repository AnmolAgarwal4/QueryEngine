#include <stdio.h>
#include <stdlib.h>
#include <math.h>
#include <float.h>

#define MAX_DIMS    128
#define MAX_POINTS  10000

typedef struct {
    float  coords[MAX_DIMS];
    int    id;
} Point;

typedef struct KDNode {
    Point         point;
    struct KDNode *left;
    struct KDNode *right;
} KDNode;

static float euclidean_sq(const float *a, const float *b, int dims) {
    float sum = 0.0f;
    for (int i = 0; i < dims; i++) {
        float d = a[i] - b[i];
        sum += d * d;
    }
    return sum;
}

static int cmp_dim;

static int cmp_points(const void *a, const void *b) {
    const Point *pa = (const Point *)a;
    const Point *pb = (const Point *)b;
    if (pa->coords[cmp_dim] < pb->coords[cmp_dim]) return -1;
    if (pa->coords[cmp_dim] > pb->coords[cmp_dim]) return  1;
    return 0;
}

KDNode *build_kdtree(Point *points, int n, int depth, int dims) {
    if (n <= 0) return NULL;

    int axis = depth % dims;
    cmp_dim  = axis;
    qsort(points, n, sizeof(Point), cmp_points);

    int mid = n / 2;

    KDNode *node = malloc(sizeof(KDNode));
    node->point  = points[mid];
    node->left   = build_kdtree(points, mid, depth + 1, dims);
    node->right  = build_kdtree(points + mid + 1, n - mid - 1, depth + 1, dims);

    return node;
}

void nearest_neighbor(KDNode *root, const float *query,
                      int depth, int dims,
                      KDNode **best, float *best_dist) {
    if (!root) return;

    float dist = euclidean_sq(root->point.coords, query, dims);
    if (dist < *best_dist) {
        *best_dist = dist;
        *best      = root;
    }

    int   axis = depth % dims;
    float diff = query[axis] - root->point.coords[axis];

    KDNode *near = diff < 0 ? root->left  : root->right;
    KDNode *far  = diff < 0 ? root->right : root->left;

    nearest_neighbor(near, query, depth + 1, dims, best, best_dist);

    if (diff * diff < *best_dist)
        nearest_neighbor(far, query, depth + 1, dims, best, best_dist);
}

void free_kdtree(KDNode *root) {
    if (!root) return;
    free_kdtree(root->left);
    free_kdtree(root->right);
    free(root);
}

int main(void) {
    int dims = 3;
    int n    = 5;

    Point points[] = {
        {{1.0f, 2.0f, 3.0f}, 1},
        {{4.0f, 5.0f, 6.0f}, 2},
        {{7.0f, 8.0f, 9.0f}, 3},
        {{2.0f, 3.0f, 1.0f}, 4},
        {{5.0f, 1.0f, 4.0f}, 5},
    };

    KDNode *tree = build_kdtree(points, n, 0, dims);

    float query[] = {3.0f, 3.0f, 3.0f};

    KDNode *best      = NULL;
    float   best_dist = FLT_MAX;

    nearest_neighbor(tree, query, 0, dims, &best, &best_dist);

    printf("Query:  [3.0, 3.0, 3.0]\n");
    printf("Nearest: Point ID=%d | dist=%.4f\n",
           best->point.id, sqrtf(best_dist));

    fflush(stdout);
    free_kdtree(tree);
    return 0;
}