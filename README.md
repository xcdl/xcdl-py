# Welcome to the XCDL.py Project!

This was the initial Python implementation of [XCDL](https://github.com/xcdl).

The implementation was experimental, as a proof of concept. The metadata files were in fact fragments of Python code, loaded at trun time.

This implementation was used to define and build the **µOS++ SE** components. Surprisingly, the performance was quite good, the pre-build step (required to parse all metadata and generate the make files) took just tens of milliseconds.

The project is currently obsolete, and development moved to a new version, with XML metadata files and compiled tools.
