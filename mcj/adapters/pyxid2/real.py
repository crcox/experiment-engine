import os
import sys

from pathlib import Path

def _setup_dll_path():
    base = Path(__file__).resolve().parents[2]
    arch = "x64" if sys.maxsize > 2**32 else "i386"
    dll_dir = base / "external" / "ftd2xx" / arch
    os.add_dll_directory(str(dll_dir.resolve()))

_setup_dll_path()

try:
    import ftd2xx
except Exception as e:
    raise RuntimeError(
        "FTD2XX library not found. Ensure DLLs are present in external/ftd2xx.\n" +
        "  They can be found in the ReLearn Lab shared OneDrive."
    ) from e
