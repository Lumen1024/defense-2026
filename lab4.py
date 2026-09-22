import random
from math import gcd

from gen import MAGNITUDE, generate_prime
from lib import extended_euclid, fast_pow_mod, is_prime_fermat
from ui import read_int

MIN_P = 257
LOW = 10 ** 6

SOURCE = "files/some.txt"
ENCRYPTED = "files/some.enc"
DECRYPTED = "files/some_dec.txt"


def inverse(a: int, m: int) -> int | None:
    g, x, _ = extended_euclid(a % m, m)
    return x % m if g == 1 else None


def random_coprime(m: int) -> int:
    while True:
        c = random.randint(2, m - 1)
        if gcd(c, m) == 1:
            return c


def make_keys(p: int, c1: int, c2: int):
    if p < MIN_P or not is_prime_fermat(p):
        print(f"Ошибка: p должно быть простым и >= {MIN_P}.")
        return None
    if gcd(c1, p - 1) != 1 or gcd(c2, p - 1) != 1:
        print("Ошибка: C_A и C_B должны быть взаимно просты с p-1.")
        return None
    return p, c1, c2, inverse(c1, p - 1), inverse(c2, p - 1)


def get_keys() -> tuple[int, int, int, int, int] | None:
    p = read_int(
        "p = ",
        True,
        lambda: generate_prime(low=max(LOW, MIN_P), high=MAGNITUDE),
        validate=lambda v: v >= MIN_P and is_prime_fermat(v),
        error=f"p должно быть простым и >= {MIN_P}",
    )

    def valid_c(value: int) -> bool:
        return 2 <= value <= p - 2 and gcd(value, p - 1) == 1

    c1 = read_int(
        "C_A = ",
        True,
        lambda: random_coprime(p - 1),
        validate=valid_c,
        error=f"нужно 2 <= C_A <= {p - 2} и НОД(C_A, p-1) = 1",
    )
    c2 = read_int(
        "C_B = ",
        True,
        lambda: random_coprime(p - 1),
        validate=valid_c,
        error=f"нужно 2 <= C_B <= {p - 2} и НОД(C_B, p-1) = 1",
    )
    keys = make_keys(p, c1, c2)
    if keys is not None:
        print(f"D_A = {keys[3]}\nD_B = {keys[4]}")
    return keys


def block_bytes(p: int) -> int:
    return (p.bit_length() - 1) // 8


def coded_bytes(p: int) -> int:
    return ((p - 1).bit_length() + 7) // 8


def encrypt_file(src: str, dst: str, p: int, c1: int, c2: int, d1: int) -> None:
    k, w = block_bytes(p), coded_bytes(p)
    data = open(src, "rb").read()
    with open(dst, "wb") as f:
        f.write(len(data).to_bytes(8, "big"))
        for i in range(0, len(data), k):
            m = int.from_bytes(data[i:i + k], "big")
            m = fast_pow_mod(m, c1, p) # A - замок
            m = fast_pow_mod(m, c2, p) # B - замок
            m = fast_pow_mod(m, d1, p) # A - снятие замка
            f.write(m.to_bytes(w, "big"))
    print(f"Зашифровано: {src} -> {dst} ({len(data)} байт)")


def decrypt_file(src: str, dst: str, p: int, d2: int) -> None:
    k, w = block_bytes(p), coded_bytes(p)
    raw = open(src, "rb").read()
    size = int.from_bytes(raw[:8], "big")
    body = raw[8:]
    out = bytearray()
    left = size
    for i in range(0, len(body), w):
        m = int.from_bytes(body[i:i + w], "big")
        m = fast_pow_mod(m, d2, p) # B - снятие замка
        take = min(k, left)
        out += m.to_bytes(k, "big")[-take:]
        left -= take
    open(dst, "wb").write(bytes(out))
    print(f"Расшифровано: {src} -> {dst} ({size} байт)")


def menu() -> int:
    print("1. Задать ключи")
    print(f"2. Зашифровать файл   ({SOURCE} -> {ENCRYPTED})")
    print(f"3. Расшифровать файл  ({ENCRYPTED} -> {DECRYPTED})")
    return read_int("> ")


def main() -> None:
    keys = None
    while True:
        cmd = menu()
        match cmd:
            case 1:
                keys = get_keys()
            case 2:
                if keys is None:
                    print("Ключи не заданы")
                    continue
                p, c1, c2, d1, d2 = keys
                encrypt_file(SOURCE, ENCRYPTED, p, c1, c2, d1)
            case 3:
                if keys is None:
                    print("Ключи не заданы")
                    continue
                p, c1, c2, d1, d2 = keys
                decrypt_file(ENCRYPTED, DECRYPTED, p, d2)
            case _:
                break


if __name__ == "__main__":
    main()
