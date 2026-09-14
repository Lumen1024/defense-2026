import random

from gen import MAGNITUDE, generate_discrete_log_challenge, generate_pair, generate_prime, generate_prime_pair
from lib import discrete_log, extended_euclid, fast_pow_mod, is_prime_fermat
from ui import read_choice, read_int, read_mode


def menu() -> int:
    print("\n\n")
    print("1. Быстрое возведение в степень по модулю")
    print("2. Тест простоты Ферма")
    print("3. Обобщённый алгоритм Евклида")
    print("4. Нахождение дискретного логарифма (Шаг младенца, шаг великана)")
    print("0. Выход\n\n")
    return read_int("> ")


def _demo_fast_pow() -> None:
    print("> y = a^x mod p")
    if read_mode():
        a, p = generate_pair()
        x = random.randint(2, MAGNITUDE)
        print(f"a = {a}\nx = {x}\np = {p}")
    else:
        a = read_int("a = ")
        x = read_int("x = ")
        p = read_int("p = ")
    y = fast_pow_mod(a, x, p)
    print(f"y = {a}^{x} % {p} = {y}")
    input()


def _demo_ferma() -> None:
    n = generate_prime() if read_mode() else read_int("n = ")
    print(f"> Число {n} вероятно простое: {is_prime_fermat(n)}")
    input()


def _demo_gcd() -> None:
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
    if read_mode():
        a, y, p, _ = generate_discrete_log_challenge()
        print(f"Сгенерировано:\na = {a}\ny = {y}\np = {p}")
    else:
        a = read_int("a = ")
        y = read_int("y = ")
        p = read_int("p = ")
    try:
        x = discrete_log(a, y, p)
    except ValueError as exc:
        print(f"Ошибка: {exc}")
        return
    if x is None:
        print("Дискретный логарифм не найден в заданном диапазоне.")
    else:
        print(f"x = {x}")
        print(f"Проверка: {a}^{x} % {p} = {fast_pow_mod(a, x, p)} (y = {y})")
    input()


if __name__ == "__main__":
    while True:
        choice = menu()
        if choice == 1:
            _demo_fast_pow()
        elif choice == 2:
            _demo_ferma()
        elif choice == 3:
            _demo_gcd()
        elif choice == 4:
            _demo_discrete_log()
        elif choice == 0:
            break
        else:
            print("Неверный пункт меню.")
