# HyperLogLog

This repository contains a simple Python implementation of the **HyperLogLog** algorithm, a **probabilistic data structure** used for estimating the cardinality (the number of distinct elements) of a set. HyperLogLog achieves this with a small memory footprint, making it an efficient tool for large-scale data analysis.

---

### What is HyperLogLog?
HyperLogLog is a probabilistic data structure used for **cardinality estimation** with fixed memory usage. Instead of storing all elements, it hashes input data and tracks the distribution of hash values. This allows it to estimate the number of unique items in a dataset efficiently.

Key properties of HyperLogLog:
- **Memory efficiency:** Memory usage depends only on the number of buckets, not the size of the dataset.
- **Probabilistic estimation:** Provides approximate cardinality with a small error margin.

You can try the HyperLogLog at `example.py`. For example,
```py
# example.py
import os
from hyperloglog import HyperLogLog
from tqdm import tqdm

# Generate sample data for 1,000,000 times and add them to the HyperLogLog structure, then analyze it

hll = HyperLogLog(number_of_buckets = 512)
number_of_data = 1_000_000
for i in tqdm(range(number_of_data)):
    data = os.urandom(32).hex()
    hll.add(data)

hll.analyze()
```
The result would be like
```
Number of Buckets:      512
Alpha_m Constant:       0.7197831133217303
Estimated Cardinality:  1017576
Actual Cardinality:     1000000
Error (%):              1.7576
```

### Theoretical ground
Check out [Wikipedia page](https://en.wikipedia.org/wiki/HyperLogLog) and [research paper](https://algo.inria.fr/flajolet/Publications/FlFuGaMe07.pdf).
