import random
from math import gcd
from typing import NamedTuple

from gen import MAGNITUDE, generate_prime
from lib import (
    DEFAULT_HASH,
    HASH_TITLE,
    default_signature_path,
    fast_pow_mod,
    get_public_key,
    get_signature,
    hash_file,
    inverse,
    read_signature,
    write_signature,
)
from ui import read_int, read_path

ALGORITHM = "RSA"
SOURCE = "some.txt"


class RsaKeys(NamedTuple):
    p: int
    q: int
    n: int
    e: int
    d: int


def generate_keys() -> RsaKeys:
    """Генерирует пару ключей RSA (n, e) — открытый, d — секретный."""
    while True:
        p = generate_prime(low=257, high=MAGNITUDE)
        q = generate_prime(low=257, high=MAGNITUDE)
        if p == q:
            continue

        n = p * q
        phi = (p - 1) * (q - 1)

        e = 65537
        if gcd(e, phi) != 1:
            while True:
                e = random.randrange(3, phi, 2)
                if gcd(e, phi) == 1:
                    break

        d = inverse(e, phi)
        if d is None:
            continue

        keys = RsaKeys(p, q, n, e, d)
        print("Сгенерированы ключи RSA:")
        print(f"> p = {p}\n> q = {q}\n> n = p*q = {n}")
        print(f"> phi(n) = (p-1)*(q-1) = {phi}")
        print(f"> e = {e} (открытый)\n> d = {d} (секретный)")
        return keys


def _public_key(keys: RsaKeys | None, public: dict) -> tuple[int, int] | None:
    """Берёт открытый ключ из сеанса или из файла подписи."""
    if keys is not None:
        return keys.n, keys.e
    n, e = public.get("n"), public.get("e")
    if (
        not isinstance(n, int)
        or not isinstance(e, int)
        or n <= 255
        or e <= 1
    ):
        print("Ошибка: в файле подписи некорректный открытый ключ.")
        return None
    print("Открытый ключ взят из файла подписи.")
    return n, e


def sign_file(keys: RsaKeys) -> None:
    src = read_path("Файл для подписи", SOURCE)
    try:
        digest = hash_file(src)
    except OSError as exc:
        print(f"Ошибка: не удалось прочитать {src}: {exc}")
        return

    signature = [fast_pow_mod(byte, keys.d, keys.n) for byte in digest]
    dst = read_path("Файл подписи", default_signature_path(src))
    payload = {
        "version": 1,
        "algorithm": ALGORITHM,
        "hash": DEFAULT_HASH,
        "public_key": {"n": keys.n, "e": keys.e},
        "signature": signature,
    }
    try:
        write_signature(dst, payload)
    except OSError as exc:
        print(f"Ошибка: не удалось записать {dst}: {exc}")
        return

    print(f"Подписан файл: {src}")
    print(f"Подпись сохранена: {dst}")
    print(f"{HASH_TITLE}: {len(digest)} байт, каждый подписан отдельно.")


def verify_file(keys: RsaKeys | None) -> None:
    src = read_path("Проверяемый файл", SOURCE)
    sig_path = read_path("Файл подписи", default_signature_path(src))

    try:
        payload = read_signature(sig_path)
        public = get_public_key(payload, ALGORITHM)
        signature = get_signature(payload)
    except (OSError, ValueError) as exc:
        print(f"Ошибка: не удалось прочитать подпись {sig_path}: {exc}")
        return

    key = _public_key(keys, public)
    if key is None:
        return
    n, e = key

    try:
        digest = hash_file(src)
    except OSError as exc:
        print(f"Ошибка: не удалось прочитать {src}: {exc}")
        return

    if len(signature) != len(digest):
        print("Подпись недействительна: размер подписи не совпадает с хешем.")
        return

    for index, (byte, value) in enumerate(zip(digest, signature), start=1):
        if not isinstance(value, int) or not 0 <= value < n:
            print(f"Подпись недействительна: некорректное значение №{index}.")
            return
        if byte >= n or fast_pow_mod(value, e, n) != byte:
            print("Подпись недействительна: файл изменён или ключ не совпадает.")
            return

    print("Подпись действительна.")


def menu() -> int:
    print("1. Сгенерировать ключи RSA")
    print("2. Подписать файл")
    print("3. Проверить подпись")
    print("0. Выход")
    return read_int("> ")


def main() -> None:
    keys: RsaKeys | None = None
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
