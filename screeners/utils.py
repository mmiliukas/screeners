import time


def a_string(x: str):
    return x


def a_percent(x: str):
    try:
        return round(float(x.replace("%", "")), 4)
    except Exception:
        return round(0, 4)


def a_number(x: str):
    multipliers = {
        "k": 10**3,
        "K": 10**3,
        "m": 10**6,
        "M": 10**6,
        "b": 10**9,
        "B": 10**9,
    }

    try:
        if x[-1] in multipliers:
            return round(float(x[:-1]) * multipliers[x[-1]], 4)
        else:
            return float(x)
    except Exception:
        return round(0, 4)


def an_integer(x: str):
    try:
        return int(a_number(x))
    except Exception:
        return 0


def retry(times: int):
    def try_fn(fn):
        for _ in range(times + 1):
            try:
                return fn()
            except Exception as e:
                if _ < times:
                    continue
                else:
                    raise e

    return try_fn


def unique_file_name(extension: str = ".csv"):
    name = time.strftime("%Y_%m_%d_%H_%M_%S")
    return f"{name}{extension}"


def progress(prefix: str, current: int, total: int) -> None:
    percentage = current / total
    line = "\r[{1:20s}] {2:4}/{3} ({4:3}%) {0}".format(
        prefix, "■" * int(percentage * 20), current, total, int(percentage * 100)
    )
    print(line, end="", flush=True)
    if current == total:
        print("", flush=True)
