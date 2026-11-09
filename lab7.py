import os
import random

from gen import generate_prime, generate_primitive_root
from lib import (
    diffie_hellman,
    diffie_hellman_get_shared_secret,
    is_prime_fermat,
)
from ui import read_int

MIN_P = 5
LOW = 10**6

SOURCE = "files/some.txt"
ENCRYPTED = "files/some.enc"
DECRYPTED = "files/some_dec.txt"


def read_path(prompt: str, default: str) -> str:
    """Читает путь к файлу; пустой ввод оставляет значение по умолчанию."""
    try:
        raw = input(f"{prompt} [{default}]: ").strip()
    except EOFError:
        print("\nВвод завершён.")
        raise SystemExit(0) from None
    return raw or default


def default_encrypted(src: str) -> str:
    """Заменяет расширение исходного файла на .enc."""
    return os.path.splitext(src)[0] + ".enc"


def default_decrypted(src: str) -> str:
    """Заменяет расширение шифрфайла на _dec.txt."""
    return os.path.splitext(src)[0] + "_dec.txt"


def get_keys() -> int | None:
    """Строит общий ключ K по схеме Диффи-Хеллмана."""
    p = read_int(
        "p = ",
        True,
        lambda: generate_prime(low=max(LOW, MIN_P)),
        validate=lambda v: v >= MIN_P and is_prime_fermat(v),
        error=f"p должно быть простым и >= {MIN_P}",
    )

    g = read_int(
        "g = ",
        True,
        lambda: generate_primitive_root(p),
        validate=lambda v: 1 < v < p,
        error=f"нужно 1 < g < {p}",
    )

    def valid_x(value: int) -> bool:
        return 1 <= value <= p - 2

    x_a = read_int(
        "X_a = ",
        True,
        lambda: random.randint(2, p - 2),
        validate=valid_x,
        error=f"нужно 1 <= X_a <= {p - 2}",
    )
    x_b = read_int(
        "X_b = ",
        True,
        lambda: random.randint(2, p - 2),
        validate=valid_x,
        error=f"нужно 1 <= X_b <= {p - 2}",
    )

    y_a, y_b, k_a = diffie_hellman(p, g, x_a, x_b)
    k_b = diffie_hellman_get_shared_secret(p, x_b, y_a)

    print("Публичные ключи абонентов:")
    print(f"> Y_a = g^X_a mod p = {y_a}")
    print(f"> Y_b = g^X_b mod p = {y_b}")
    print("Общий секретный ключ:")
    print(f"> K (A) = Y_b^X_a mod p = {k_a}")
    print(f"> K (B) = Y_a^X_b mod p = {k_b}")

    if k_a != k_b:
        print("Ошибка: ключи абонентов не совпали.")
        return None

    print(f"Ключ K = {k_a} будет использован как seed генератора гаммы.")
    return k_a


def vernam(src: str, dst: str, key: int, action: str) -> None:
    """Шифр Вернама: C = M XOR gamma(K), M = C XOR gamma(K)."""
    try:
        data = open(src, "rb").read()
    except OSError as exc:
        print(f"Ошибка: не удалось прочитать {src}: {exc}")
        return

    gamma = random.Random(key).randbytes(len(data))
    out = bytes(byte ^ g for byte, g in zip(data, gamma))

    try:
        with open(dst, "wb") as f:
            f.write(out)
    except OSError as exc:
        print(f"Ошибка: не удалось записать {dst}: {exc}")
        return

    print(f"{action}: {src} -> {dst} ({len(data)} байт)")


def encrypt_file(key: int) -> None:
    src = read_path("Исходный файл", SOURCE)
    dst = read_path("Куда сохранить шифр", default_encrypted(src))
    vernam(src, dst, key, "Зашифровано")


def decrypt_file(key: int) -> None:
    src = read_path("Зашифрованный файл", ENCRYPTED)
    dst = read_path("Куда сохранить расшифровку", default_decrypted(src))
    vernam(src, dst, key, "Расшифровано")


def menu() -> int:
    print("1. Задать ключ (Диффи-Хеллман)")
    print("2. Зашифровать файл")
    print("3. Расшифровать файл")
    print("0. Выход")
    return read_int("> ")


def main() -> None:
    key = None
    while True:
        cmd = menu()
        match cmd:
            case 1:
                key = get_keys()
            case 2:
                if key is None:
                    print("Ключ не задан")
                    continue
                encrypt_file(key)
            case 3:
                if key is None:
                    print("Ключ не задан")
                    continue
                decrypt_file(key)
            case _:
                break


if __name__ == "__main__":
    main()
