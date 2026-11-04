#!/usr/bin/python3
import os
import sys

DATA_FILES = ["/lab-data/ogolny.txt", "/lab-data/poufny.txt"]

lines = [f"EUID: {os.geteuid()}", f"EGID: {os.getegid()}"]
for path in DATA_FILES:
    try:
        with open(path, encoding="utf-8") as data_file:
            lines.append(f"{path}: {data_file.read().strip()}")
    except OSError as error:
        lines.append(f"{path}: odmowa odczytu ({error.strerror})")

response = "Content-Type: text/plain; charset=utf-8\n\n" + "\n".join(lines) + "\n"
sys.stdout.buffer.write(response.encode("utf-8"))
