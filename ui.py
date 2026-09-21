import os
import sys
from collections.abc import Callable

_ansi_ready = False


def _enable_ansi() -> None:
    """Включает обработку ANSI-последовательностей в консоли Windows.

    CPython сам этого не делает (bpo-29059), поэтому включаем
    ENABLE_VIRTUAL_TERMINAL_PROCESSING вручную один раз.
    """
    global _ansi_ready
    if _ansi_ready:
        return
    _ansi_ready = True
    if os.name != "nt":
        return
    try:
        import ctypes

        kernel32 = ctypes.windll.kernel32
        handle = kernel32.GetStdHandle(-11)  # STD_OUTPUT_HANDLE
        mode = ctypes.c_uint32()
        if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
            kernel32.SetConsoleMode(handle, mode.value | 0x0004)  # VT processing
    except Exception:  # noqa: BLE001 — включение ANSI не должно ронять программу
        pass


def _echo_generated(prompt: str, value: int) -> None:
    """Дописывает сгенерированное значение в уже начатую строку приглашения."""
    if sys.stdout.isatty():
        _enable_ansi()
        # курсор после Enter стоит в начале следующей строки —
        # поднимаемся на строку вверх и перезаписываем её целиком
        sys.stdout.write(f"\033[1A\r{prompt}{value}\n")
        sys.stdout.flush()
    else:
        # при перенаправлении вывода приглашение уже напечатано, эхо не работает
        print(value)


def clear_screen() -> None:
    """Очищает консоль (только когда вывод идёт в терминал)."""
    if not sys.stdout.isatty():
        return
    _enable_ansi()
    sys.stdout.write("\033[2J\033[H")  # очистить экран и вернуть курсор в начало
    sys.stdout.flush()


def read_int(
    prompt: str,
    can_skip: bool = False,
    fallback: int | Callable[[], int] | None = None,
    validate: Callable[[int], bool] | None = None,
    error: str = "недопустимое значение",
) -> int | None:
    """Читает целое число с клавиатуры.

    can_skip — пустой ввод возвращает ``fallback`` (значение или функцию без
    аргументов, тогда значение вычисляется в момент пропуска ввода).
    validate — предикат; если вернул False, печатается ``error`` и ввод повторяется.
    """
    while True:
        try:
            raw = input(prompt).strip()
        except EOFError:
            print("\nВвод завершён.")
            raise SystemExit(0) from None
        skipped = raw == "" and can_skip
        if skipped:
            value = fallback() if callable(fallback) else fallback
        else:
            try:
                value = int(raw)
            except ValueError:
                print("Ошибка: введите целое число.")
                continue
        if value is not None and validate is not None and not validate(value):
            print(f"Ошибка: {error}.")
            continue
        if skipped and value is not None:
            _echo_generated(prompt, value)
        return value


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
