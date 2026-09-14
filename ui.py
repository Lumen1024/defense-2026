def read_int(prompt: str) -> int:
    while True:
        try:
            return int(input(prompt))
        except ValueError:
            print("Ошибка: введите целое число.")


def read_choice(prompt: str, valid: tuple[str, ...]) -> str:
    while True:
        v = input(prompt).strip()
        if v in valid:
            return v
        print("Ошибка: введите " + ", ".join(f"'{x}'" for x in valid) + ".")


def read_mode() -> bool:
    """True — «генерировать», False — «ввод с клавиатуры»."""
    return read_choice("Ввод с клавиатуры (1) или генерация (2)? [1/2]: ", ("1", "2")) == "2"
