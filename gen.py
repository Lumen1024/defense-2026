import random

from lib import fast_pow_mod, is_prime_fermat

MAGNITUDE = 10 ** 9


def generate_pair(low: int = 2, high: int = MAGNITUDE) -> tuple[int, int]:
    return random.randint(low, high), random.randint(low, high)


def generate_prime(low: int = 2, high: int = MAGNITUDE, rounds: int = 20) -> int:
    while True:
        n = random.randint(low, high)
        if is_prime_fermat(n, rounds):
            return n


def generate_prime_pair(low: int = 2, high: int = MAGNITUDE, rounds: int = 20) -> tuple[int, int]:
    return generate_prime(low, high, rounds), generate_prime(low, high, rounds)


def generate_discrete_log_challenge(rounds: int = 20) -> tuple[int, int, int, int]:
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
    g = random.randint(2, p - 1)
    x_a = random.randint(2, p - 2)
    x_b = random.randint(2, p - 2)
    key = fast_pow_mod(g, x_a * x_b, p)
    return p, g, x_a, x_b, key
