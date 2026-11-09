import random
from math import gcd
from typing import NamedTuple

from gen import MAGNITUDE, generate_prime, generate_primitive_root
from lib import (
    HASH_TITLE,
    default_signature_path,
    fast_pow_mod,
    hash_file,
    inverse,
    load_signature,
    save_signature,
)
from ui import read_int, read_path

ALGORITHM = "ElGamal"
SOURCE = "files/some.txt"


class ElGamalKeys(NamedTuple):
    p: int
    g: int
    x: int
    y: int


def generate_keys() -> ElGamalKeys:
    """Генерирует параметры и пару ключей Эль-Гамаля."""
    p = generate_prime(low=257, high=MAGNITUDE)
    g = generate_primitive_root(p)
    x = random.randint(1, p - 2)
    y = fast_pow_mod(g, x, p)

    keys = ElGamalKeys(p, g, x, y)
    print("Сгенерированы ключи Эль-Гамаля:")
    print(f"> p = {p}\n> g = {g} (первообразный корень)")
    print(f"> x = {x} (секретный)\n> y = g^x mod p = {y} (открытый)")
    return keys


def sign_byte(message: int, keys: ElGamalKeys) -> tuple[int, int]:
    """Подписывает один байт хеша, возвращает пару (r, s)."""
    while True:
        k = random.randint(1, keys.p - 2)
        if gcd(k, keys.p - 1) != 1:
            continue
        k_inverse = inverse(k, keys.p - 1)
        if k_inverse is None:
            continue

        r = fast_pow_mod(keys.g, k, keys.p)
        s = ((message - keys.x * r) * k_inverse) % (keys.p - 1)
        if r != 0 and s != 0:
            return r, s


def verify_byte(
    message: int, r: int, s: int, p: int, g: int, y: int
) -> bool:
    """Проверяет подпись одного байта хеша."""
    if not 0 < r < p or not 0 <= s < p - 1:
        return False
    left = fast_pow_mod(y, r, p) * fast_pow_mod(r, s, p) % p
    right = fast_pow_mod(g, message, p)
    return left == right


def _public_key(
    keys: ElGamalKeys | None, public: dict
) -> tuple[int, int, int] | None:
    """Берёт открытый ключ из сеанса или из файла подписи."""
    if keys is not None:
        return keys.p, keys.g, keys.y

    p, g, y = public.get("p"), public.get("g"), public.get("y")
    if (
        not isinstance(p, int)
        or not isinstance(g, int)
        or not isinstance(y, int)
        or p <= 2
        or not 1 < g < p
        or not 0 < y < p
    ):
        print("Ошибка: в файле подписи некорректный открытый ключ.")
        return None
    print("Открытый ключ взят из файла подписи.")
    return p, g, y


def sign_file(keys: ElGamalKeys) -> None:
    src = read_path("Файл для подписи", SOURCE)
    try:
        digest = hash_file(src)
    except OSError as exc:
        print(f"Ошибка: не удалось прочитать {src}: {exc}")
        return

    signature = [sign_byte(byte, keys) for byte in digest]
    dst = read_path("Файл подписи", default_signature_path(src))
    try:
        save_signature(
            dst,
            ALGORITHM,
            {"p": keys.p, "g": keys.g, "y": keys.y},
            signature,
        )
    except OSError as exc:
        print(f"Ошибка: не удалось записать {dst}: {exc}")
        return

    print(f"Подписан файл: {src}")
    print(f"Подпись сохранена: {dst}")
    print(f"{HASH_TITLE}: {len(digest)} байт, каждый подписан парой (r, s).")


def verify_file(keys: ElGamalKeys | None) -> None:
    src = read_path("Проверяемый файл", SOURCE)
    sig_path = read_path("Файл подписи", default_signature_path(src))

    try:
        public, signature = load_signature(sig_path, ALGORITHM)
    except (OSError, ValueError) as exc:
        print(f"Ошибка: не удалось прочитать подпись {sig_path}: {exc}")
        return

    key = _public_key(keys, public)
    if key is None:
        return
    p, g, y = key

    try:
        digest = hash_file(src)
    except OSError as exc:
        print(f"Ошибка: не удалось прочитать {src}: {exc}")
        return

    if len(signature) != len(digest):
        print("Подпись недействительна: размер подписи не совпадает с хешем.")
        return

    for index, (byte, value) in enumerate(zip(digest, signature), start=1):
        if (
            not isinstance(value, list)
            or len(value) != 2
            or not all(isinstance(v, int) for v in value)
        ):
            print(f"Подпись недействительна: некорректная пара №{index}.")
            return
        r, s = value
        if not verify_byte(byte, r, s, p, g, y):
            print("Подпись недействительна: файл изменён или ключ не совпадает.")
            return

    print("Подпись действительна.")


def menu() -> int:
    print("1. Сгенерировать ключи Эль-Гамаля")
    print("2. Подписать файл")
    print("3. Проверить подпись")
    print("0. Выход")
    return read_int("> ")


def main() -> None:
    keys: ElGamalKeys | None = None
    while True:
        command = menu()
        match command:
            case 1:
                keys = generate_keys()
            case 2:
                if keys is None:
                    print("Ключи не заданы. Сначала выполните пункт 1.")
                    continue
                sign_file(keys)
            case 3:
                verify_file(keys)
            case _:
                break


if __name__ == "__main__":
    main()
