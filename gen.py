"""Генераторы чисел и параметров для лабораторных работ."""

import random

from lib import fast_pow_mod, is_prime_fermat, primitive_root

MAGNITUDE = 10 ** 9
MIN_SAFE_Q = 10 ** 6


def generate_pair(low: int = 2, high: int = MAGNITUDE) -> tuple[int, int]:
    return random.randint(low, high), random.randint(low, high)


def generate_prime(
    low: int = 2, high: int = MAGNITUDE, rounds: int = 20
) -> int:
    """Генерирует вероятно простое число в диапазоне [low, high]."""
    while True:
        n = random.randint(low, high)
        if is_prime_fermat(n, rounds):
            return n


def generate_prime_pair(
    low: int = 2, high: int = MAGNITUDE, rounds: int = 20
) -> tuple[int, int]:
    return generate_prime(low, high, rounds), generate_prime(low, high, rounds)


def generate_primitive_root(p: int) -> int:
    """Первообразный корень по модулю простого p (иначе — случайное g)."""
    g = primitive_root(p)
    if g is None:
        return random.randint(2, p - 1)
    return g


def generate_safe_prime(
    low: int = MIN_SAFE_Q, high: int = MAGNITUDE // 2, rounds: int = 20
) -> tuple[int, int]:
    """Генерирует p = 2q + 1, где q — простое (безопасное простое p)."""
    while True:
        q = generate_prime(low, high, rounds)
        p = 2 * q + 1
        if is_prime_fermat(p, rounds):
            return p, q


def generate_discrete_log_challenge(
    rounds: int = 20,
) -> tuple[int, int, int, int]:
    """Генерирует (a, y, p, x), где y = a^x mod p, а x — «секретный» ответ."""
    p = generate_prime(rounds=rounds)
    a = random.randint(2, p - 1)
    x = random.randint(1, p - 1)
    y = fast_pow_mod(a, x, p)
    return a, y, p, x


def generate_diffie_hellman_challenge(
    rounds: int = 20,
) -> tuple[int, int, int, int, int]:
    """Генерирует (p, g, x_a, x_b, key) для схемы Диффи-Хеллмана."""
    # p >= 5, иначе диапазон [2, p - 2] для секретных ключей пуст
    p = generate_prime(low=5, rounds=rounds)
    g = generate_primitive_root(p)
    x_a = random.randint(2, p - 2)
    x_b = random.randint(2, p - 2)
    key = fast_pow_mod(g, x_a * x_b, p)
    return p, g, x_a, x_b, key
