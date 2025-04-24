#!/usr/bin/env python3


# PRCA (Pseudo-Random Compression Algorithm)

from functools import reduce


# Affine/Linear Congruential Generator (Affine/Linear Congruential Pseudo-Random Number Generator)
class CongruentialGenerator:
    m = 672257317069504227  # the "multiplier"
    c = 7382843889490547368  # the "increment"
    n = 9223372036854775783  # the "modulus"

    def __init__(self, seed):
        self.state = seed  # the "seed"

    def next(self):
        self.state = (self.state * self.m + self.c) % self.n
        return self.state


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


def egcd(a, b):
    if a == 0:
        return (b, 0, 1)
    else:
        g, y, x = egcd(b % a, a)
        return (g, x - (b // a) * y, y)


# def modinv(a, m):
#     g, x, y = egcd(a, m)
#     if g != 1:
#         raise Exception('modular inverse does not exist')
#     else:
#         return x % m


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


def test():
    seed = 42
    prng = CongruentialGenerator(seed)
    data = [
        prng.next(),
        prng.next(),
        prng.next(),
        prng.next(),
        prng.next(),
        prng.next(),
        prng.next(),
        prng.next()
    ]
    print(data)
    n, m, c = crack_unknown_modulus(data)
    print("n=" + str(n))
    print("m=" + str(m))
    print("c=" + str(c))


test()
