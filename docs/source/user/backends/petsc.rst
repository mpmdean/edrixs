.. _petsc-backend-options:

**************
PETSc keywords
**************

:doc:`Back to the backend overview <../backend>`

About this backend
==================

PETSc supplies distributed vectors and matrices together with scalable linear
solvers and preconditioners; its concise
`architecture overview <https://petsc.org/release/overview/nutshell/>`__
introduces the ``Vec``, ``Mat``, ``KSP``, and ``PC`` objects.  Python programs
access them through the official
`petsc4py API <https://petsc.org/release/petsc4py/reference/petsc4py.PETSc.html>`__.
For eigenvalue problems, SLEPc builds on PETSc and exposes its ``EPS`` solver
through the
`SLEPc eigenvalue guide <https://slepc.upv.es/release/documentation/manual/eps.html>`__
and the
`slepc4py EPS API <https://slepc.upv.es/release/slepc4py/reference/slepc4py.SLEPc.EPS.html>`__.

EDRIXS constructs distributed PETSc ``Mat`` objects, obtains low-energy
eigenpairs with SLEPc's Krylov--Schur method, and evaluates XAS and RIXS with
distributed Lanczos and KSP solves.  Importing EDRIXS does not import PETSc;
``petsc4py`` and ``slepc4py`` are loaded only when this backend is used.

Options are specific to the stage where they are supplied.

``build_op`` and ``get_ops``
============================

.. backend-options:: petsc get_ops

``nnz_guess_per_row`` controls PETSc matrix preallocation.  Leaving it unset
uses an estimate from the retained one- and two-body coefficients.  A
``mat_type`` such as ``'aijcusparse'`` can select an accelerated matrix format;
see PETSc's `matrix type overview
<https://petsc.org/release/manual/mat/#basic-matrix-operations>`__.

``ed``
======

.. backend-options:: petsc ed

The eigensolver uses SLEPc ``EPS`` with a Hermitian problem type and requests
the smallest-real eigenpairs.  ``ncv`` sets the Krylov subspace size described
by `EPS.setDimensions
<https://slepc.upv.es/release/slepc4py/reference/slepc4py.SLEPc.EPS.html#slepc4py.SLEPc.EPS.setDimensions>`__.

``xas``
=======

.. backend-options:: petsc xas

``rixs``
========

.. backend-options:: petsc rixs

``ksp_type`` accepts a PETSc KSP type such as ``'gmres'``; the available
algorithms and their tradeoffs are listed in the `KSP solver table
<https://petsc.org/release/manual/ksp/#tab-kspdefaults>`__.
