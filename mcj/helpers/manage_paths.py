import os
import sys

def add_ftd2xx_dll_path():
    base = os.path.dirname(os.path.abspath(__file__))

    dll_dir = os.path.join(
        base,
        "..",
        "..",
        "external",
        "ftd2xx",
        "x64" if sys.maxsize > 2**32 else "i386"
    )

    os.add_dll_directory(os.path.abspath(dll_dir))


add_ftd2xx_dll_path()
