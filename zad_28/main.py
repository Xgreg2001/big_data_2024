import random
import math
import numpy as np
import matplotlib.pyplot as plt


class HyperLogLog:
    def __init__(self, registers=1024):
        if not (registers & (registers - 1) == 0):
            raise ValueError("Number of registers must be a power of 2")

        self.registers = registers
        self.register_bits = int(math.log2(registers))
        self.registers_array = [0] * registers

    def _hash(self, item):
        return hash(str(item))

    def _get_leading_zeros(self, hash_value):
        hash_value = abs(hash_value) & 0xFFFFFFFF
        if hash_value == 0:
            return 32

        return (hash_value).bit_length() - (hash_value).bit_length()

    def add(self, item):
        hash_value = self._hash(item)
        register_index = hash_value & ((1 << self.register_bits) - 1)
        leading_zeros = self._get_leading_zeros(hash_value >> self.register_bits) + 1
        self.registers_array[register_index] = max(
            self.registers_array[register_index], leading_zeros
        )

    def estimate(self):
        if self.registers == 16:
            alpha = 0.673
        elif self.registers == 32:
            alpha = 0.697
        elif self.registers == 64:
            alpha = 0.709
        else:
            alpha = 0.7213 / (1 + 1.079 / self.registers)

        raw_estimate = (
            alpha
            * (self.registers**2)
            / sum(2 ** (-reg_value) for reg_value in self.registers_array)
        )

        if raw_estimate <= 2.5 * self.registers:
            empty_registers = self.registers_array.count(0)
            if empty_registers > 0:
                return self.registers * math.log(self.registers / empty_registers)

        return raw_estimate


class LogLog:
    def __init__(self, registers=1024):
        self.registers = registers
        self.register_bits = int(math.log2(registers))
        self.registers_array = [0] * registers

    def _hash(self, item):
        return hash(str(item))

    def _get_leading_zeros(self, hash_value):
        hash_value = abs(hash_value) & 0xFFFFFFFF
        if hash_value == 0:
            return 32

        return (hash_value).bit_length() - (hash_value).bit_length()

    def add(self, item):
        hash_value = self._hash(item)
        register_index = hash_value % self.registers
        leading_zeros = self._get_leading_zeros(hash_value) + 1
        self.registers_array[register_index] = max(
            self.registers_array[register_index], leading_zeros
        )

    def estimate(self):
        mean_leading_zeros = np.mean(self.registers_array)
        return 2**mean_leading_zeros * self.registers / 0.77351


def single_run_errors(n, k):
    elements = random.sample(range(n * 100), n)
    ll = LogLog(registers=k)
    hll = HyperLogLog(registers=k)
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
            int(max(1, center * 0.1)),
            int(max(1, center * 0.15)),
            int(max(1, center * 0.25)),
            int(max(1, center * 0.45)),
            int(max(1, center * 0.5)),
            int(max(1, center * 0.75)),
            center,
            int(center * 1.25),
            int(center * 1.5),
            int(center * 1.75),
            center * 2,
        ]
        n_vals = sorted(set(n_vals))
        ll_errs = []
        hll_errs = []
        for n in n_vals:
            e_ll, e_hll = average_run_errors(n, k, runs=runs)
            ll_errs.append(e_ll)
            hll_errs.append(e_hll)
        plt.figure(figsize=(16, 9))
        plt.plot(n_vals, ll_errs, marker="o", label="LogLog")
        plt.plot(n_vals, hll_errs, marker="s", label="HyperLogLog")
        plt.axvline(center, color="r", linestyle="--", label="k ln(k)")
        plt.title(f"k={k}")
        plt.xlabel("n")
        plt.ylabel("Relative Error")
        plt.legend()
        plt.grid(True, which="both", linestyle="--", alpha=0.7)
        plt.savefig(f"plot_k_{k}.pdf")
        plt.close()


if __name__ == "__main__":
    main()
