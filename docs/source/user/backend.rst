.. _backend:

*******
Backend
*******

The :ref:`introduction` describes the four stages of a calculation.  Stages two
to four -- building operators, diagonalizing, and assembling spectra --
delegate their numerical work to a backend selected with ``backend``:

* ``'dense'`` returns full NumPy matrices.  It uses the SciPy solvers and is
  intended for small problems and pedagogy.
* ``'scipy'`` returns SciPy sparse matrices and uses LOBPCG, Lanczos, and GMRES.
  It is the default backend.
* ``'fortran'`` uses the native MPI solvers and communicates through files in
  the current working directory.  We provide the function
  :func:`edrixs.get_ops_disk <edrixs.solvers.get_ops_disk>` to load the setup
  from disk if desired.
* ``'petsc'`` uses distributed PETSc matrices, SLEPc eigensolvers, and PETSc
  Krylov solvers.  It is intended for larger Hilbert spaces and MPI runs.

Backend-specific numerical controls belong in a ``backend_kws`` mapping.  The
mapping is specific to both the backend *and the operation*.

.. _backend-options:

Backend keyword reference
=========================

Choose the backend whose keywords you need:

* :doc:`SciPy and dense keywords <backends/scipy>`
* :doc:`Fortran keywords <backends/fortran>`
* :doc:`PETSc keywords <backends/petsc>`

These references apply to the staged ``get_ops`` / ``ed`` / ``xas`` / ``rixs``
interface.  The legacy ``ed_*_fort``, ``xas_*_fort``, and ``rixs_*_fort``
functions retain their existing explicit parameters.

.. toctree::
   :hidden:

   backends/scipy
   backends/fortran
   backends/petsc
