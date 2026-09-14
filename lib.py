import random
from math import isqrt


def fast_pow_mod(a: int, x: int, p: int) -> int:
    """Быстрое возведение в степень по модулю: a^x mod p."""
    if p <= 0:
        raise ValueError("p must be positive")

    result = 1
    a %= p
    exp = x

    while exp > 0:
        if exp & 1:
            result = (result * a) % p
        a = (a * a) % p
        exp >>= 1
    return result


def is_prime_fermat(n: int, rounds: int = 20) -> bool:
    """Вероятностный тест простоты Ферма."""
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False

    for _ in range(rounds):
        a = random.randint(2, n - 2)
        if fast_pow_mod(a, n - 1, n) != 1:
            return False
    return True


def extended_euclid(a: int, b: int) -> tuple[int, int, int]:
    """Обобщённый алгоритм Евклида. a*x + b*y = НОД(a, b)."""
    old_r, r = a, b
    old_s, s = 1, 0
    old_t, t = 0, 1
    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t
    return old_r, old_s, old_t




def discrete_log(a: int, y: int, p: int) -> int | None:
    """Нахождение дискретного логарифма a^x % p = y."""
    if p <= 1:
        print("p must be > 1")
        return None
    a %= p
    y %= p

    # a^0 ≡ 1
    if y == 1:
        return 0

    m = isqrt(p) + 1
    k = (p + m - 1) // m

    # Шаг младенца: (y * a^j) % p
    baby_steps = {}
    value = y  # j = 0: y * a^0
    for j in range(m):
        if value not in baby_steps:
            baby_steps[value] = j
        value = (value * a) % p

    # Шаг великана: a^(i*m) % p
    power = fast_pow_mod(a, m, p)  # a^m
    value = power                   # i = 1
    for i in range(1, k + 1):
        if value in baby_steps:
            return i * m - baby_steps[value]
        value = (value * power) % p  # a^((i+1)*m)

    return None


