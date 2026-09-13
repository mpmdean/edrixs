# EDRIXS container image

EDRIXS is an open source toolkit for simulating resonant inelastic X-ray
scattering spectra based on exact diagonalization.

The `edrixs/edrixs` image contains EDRIXS, OpenMPI, the Python scientific
stack, JupyterLab, and the bundled examples. It is based on Ubuntu 24.04 and is
published for Linux AMD64 and ARM64.

## Tags

- `latest` is the most recent stable GitHub release.
- `vX.Y.Z` identifies one release and is the recommended form for reproducible
  work, for example `edrixs/edrixs:v0.1.3`.
- Pre-release images receive their version tag but do not update `latest`.

The old `edrixs/edrixs_base` and `edrixs/edrixs_interactive` repositories are
deprecated. Their functionality is incorporated into `edrixs/edrixs`.

## Quick start

Start an interactive Python session:

```console
docker run --rm -it edrixs/edrixs:latest ipython
```

Run a two-rank MPI calculation:

```console
docker run --rm edrixs/edrixs:latest \
  mpirun -np 2 python -c \
  "from mpi4py import MPI; from edrixs import fedrixs; print(MPI.COMM_WORLD.rank)"
```

Start JupyterLab in the current directory:

```console
docker run --rm -it -p 8888:8888 \
  -v "$PWD:/home/rixs" -w /home/rixs \
  edrixs/edrixs:latest \
  jupyter lab --ip=0.0.0.0 --port=8888 --no-browser
```

## Project links

- [Source code](https://github.com/EDRIXS/edrixs)
- [Documentation](https://edrixs.github.io/edrixs/)
- [Releases](https://github.com/EDRIXS/edrixs/releases)
- [Issue tracker](https://github.com/EDRIXS/edrixs/issues)

The image is published from the corresponding GitHub release by GitHub
Actions. Images produced by the current release workflow include build
provenance and a software bill of materials.
