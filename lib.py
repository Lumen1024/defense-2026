import hashlib
import json
import random
from math import gcd, isqrt
from typing import Any

DEFAULT_HASH = "sha256"
HASH_TITLE = "SHA-256"


def fast_pow_mod(a: int, x: int, p: int) -> int:
    """Быстрое возведение в степень по модулю: a^x mod p."""
    if p <= 0:
        raise ValueError("p должно быть положительным")

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


def inverse(a: int, m: int) -> int | None:
    """Обратный элемент a^(-1) mod m или None, если его не существует."""
    if m <= 0:
        raise ValueError("m должно быть положительным")
    g, x, _ = extended_euclid(a % m, m)
    return x % m if g == 1 else None


def discrete_log(a: int, y: int, p: int) -> int | None:
    """Нахождение дискретного логарифма a^x % p = y."""
    if p <= 1:
        raise ValueError("p должно быть больше 1")

    a %= p
    y %= p

    # a^0 ≡ 1
    if y == 1:
        return 0

    # Алгоритм корректен только для обратимого a (иначе нет структуры группы)
    if gcd(a, p) != 1:
        raise ValueError(f"a и p должны быть взаимно просты (НОД = {gcd(a, p)})")

    m = isqrt(p) + 1
    k = (p + m - 1) // m

    # Шаг младенца: (y * a^j) % p
    baby_steps: dict[int, int] = {}
    value = y  # j = 0: y * a^0
    for j in range(m):
        if value not in baby_steps:
            baby_steps[value] = j
        value = (value * a) % p

    # Шаг великана: a^(i*m) % p
    power = fast_pow_mod(a, m, p)  # a^m
    value = power  # i = 1
    for i in range(1, k + 1):
        if value in baby_steps:
            x = i * m - baby_steps[value]
            if fast_pow_mod(a, x, p) == y:  # страховка от ложного совпадения
                return x
        value = (value * power) % p  # a^((i+1)*m)

    return None


def primitive_root(p: int) -> int | None:
    """Наименьший первообразный корень по модулю p."""
    if p < 2:
        raise ValueError("p должно быть >= 2")
    if p == 2:
        return 1

    factors: set[int] = set()
    n = p - 1
    d = 2
    while d * d <= n:
        if n % d == 0:
            factors.add(d)
            while n % d == 0:
                n //= d
        d += 1
    if n > 1:
        factors.add(n)

    for g in range(2, p):
        if all(fast_pow_mod(g, (p - 1) // f, p) != 1 for f in factors):
            return g
    return None


def diffie_hellman_get_public_key(p: int, g: int, x: int) -> int:
    """Публичный ключ абонента по его секретному ключу: g^x mod p."""
    return fast_pow_mod(g, x, p)


def diffie_hellman_get_shared_secret(p: int, x: int, y_other: int) -> int:
    """Общий секрет по своему секретному и чужому открытому ключу."""
    return fast_pow_mod(y_other, x, p)


def diffie_hellman(p: int, g: int, x_a: int, x_b: int) -> tuple[int, int, int]:
    """Построение общего ключа по схеме Диффи-Хеллмана.

    p, g - публичные параметры шифрования
    x_a, x_b - секретные ключи абонентов
    y_a, y_b - публичные ключи абонентов
    k_a = k_b - общий секретный ключ шифрования
    """

    if p <= 2:
        raise ValueError("p должно быть больше 2")
    if not 1 < g < p:
        raise ValueError("g должно удовлетворять 1 < g < p")
    if x_a < 1 or x_b < 1:
        raise ValueError("секретные ключи должны быть >= 1")

    y_a = fast_pow_mod(g, x_a, p)
    y_b = fast_pow_mod(g, x_b, p)

    key_a = fast_pow_mod(y_b, x_a, p)
    key_b = fast_pow_mod(y_a, x_b, p)

    if key_a != key_b:  # не должно достигаться при корректных параметрах
        raise ArithmeticError("общие ключи абонентов не совпали")
    return y_a, y_b, key_a


# --- Хеширование и файлы электронных подписей ---


def hash_file(path: str, algorithm: str = DEFAULT_HASH) -> bytes:
    """Вычисляет хеш файла, читая его по частям (файл может быть большим)."""
    digest = hashlib.new(algorithm)
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.digest()


def default_signature_path(src: str) -> str:
    """Путь к отдельному файлу подписи: <исходный файл>.sig."""
    return src + ".sig"


def write_signature(path: str, payload: dict[str, Any]) -> None:
    """Сохраняет подпись в отдельный JSON-файл."""
    with open(path, "w", encoding="utf-8") as f:
        json.dump(payload, f, ensure_ascii=False, indent=2)
        f.write("\n")


def read_signature(path: str) -> dict[str, Any]:
    """Загружает JSON-файл подписи."""
    with open(path, encoding="utf-8") as f:
        payload = json.load(f)
    if not isinstance(payload, dict):
        raise ValueError("файл подписи должен содержать JSON-объект")
    return payload


def get_public_key(payload: dict[str, Any], algorithm: str) -> dict[str, Any]:
    """Проверяет заголовок подписи и возвращает открытый ключ."""
    if payload.get("algorithm") != algorithm:
        raise ValueError(f"ожидалась подпись {algorithm}")
    if payload.get("hash") != DEFAULT_HASH:
        raise ValueError(f"ожидалась хеш-функция {HASH_TITLE}")
    public_key = payload.get("public_key")
    if not isinstance(public_key, dict):
        raise ValueError("в файле подписи отсутствует открытый ключ")
    return public_key


def get_signature(payload: dict[str, Any]) -> list[Any]:
    """Возвращает список значений подписи из файла."""
    signature = payload.get("signature")
    if not isinstance(signature, list):
        raise ValueError("в файле подписи отсутствует список значений")
    return signature

