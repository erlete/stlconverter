"""Main execution module.

This module is the entry point for the STLConverter application through the
command line interface.

Author:
    Paulo Sanchez (@erlete)
"""


import sys
from time import perf_counter as pc

from colorama import Fore, Style, init
from .modules.conversion import STL
from .modules.input_handling import InputHandler


def same_format_warn(input_handler: InputHandler, stl: STL) -> None:
    """Print a warning if input and output formats are the same.

    Args:
        input_handler (InputHandler): Input handler instance.
        stl (STL): STL instance.
    """
    if input_handler.is_binary and stl._is_input_binary:
        print(
            Style.BRIGHT + Fore.YELLOW
            + "Warning: detected same input and output format (binary)."
            " File contents will remain unchanged after conversion"
            + Style.RESET_ALL
        )
    elif input_handler.is_ascii and stl._is_input_ascii:
        print(
            Style.BRIGHT + Fore.YELLOW
            + "Warning: detected same input and output format (ASCII)."
            " File contents will remain unchanged after conversion"
            + Style.RESET_ALL
        )


init()  # Initialize colorama.
handler = InputHandler(sys.argv[1:])
out_name = (
    f"{handler.input_path[:handler.input_path.rfind('.')]}-converted"
    + f"-{pc()}.stl"
)

try:
    stl = STL(handler.input_path)
    if handler.is_binary:
        same_format_warn(handler, stl)
        stl.save_stlb(out_name)
    else:
        same_format_warn(handler, stl)
        stl.save_stla(out_name)
except Exception:  # Uncaught exceptions.
    print(
        Style.BRIGHT + Fore.RED
        + f"Unknown error: {Style.RESET_ALL}{str(sys.exc_info()[1])}"
    )
else:  # Successful conversion.
    mode = "binary" if handler.is_binary else "ASCII"
    print(
        Style.BRIGHT + Fore.GREEN
        + f"File successfully converted to {mode} format"
    )
