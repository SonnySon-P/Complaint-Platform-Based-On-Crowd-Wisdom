from typing import List, Tuple
from cryptography.hazmat.primitives.serialization import (Encoding, PrivateFormat, NoEncryption)
import random

def _miller_rabin(n: int, k: int = 16) -> bool:
    if n < 2:
        return False
    small_primes = [2, 3, 5, 7, 11, 13, 17, 19, 23]
    for p in small_primes:
        if n == p:
            return True
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = random.randrange(2, n - 2)
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for __ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

def next_prime(n: int) -> int:
    p = n + 1 if n % 2 == 0 else n + 2
    while True:
        if _miller_rabin(p):
            return p
        p += 2

def mod_inverse(a: int, m: int) -> int:
    a %= m
    if a == 0:
        raise ValueError("0 mod m不存在反元素")
    m0, x0, x1 = m, 0, 1
    while a > 1:
        q = a // m
        m, a = a % m, m
        x0, x1 = x1 - q * x0, x0
    if x1 < 0:
        x1 += m0
    return x1

def split_secret(secret_int: int, threshold: int, total_shares: int, prime: int) -> List[Tuple[int, int]]:
    if threshold < 2:
        raise ValueError("threshold必須 >= 2")
    if total_shares < threshold:
        raise ValueError("total_shares必須 >= threshold")
    if not (secret_int < prime):
        raise ValueError("prime必須大於秘密(d)")

    coefficients = [secret_int] + [random.randrange(1, prime) for _ in range(threshold - 1)]
    shares = []
    for i in range(1, total_shares + 1):
        y = 0
        for coeff in reversed(coefficients):
            y = (y * i + coeff) % prime
        shares.append((i, y))
    return shares

def reconstruct_secret(shares: List[Tuple[int, int]], threshold: int, prime: int) -> int:
    if len(shares) < threshold:
        raise ValueError("提供的份額不足以重建秘密")
    total = 0
    for i, (xi, yi) in enumerate(shares):
        num = 1
        den = 1
        for j, (xj, _) in enumerate(shares):
            if i == j:
                continue
            num = (num * (-xj)) % prime
            den = (den * (xi - xj)) % prime
        li = (num * mod_inverse(den, prime)) % prime
        total = (total + yi * li) % prime
    return total
