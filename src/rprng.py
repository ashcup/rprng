#!/usr/bin/env python3

# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this
# file, You can obtain one at https://mozilla.org/MPL/2.0/.

# RPRNG (Reversible Pseudo-Random Number Generator)

from functools import reduce
from random import randint


def random():
    return randint(0, 0xFFFFFFFF)


def gcdint(a, b):
    if a is None:
        a = 0
    if b is None:
        b = 0
    if (a == 0):
        return b
    return gcdint(b % a, a)


def gcdvec(vector: list[int]):
    result: int = vector[0]
    i: int = 1
    while (i < len(vector)):
        result = gcdint(vector[i], result)
        # If result becomes 1 at any iteration, then it remains 1.
        # Therefore, there's no need to check further.
        if (result == 1):
            return 1
        i += 1
    return result


def modinv(a, m):
    return pow(a, -1, m)


def crack_unknown_increment(states, modulus, multiplier):
    increment = (states[1] - states[0]*multiplier) % modulus
    return modulus, multiplier, increment


def crack_unknown_multiplier(states, modulus):
    multiplier = (states[2] - states[1]) * modinv(states[1] - states[0], modulus) % modulus
    return crack_unknown_increment(states, modulus, multiplier)


def crack_unknown_modulus(states):
    diffs = [s1 - s0 for s0, s1 in zip(states, states[1:])]
    zeroes = [t2*t0 - t1*t1 for t0, t1, t2 in zip(diffs, diffs[1:], diffs[2:])]
    modulus = abs(reduce(gcdint, zeroes))
    return crack_unknown_multiplier(states, modulus)


# Affine/Linear Congruential Generator (Affine/Linear Congruential Pseudo-Random Number Generator)
class CongruentialGenerator:
    state = 0   # the "seed"
    n = 0       # the "modulus"
    m = 0       # the "multiplier"
    c = 0       # the "increment"

    def __init__(self, seed, n, m, c):
        self.state = seed
        self.n = n
        self.m = m
        self.c = c

    def next(self):
        self.state = self.peek()
        return self.state

    def peek(self):
        return (self.state * self.m + self.c) % self.n


class RPRNG:
    def __init__(self, seed: int, cg: CongruentialGenerator = None):
        self.seed = seed
        if cg is None:
            cg = CongruentialGenerator(seed, max(2, 2 + seed), 252705073, 234972692)
        self.cg = cg
        self.has_started = False

    def next(self):
        return self.cg.next()

    def nextvec(self, count):
        samples = []
        remaining = count
        while remaining > 0:
            sample = self.next()
            samples.append(sample)
            remaining -= 1
        return samples

    @staticmethod
    def reverse(samples):
        try:
            n, m, c = crack_unknown_modulus(samples)
            seed = n - 2
            cg = CongruentialGenerator(seed, n, m, c)
            return RPRNG(seed, cg)
        except:
            return None


def test():
    seed = random()
    rprng = RPRNG(seed)
    print(rprng.seed)
    samples = rprng.nextvec(16)
    rprng = RPRNG.reverse(samples)
    if rprng is not None:
        print(rprng.seed)
    else:
        print("ERROR: Invalid seed.")


test()
