import os

from colorama import Fore, Style


class InputHandler:

    def __init__(self, arguments):
        self.arguments = arguments

    @property
    def arguments(self):
        return self._arguments

    @arguments.setter
    def arguments(self, arguments):
        if len(arguments) != 2:
            print(f"""{Style.BRIGHT}{Fore.GREEN}\
Usage:
    {Fore.YELLOW}python -m stlconverter <input file path> <output mode>

{Style.BRIGHT}{Fore.GREEN}Output modes:
  {Style.BRIGHT}{Fore.YELLOW}STLB{Style.RESET_ALL}: to binary STL file.
  {Style.BRIGHT}{Fore.YELLOW}STLA{Style.RESET_ALL}: to ASCII STL file.""")
            exit(1)

        if not os.path.isfile(arguments[0]):
            print(
                Style.BRIGHT + Fore.RED +
                f"Error: input file \"{arguments[0]}\" does not exist"
                + Style.RESET_ALL
            )
            exit(1)

        if not arguments[1].upper() in ("STLB", "STLA"):
            print(
                Style.BRIGHT + Fore.RED +
                "Error: output mode must be \"SLTB\" (binary) or \"STLA\""
                + " (ASCII)" + Style.RESET_ALL
            )
            exit(1)

        self._arguments = arguments

    @property
    def input_path(self):
        return self.arguments[0]

    @property
    def is_binary(self):
        return self.arguments[1] == "STLB"

    @property
    def is_ascii(self):
        return self.arguments[1] == "STLA"
