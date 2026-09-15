from collections.abc import Callable


def read_int(
    prompt: str,
    can_skip: bool = False,
    fallback: int | Callable[[], int] | None = None,
) -> int | None:
    """Читает целое число с клавиатуры.

    При ``can_skip=True`` и пустом вводе возвращает ``fallback``. Если ``fallback`` —
    функция, она вызывается только в момент пропуска ввода (ленивая генерация).
    """
    hint = "[Enter — сгенерировать] " if can_skip and fallback is not None else ""
    while True:
        try:
            user_input = input(f"{prompt}{hint}").strip()
        except EOFError:
            print("\nВвод завершён.")
            raise SystemExit(0) from None
        if user_input == "" and can_skip:
            return fallback() if callable(fallback) else fallback
        try:
            return int(user_input)
        except ValueError:
            print("Ошибка: введите целое число.")


def read_choice(prompt: str, valid: tuple[str, ...]) -> str:
    while True:
        try:
            v = input(prompt).strip()
        except EOFError:
            print("\nВвод завершён.")
            raise SystemExit(0) from None
        if v in valid:
            return v
        print("Ошибка: введите " + ", ".join(f"'{x}'" for x in valid) + ".")


def read_mode() -> bool:
    """True — «генерировать», False — «ввод с клавиатуры»."""
    return read_choice("Ввод с клавиатуры (1) или генерация (2)? [1/2]: ", ("1", "2")) == "2"
