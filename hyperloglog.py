import math
import hashlib
from typing import List


class HyperLogLog:
    """
    A class to represent a HyperLogLog data structure for estimating 
    the cardinality of a set.
    """
    def __init__(self, number_of_buckets: int) -> None:
        """
        Initializes the HyperLogLog data structure with a given number of buckets.
        """
        assert number_of_buckets > 0, "Number of buckets should be greater than 0."
        assert number_of_buckets & (number_of_buckets - 1) == 0, "Number of buckets must be a power of 2."
        self.number_of_buckets: int = number_of_buckets
        self.buckets: List[int] = [0] * number_of_buckets  # Store the max run-of-zero count
        self.alpha_m: float = self._compute_alpha_m(number_of_buckets)

    @staticmethod
    def _compute_alpha_m(number_of_buckets: int) -> float:
        """
        Computes the alpha_m constant for the given number of buckets.

        Standard HyperLogLog constants for small m (16, 32, 64):
            m=16 -> alpha_m=0.673
            m=32 -> alpha_m=0.697
            m=64 -> alpha_m=0.709

        For m >= 128:
            alpha_m = 0.7213 / (1 + 1.079/m)
        """
        # Give a warning if the number of buckets isn't 16, 32, 64, or >= 128 which is 2**k
        if not math.log2(number_of_buckets).is_integer() and number_of_buckets < 128:
            print("Warning: Using a non-standard number of buckets. "
                  "Consider using 16, 32, 64, or a power of 2 >= 128 for better accuracy.")
            
        if number_of_buckets == 16:
            return 0.673
        elif number_of_buckets == 32:
            return 0.697
        elif number_of_buckets == 64:
            return 0.709
        else:
            # Usually bigger values of m >= 64
            return 0.7213 / (1 + 1.079 / number_of_buckets)

    @staticmethod
    def _count_leading_zeroes(value: int) -> int:
        """
        Counts the number of leading (actually trailing) zeros in the
        binary representation of 'value', starting from 1 as per HLL spec.
        Since Python3 doesn't have a specific width for integers, calculating the # of leading 0s
        is a bit tricky. Thus, we use the trailing 0s instead, since the probability of having
        the same number of trailing 0s as leading 0s is the same.
        """
        count = 1
        while value > 0:
            if value & 1 == 1:
                break
            value >>= 1
            count += 1
        return count

    def add(self, item: str) -> None:
        """
        Adds an item (string) to the HyperLogLog data structure.
        """
        # Hash the item and convert to an integer
        sha256 = hashlib.sha256()
        sha256.update(item.encode("utf-8"))
        hash_value = int(sha256.hexdigest(), 16)

        # Extract the bucket index (lowest log2(m) bits)
        bucket_index = hash_value & (self.number_of_buckets - 1)

        # Shift out those bits to get the part used for the zero-count
        remaining_hash = hash_value >> int(math.log2(self.number_of_buckets))

        # Count the run of zeros
        leading_zeroes = self._count_leading_zeroes(remaining_hash)

        # Store the maximum run length seen for this bucket
        self.buckets[bucket_index] = max(self.buckets[bucket_index], leading_zeroes)

    def estimate(self) -> float:
        """
        Estimates the cardinality of the set using the HyperLogLog algorithm.
        """
        # Compute the raw HyperLogLog estimate
        harmonic_mean = sum(2 ** -register for register in self.buckets)
        raw_estimate = self.alpha_m * (self.number_of_buckets ** 2) / harmonic_mean

        # Small range correction: linear counting if estimate is small
        if raw_estimate <= 2.5 * self.number_of_buckets:
            zero_buckets = self.buckets.count(0)
            if zero_buckets > 0:
                raw_estimate = self.number_of_buckets * math.log(self.number_of_buckets / zero_buckets)

        # Large range correction
        if raw_estimate > (1 << 32) / 30.0:
            raw_estimate = -(1 << 32) * math.log(1.0 - raw_estimate / (1 << 32))

        return raw_estimate

    def merge(self, other: "HyperLogLog") -> None:
        """
        Merges another HyperLogLog structure into this one.
        They must have the same number of buckets.
        """
        assert self.number_of_buckets == other.number_of_buckets, \
            "Cannot merge HyperLogLogs with different numbers of buckets."

        self.buckets = [
            max(self.buckets[i], other.buckets[i])
            for i in range(self.number_of_buckets)
        ]

    def __len__(self) -> int:
        """
        Returns the integer-rounded estimate of cardinality when len() is called.
        """
        return int(self.estimate())


# Example usage
if __name__ == "__main__":
    hll = HyperLogLog(16)
    hll.add("hello")
    hll.add("world")
    hll.add("hello")  # Adding "hello" again should not increase the count
    print("Estimated Cardinality:", len(hll))
