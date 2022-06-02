#include <Python.h>
#include <math.h>
#include <stdio.h>
#include <stdlib.h>

static inline int eq(double a, double b) {
	return a == b;
}

struct bin {
	double centroid;
	unsigned long count;
};

PyObject histogram {
	struct bin *bins;
	unsigned max_bins;
	unsigned num_bins;
	unsigned gap;
	unsigned long count;
	double min;
	double max;
};

static PyObject histogram* histogram_new(unsigned max_bins) {
	struct histogram *h = malloc(sizeof(struct histogram));
	h->bins = calloc(max_bins + 1, sizeof(struct bin));
	h->max_bins = max_bins;
	h->num_bins = 0;
	h->gap = 0;
	h->count = 0;
	h->min = INFINITY;
	h->max = -INFINITY;
	return h;
}

static void histogram_free(struct histogram *h) {
	free(h->bins);
	free(h);
}

static void histogram_update(struct histogram *h, double observation) {
	unsigned bin;
	double delta;
	double min_delta = INFINITY;

	++(h->count);
	if (observation < h->min)
		h->min = observation;
	if (observation > h->max)
		h->max = observation;

	while (1) {
		if (h->gap != 0) {
			if (h->bins[h->gap - 1].centroid > observation) {
				h->bins[h->gap] = h->bins[h->gap - 1];
				--(h->gap);
				continue;
			}
			if (eq(h->bins[h->gap - 1].centroid, observation)) {
				++(h->bins[h->gap - 1].count);
				return;
			}
		}

		if (h->gap != h->num_bins) {
			if (h->bins[h->gap + 1].centroid < observation) {
				h->bins[h->gap] = h->bins[h->gap + 1];
				++(h->gap);
				continue;
			}
			if (eq(h->bins[h->gap + 1].centroid, observation)) {
				++(h->bins[h->gap + 1].count);
				return;
			}
		}

		break;
	}

	h->bins[h->gap].centroid = observation;
	h->bins[h->gap].count = 1;

	if (h->num_bins != h->max_bins) {
		h->gap = ++(h->num_bins);
		return;
	}

	for (bin = 0; bin < h->num_bins; ++bin) {
		delta = h->bins[bin + 1].centroid - h->bins[bin].centroid;
		if (delta < min_delta) {
			min_delta = delta;
			h->gap = bin;
		}
	}
	h->bins[h->gap + 1].centroid =
		(h->bins[h->gap].centroid * h->bins[h->gap].count +
		 h->bins[h->gap + 1].centroid * h->bins[h->gap + 1].count) /
		(h->bins[h->gap].count + h->bins[h->gap + 1].count);
	h->bins[h->gap + 1].count += h->bins[h->gap].count;
}