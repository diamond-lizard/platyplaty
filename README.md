# Platyplaty

A C++ wrapper for libprojectM controlled from Python.

## Dependencies

- libprojectM 4.x (`projectM-devel` on Fedora/RHEL)
- SDL2 (`SDL2-devel` on Fedora/RHEL)
- C++17 capable compiler (GCC 7+ or Clang 5+)
- pkg-config

## Building

```bash
make
```

The renderer binary is built to `build/platyplaty-renderer`.

### Non-standard libprojectM location

If libprojectM is installed in a non-standard location, set `PKG_CONFIG_PATH` before building:

```bash
export PKG_CONFIG_PATH=/path/to/libprojectm/lib64/pkgconfig:$PKG_CONFIG_PATH
make
```

## Running

Run from the project root directory:

```bash
./build/platyplaty-renderer
```

## Cleaning

```bash
make clean
```
