.. _scipy-backend-options:

************************
SciPy and dense keywords
************************

:doc:`Back to the backend overview <../backend>`

About these backends
====================

The ``scipy`` backend builds operators as SciPy
`CSR matrices <https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.csr_matrix.html>`__.
The solver stages also accept a NumPy array, a SciPy sparse matrix, or a
matrix-free
`LinearOperator <https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.LinearOperator.html>`__.
Exact diagonalization uses SciPy's
`LOBPCG eigensolver <https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.lobpcg.html>`__;
XAS and RIXS use EDRIXS's Lanczos routines, and the RIXS correction-vector
step uses SciPy's
`GMRES solver <https://docs.scipy.org/doc/scipy/reference/generated/scipy.sparse.linalg.gmres.html>`__.

The ``dense`` backend converts constructed operators to NumPy
`ndarray objects <https://numpy.org/doc/stable/reference/arrays.ndarray.html>`__
but otherwise uses the same solver adapters and keyword options as ``scipy``.
Because it stores every matrix element, it is most useful for small problems;
the sparse or matrix-free forms avoid that dense storage cost.

Options are specific to the stage where they are supplied.

``build_op`` and ``get_ops``
============================

.. backend-options:: scipy get_ops

Here ``tol`` controls operator truncation.  It is separate from the
eigensolver tolerance accepted by ``ed``.

``ed``
======

.. backend-options:: scipy ed

``xas``
=======

.. backend-options:: scipy xas

``rixs``
========

.. backend-options:: scipy rixs
