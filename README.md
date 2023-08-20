# [STL Converter](https://stlconverter.erlete.org)

This repository contains a multi-language STL data manipulation tool that can be used to convert STL binary files into ASCII ones and vice-versa.

## Python

Check the dedicated [Python package README](./python/README.md) for more information on how to install and use the tool through Pyton.

## JavaScript

The tool has also been developed in JavaScript (ES10) for web interface usage (or modular import).

### Web

The web interface version is available [here](https://stlconverter.erlete.org).

### Modular

Although the tool has not been explicitely developed for modular usage, it can be used like that. Just load the [conversion](https://github.com/erlete/stl-converter/blob/stable/js/src/modules/conversion.js) module into your site and access the functions that perform the conversion process.

## Note regarding STL numerical format

This conversion tool does not use [IEEE 754](https://en.wikipedia.org/wiki/IEEE_754)-compliant numerical formats. Instead, it uses 32-bit floating point values. This greatly reduces the size of the ASCII variant of the STL format, but it might cause computational irregularities in some specific or complex conversion scenarios.
