models
======

All four model constructors include explicit core orbitals in both initial
and intermediate integrals. The initial basis appends a fully occupied core
sector; occupancy arguments count valence electrons only. Initial core-valence
and core-core interactions are active. No implicit-core compatibility mode is
provided.

The Fortran backend contracts the filled core immediately before writing its
valence-only initial files, preserving the full many-body energies. It cannot
represent a zero-valence sector with nonzero core energy. Intermediate integrals
and transition matrices remain in full orbital space. Legacy Fortran density
matrices still contain valence orbitals only.

.. automodule:: edrixs.models
   :members:
