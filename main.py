import random

from gen import (
    MAGNITUDE,
    generate_pair,
    generate_prime,
    generate_prime_pair,
    generate_primitive_root,
)
from lib import (
    diffie_hellman,
    diffie_hellman_get_shared_secret,
    discrete_log,
    extended_euclid,
    fast_pow_mod,
    is_prime_fermat,
)
from ui import clear_screen, read_choice, read_int


def menu() -> int:
    clear_screen()
    print("1. Быстрое возведение в степень по модулю")
    print("2. Тест простоты Ферма")
    print("3. Обобщённый алгоритм Евклида")
    print("4. Нахождение дискретного логарифма (Шаг младенца, шаг великана)")
    print("5. Построение общего ключа по схеме Диффи-Хеллмана")
    print("0. Выход\n\n")
    return read_int("> ")


def _demo_fast_pow() -> None:
    print("> y = a^x mod p")
    a = read_int(
        "a = ",
        True,
        lambda: random.randint(2, MAGNITUDE),
        validate=lambda v: v >= 0,
        error="a должно быть неотрицательным",
    )
    x = read_int(
        "x = ",
        True,
        lambda: random.randint(2, MAGNITUDE),
        validate=lambda v: v >= 0,
        error="x должно быть неотрицательным",
    )
    p = read_int(
        "p = ",
        True,
        lambda: generate_prime(rounds=20),
        validate=lambda v: v > 1,
        error="p должно быть больше 1",
    )
    y = fast_pow_mod(a, x, p)
    print(f"y = {a}^{x} mod {p} = {y}")
    input()


def _demo_ferma() -> None:
    n = read_int(
        "n = ",
        True,
        generate_prime,
        validate=lambda v: v >= 1,
        error="n должно быть натуральным числом",
    )
    print(f"> Число {n} вероятно простое: {is_prime_fermat(n)}")
    input()


def _demo_gcd() -> None:
    print("Обобщённый алгоритм Евклида: a*x + b*y = НОД(a, b)")
    print("1. Ввод a, b с клавиатуры")
    print("2. Генерация a, b внутри функции")
    print("3. Генерация a, b простыми (тест Ферма)")
    mode = read_choice("Выберите режим [1/2/3]: ", ("1", "2", "3"))
    if mode == "3":
        a, b = generate_prime_pair()
        print(f"a = {a},\nb = {b}")
    elif mode == "2":
        a, b = generate_pair()
        print(f"a = {a}\nb = {b}")
    else:
        a = read_int("a = ")
        b = read_int("b = ")
    g, x, y = extended_euclid(a, b)
    print(f"НОД({a}, {b}) = {g}")
    print(f"x = {x}, y = {y}")
    print(f"Проверка: {a}*({x}) + {b}*({y}) = {a * x + b * y}")
    input()


def _demo_discrete_log() -> None:
    print("> y = a^x mod p — нахождение дискретного логарифма")
    p = read_int(
        "p = ",
        True,
        lambda: generate_prime(low=3, rounds=20),
        validate=lambda v: v >= 3 and is_prime_fermat(v),
        error="p должно быть простым числом, p >= 3",
    )
    a = read_int(
        "a = ",
        True,
        lambda: random.randint(2, p - 1),
        validate=lambda v: 1 < v < p,
        error=f"нужно 1 < a < {p}",
    )
    y = read_int(
        "y = ",
        True,
        lambda: fast_pow_mod(a, random.randint(1, p - 1), p),
        validate=lambda v: 1 <= v < p,
        error=f"нужно 1 <= y < {p}",
    )
    try:
        x = discrete_log(a, y, p)
    except ValueError as exc:
        print(f"Ошибка: {exc}")
        input()
        return
    if x is None:
        print("Дискретный логарифм не найден в заданном диапазоне.")
    else:
        check = fast_pow_mod(a, x, p)
        print(f"x = {x}")
        print(f"Проверка: {a}^{x} mod {p} = {check} (y = {y})")
        print("Решение верно." if check == y else "Решение НЕВЕРНО.")
    input()


def _demo_diffie_hellman() -> None:
    print("Схема Диффи-Хеллмана: K = g^(x_a*x_b) mod p")

    print("Публичные параметры шифрования:")
    p = read_int(
        "p = ",
        True,
        lambda: generate_prime(low=5, rounds=20),
        validate=lambda v: v >= 5 and is_prime_fermat(v),
        error="p должно быть простым числом, p >= 5",
    )
    g = read_int(
        "g = ",
        True,
        lambda: generate_primitive_root(p),
        validate=lambda v: 1 < v < p,
        error=f"нужно 1 < g < {p}",
    )

    print("Личные секретные ключи абонентов:")

    def valid_x(value: int) -> bool:
        return 1 <= value <= p - 2

    x_a = read_int(
        "x_a = ",
        True,
        lambda: random.randint(2, p - 2),
        validate=valid_x,
        error=f"нужно 1 <= x_a <= {p - 2}",
    )
    x_b = read_int(
        "x_b = ",
        True,
        lambda: random.randint(2, p - 2),
        validate=valid_x,
        error=f"нужно 1 <= x_b <= {p - 2}",
    )

    try:
        y_a, y_b, k_a = diffie_hellman(p, g, x_a, x_b)
    except (ValueError, ArithmeticError) as exc:
        print(f"Ошибка: {exc}")
        input()
        return

    k_b = diffie_hellman_get_shared_secret(p, x_b, y_a)
    print("Публичные ключи абонентов:")
    print(f"> y_a = {y_a}\n> y_b = {y_b}")
    print("Вычисление общего секретного ключа:")
    print(f"> K_a = {k_a}\n> K_b = {k_b}")
    if k_a == k_b:
        print("Ключи абонентов совпадают.")
    else:
        print("Ключи абонентов НЕ совпадают.")
    input()


if __name__ == "__main__":
    while True:
        match menu():
            case 1:
                _demo_fast_pow()
            case 2:
                _demo_ferma()
            case 3:
                _demo_gcd()
            case 4:
                _demo_discrete_log()
            case 5:
                _demo_diffie_hellman()
            case 0:
                break
            case _:
                print("Неверный пункт меню.")
                input()
