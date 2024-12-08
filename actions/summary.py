import math
import os

import pandas as pd

from screeners.config import config


def convert_size(size_bytes) -> str:
    if size_bytes == 0:
        return "0 B"
    size_name = ("B", "KB", "MB", "GB", "TB")
    i = int(math.floor(math.log(size_bytes, 1024)))
    p = math.pow(1024, i)
    s = size_bytes / p
    return f"{s:.2f} {size_name[i]}"


def summarize_file(file: str) -> tuple[str, int, str, int]:
    size = os.path.getsize(file)
    return (file, size, convert_size(size), 1)


def summarize_dir(dir: str) -> tuple[str, int, str, int]:
    size = 0
    count = 0

    for dirpath, dirnames, filenames in os.walk(dir):
        for file in filenames:
            size += os.path.getsize(os.path.join(dirpath, file))
            count += 1

    return dir, size, convert_size(size), count


def summary() -> None:
    entries = os.listdir(".")

    files = [file for file in entries if os.path.isfile(file) and file.endswith(".csv")]
    dirs = [dir for dir in entries if os.path.isdir(dir) and not dir.startswith(".")]

    df_dirs = pd.DataFrame([summarize_dir(dir) for dir in dirs])
    df_files = pd.DataFrame([summarize_file(file) for file in files])

    df_dirs.sort_values(by=1, inplace=True, ascending=False)  # type: ignore
    df_files.sort_values(by=1, inplace=True, ascending=False)  # type: ignore

    df = pd.concat([df_dirs, df_files])

    with open(config.summary.target, "w") as file:
        file.write("```csv\n")
        file.write(df[[0, 2, 3]].to_string(index=False, header=False))
        file.write("\n```")
