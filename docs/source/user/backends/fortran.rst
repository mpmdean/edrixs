.. _fortran-backend-options:

****************
Fortran keywords
****************

:doc:`Back to the backend overview <../backend>`

All staged Fortran operations are collective on ``comm``.  When it is omitted,
``mpi4py.MPI.COMM_WORLD`` is used.

These options belong only to the staged interface.  The legacy ``*_fort``
functions retain their existing explicit parameters and behavior.

``get_ops``
===========

The Fortran backend constructs the complete problem at once, so
``build_op(..., backend='fortran')`` is not supported.

.. backend-options:: fortran get_ops

``ed``
======

.. backend-options:: fortran ed

For later XAS or RIXS calculations, ``idump`` must remain true and ``nvector``
must be at least the later ``num_gs`` value.  ``nvector`` cannot exceed
``num_evals``.

``xas``
=======

.. backend-options:: fortran xas

``rixs``
========

.. backend-options:: fortran rixs

The staged spelling ``linsys_maxiter`` is translated internally to the native
Fortran namelist field ``linsys_max``.
