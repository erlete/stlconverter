"""Input handling module.

This module contains the InputHandler class, which is responsible for handling
CLI arguments.

Author:
    Paulo Sanchez (@erlete)
"""


import os
from typing import List

from colorama import Fore, Style


class InputHandler:
    """Input handler for CLI arguments.

    Attributes:
        arguments (List[str]): CLI arguments.
    """

    def __init__(self, arguments: List[str]) -> None:
        """Initialize an InputHandler instance.

        Args:
            arguments (List[str]): CLI arguments.
        """
        self.arguments = arguments

    @property
    def arguments(self) -> List[str]:
        """Get CLI arguments.

        Returns:
            List[str]: CLI arguments.
        """
        return self._arguments

    @arguments.setter
    def arguments(self, arguments: List[str]) -> None:
        """Set CLI arguments.

        Args:
            arguments (List[str]): CLI arguments.
        """
        # General info and argument count checking:
        if len(arguments) != 2:
            print(f"""{Style.BRIGHT}{Fore.GREEN}\
Usage:
  {Fore.YELLOW}python -m stlconverter <input file path> <output mode>

{Style.BRIGHT}{Fore.GREEN}Output modes:
  {Style.BRIGHT}{Fore.YELLOW}STLB{Style.RESET_ALL}: to binary STL file.
  {Style.BRIGHT}{Fore.YELLOW}STLA{Style.RESET_ALL}: to ASCII STL file.""")
            exit(1)

        # Input file existence checking:
        if not os.path.isfile(arguments[0]):
            print(
                Style.BRIGHT + Fore.RED +
                f"[Error] input file \"{arguments[0]}\" does not exist"
                + Style.RESET_ALL
            )
            exit(1)

        # Input file extension checking:
        if not arguments[0].lower().endswith(".stl"):
            print(
                Style.BRIGHT + Fore.RED +
                f"[Error] input file \"{arguments[0]}\" is not a .stl file"
                + Style.RESET_ALL
            )
            exit(1)

        # Output mode checking:
        if not arguments[1].upper() in ("STLB", "STLA"):
            print(
                Style.BRIGHT + Fore.RED +
                "[Error] output mode must be \"SLTB\" (binary) or \"STLA\""
                + " (ASCII)" + Style.RESET_ALL
            )
            exit(1)

        self._arguments = arguments

    @property
    def input_path(self) -> str:
        """Get input file path.

        Returns:
            str: input file path.
        """
        return self.arguments[0]

    @property
    def is_binary(self) -> bool:
        """Check if output mode is binary.

        Returns:
            bool: True if output mode is binary, False otherwise.
        """
        return self.arguments[1].upper() == "STLB"

    @property
    def is_ascii(self) -> bool:
        """Check if output mode is ASCII.

        Returns:
            bool: True if output mode is ASCII, False otherwise.
        """
        return self.arguments[1].upper() == "STLA"
