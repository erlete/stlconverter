# [STL Converter](https://stlconverter.erlete.org)

This repository contains a multi-language STL data manipulation tool that can be used to convert STL binary files into ASCII ones and vice-versa.

## Python

The tool has been developed in Python>=3.9 for direct command line usage. Installation can be performed via `pip` and used through a really simple syntax.

_Note: these instructions assume that your Python interpreter is alised as `python`. If you have configured it otherwise, please use the proper alias._

### Installation

```txt
python -m pip install stlconverter
```

### Usage

The command for invoking the STL converter tool is as follows:

```txt
python -m stlconverter <input file path> <output mode>
```

The arguments for the command are the following:

- **Input file path**: the path to the STL file to be converted
- **Output mode**: the identifier of the output mode for the conversion process (case insensitive)
  - **STLB**: conversion to binary STL file
  - **STLA**: conversion to ASCII STL file

## JavaScript

The tool has also been developed in JavaScript (ES10) for web interface usage (or modular import).

### Web

The web interface version is available [here](https://stlconverter.erlete.org).

### Modular

Although the tool has not been explicitely developed for modular usage, it can be used like that. Just load the [conversion](https://github.com/erlete/stl-converter/blob/stable/js/src/modules/conversion.js) module into your site and access the functions that perform the conversion process.

## Note regarding STL numerical format

This conversion tool does not use [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754)-compliant numerical formats. Instead, it uses 32-bit floating point values. This greatly reduces the size of the ASCII variant of the STL format, but it might cause computational irregularities in some specific or complex conversion scenarios.
