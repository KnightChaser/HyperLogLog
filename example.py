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