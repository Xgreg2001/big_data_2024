import random
import math
import hashlib
import matplotlib.pyplot as plt


class LogLog:
    def __init__(self, num_buckets=128):
        self.num_buckets = num_buckets
        self.buckets = [0] * num_buckets
        self.alpha = 0.39701
        self.bucket_bits = int(math.log2(num_buckets))

    def _hash(self, value):
        h = hashlib.sha1(str(value).encode('utf-8')).digest()
        return int.from_bytes(h[:8], 'big')

    def add(self, value):
        h = self._hash(value)
        bucket_index = h >> (64 - self.bucket_bits)
        w = (h << self.bucket_bits) & ((1 << 64) - 1)
        rho = 1
        while (w & (1 << (64 - 1))) == 0 and rho <= 64:
            w <<= 1
            rho += 1
        self.buckets[bucket_index] = max(self.buckets[bucket_index], rho)

    def estimate(self):
        avg = sum(self.buckets) / self.num_buckets
        return self.alpha * self.num_buckets * (2 ** avg)


class HyperLogLog:
    def __init__(self, num_buckets=128):
        self.m = num_buckets
        self.buckets = [0] * self.m
        self.p = int(math.log2(self.m))
        self.alpha = self._get_alpha(self.m)

    def _get_alpha(self, m):
        if m == 16:
            return 0.673
        elif m == 32:
            return 0.697
        elif m == 64:
            return 0.709
        else:
            return 0.7213 / (1 + 1.079/m)

    def _hash(self, value):
        h = hashlib.sha1(str(value).encode('utf-8')).digest()
        return int.from_bytes(h[:8], 'big')

    def add(self, value):
        h = self._hash(value)
        bucket_index = h >> (64 - self.p)
        w = (h << self.p) & ((1 << 64) - 1)
        rho = 1
        while (w & (1 << (64 - 1))) == 0 and rho <= 64:
            w <<= 1
            rho += 1
        self.buckets[bucket_index] = max(self.buckets[bucket_index], rho)

    def estimate(self):
        indicator_sum = 0
        for val in self.buckets:
            indicator_sum += 2.0 ** (-val)
        raw_estimate = self.alpha * (self.m ** 2) / indicator_sum
        if raw_estimate <= (5.0 * self.m / 2.0):
            v = self.buckets.count(0)
            if v != 0:
                raw_estimate = self.m * math.log(self.m / v)
        if raw_estimate > (1 << 32) / 30.0:
            raw_estimate = - \
                ((1 << 32) * math.log(1 - (raw_estimate / (1 << 32))))
        return raw_estimate


def single_run_errors(n, k):
    elements = random.sample(range(n * 100), n)
    ll = LogLog(num_buckets=k)
    hll = HyperLogLog(num_buckets=k)
    for e in elements:
        ll.add(e)
        hll.add(e)
    return abs(ll.estimate() - n) / n, abs(hll.estimate() - n) / n


def average_run_errors(n, k, runs=5):
    s_ll = 0
    s_hll = 0
    for _ in range(runs):
        e_ll, e_hll = single_run_errors(n, k)
        s_ll += e_ll
        s_hll += e_hll
    return s_ll / runs, s_hll / runs


def main():
    bucket_sizes = [16, 32, 64, 128, 256, 512, 1024, 2048]
    runs = 50
    for k in bucket_sizes:
        center = int(k * math.log(k))
        n_vals = [
            100, 500, 1000, 2000, 3000, 4000, 5000, 10000, 20000, 30000, 40000,
            50000, 100000, max(1, center // 2), center, center * 2,
            int(center * 1.5), max(1, int(center * 0.75)),
        ]
        n_vals = sorted(set(n_vals))
        ll_errs = []
        hll_errs = []
        for n in n_vals:
            e_ll, e_hll = average_run_errors(n, k, runs=runs)
            ll_errs.append(e_ll)
            hll_errs.append(e_hll)
        plt.figure()
        plt.plot(n_vals, ll_errs, marker='o', label='LogLog')
        plt.plot(n_vals, hll_errs, marker='s', label='HyperLogLog')
        plt.axvline(k * math.log(k), color='r',
                    linestyle='--', label='k ln(k)')
        plt.xscale('log')
        plt.yscale('log')
        plt.title(f'k={k}')
        plt.xlabel('n')
        plt.ylabel('Relative Error')
        plt.legend()
        plt.grid(True, which='both', linestyle='--', alpha=0.7)
        plt.savefig(f'plot_k_{k}.pdf')
        plt.close()


if __name__ == '__main__':
    main()
