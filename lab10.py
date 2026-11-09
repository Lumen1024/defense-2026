import random
from typing import NamedTuple

from gen import (
    generate_primitive_root,
    generate_safe_prime,
)
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

ALGORITHM = "GOST R 34.10-94"
SOURCE = "files/some.txt"


class GostKeys(NamedTuple):
    p: int
    q: int
    a: int
    x: int
    y: int


def generate_keys() -> GostKeys:
    """Генерирует параметры и пару ключей ГОСТ Р 34.10-94."""
    p, q = generate_safe_prime()

    # Для безопасного простого p первообразный корень g имеет порядок 2q,
    # поэтому a = g^2 имеет порядок q.
    g = generate_primitive_root(p)
    a = fast_pow_mod(g, 2, p)

    x = random.randint(1, q - 1)
    y = fast_pow_mod(a, x, p)

    keys = GostKeys(p, q, a, x, y)
    print("Сгенерированы ключи ГОСТ Р 34.10-94:")
    print(f"> p = {p}\n> q = {q} (q | p-1)")
    print(f"> g = {g}, a = g^2 mod p = {a} (порядок q)")
    print(f"> x = {x} (секретный)\n> y = a^x mod p = {y} (открытый)")
    return keys


def _hash_byte(message: int, q: int) -> int:
    """Приводит байт хеша по модулю q; нулевое значение заменяется на 1."""
    value = message % q
    return value or 1


def sign_byte(message: int, keys: GostKeys) -> tuple[int, int]:
    """Подписывает один байт хеша, возвращает пару (r, s)."""
    h = _hash_byte(message, keys.q)
    while True:
        k = random.randint(1, keys.q - 1)
        r = fast_pow_mod(keys.a, k, keys.p) % keys.q
        s = (keys.x * r + k * h) % keys.q
        if r != 0 and s != 0:
            return r, s


def verify_byte(
    message: int, r: int, s: int, p: int, q: int, a: int, y: int
) -> bool:
    """Проверяет подпись одного байта хеша."""
    if not 0 < r < q or not 0 < s < q:
        return False

    h = _hash_byte(message, q)
    v = inverse(h, q)
    if v is None:
        return False

    z1 = s * v % q
    z2 = (q - r) * v % q
    result = (
        fast_pow_mod(a, z1, p) * fast_pow_mod(y, z2, p) % p
    ) % q
    return result == r


def _public_key(keys: GostKeys | None, public: dict) -> tuple[int, ...] | None:
    """Берёт открытый ключ из сеанса или из файла подписи."""
    if keys is not None:
        return keys.p, keys.q, keys.a, keys.y

    p, q, a, y = (public.get(name) for name in ("p", "q", "a", "y"))
    if (
        not all(isinstance(v, int) for v in (p, q, a, y))
        or p <= 2
        or q <= 1
        or not 0 < a < p
        or not 0 < y < p
    ):
        print("Ошибка: в файле подписи некорректный открытый ключ.")
        return None
    print("Открытый ключ взят из файла подписи.")
    return p, q, a, y


def sign_file(keys: GostKeys) -> None:
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
            {"p": keys.p, "q": keys.q, "a": keys.a, "y": keys.y},
            signature,
        )
    except OSError as exc:
        print(f"Ошибка: не удалось записать {dst}: {exc}")
        return

    print(f"Подписан файл: {src}")
    print(f"Подпись сохранена: {dst}")
    print(f"{HASH_TITLE}: {len(digest)} байт, каждый подписан парой (r, s).")


def verify_file(keys: GostKeys | None) -> None:
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
    p, q, a, y = key

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
        if not verify_byte(byte, r, s, p, q, a, y):
            print("Подпись недействительна: файл изменён или ключ не совпадает.")
            return

    print("Подпись действительна.")


def menu() -> int:
    print("1. Сгенерировать ключи ГОСТ Р 34.10-94")
    print("2. Подписать файл")
    print("3. Проверить подпись")
    print("0. Выход")
    return read_int("> ")


def main() -> None:
    keys: GostKeys | None = None
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
